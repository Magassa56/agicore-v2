"""Deterministic, non-vacuous tests for the Gate 6.2B contract."""
from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, replace
from datetime import datetime, timedelta, timezone

import pytest

from agicore.risk.exposure_models import ExecutionIntent, IntentSide, RiskLimits
from agicore.risk.risk_execution_authorization import (
    AUTHORIZATION_SCHEMA_VERSION,
    CONSUMPTION_SCHEMA_VERSION,
    RiskAuthorizationBoundary,
    RiskAuthorizationConsumption,
    RiskAuthorizationDecision,
    RiskAuthorizationError,
)
from agicore.risk.risk_execution_context import InMemoryRiskContextProvider, RiskContextError, RiskExecutionContext
from agicore.risk.exposure_models import empty_snapshot
from agicore.risk.risk_manager import RiskManager


class CountingRiskManager(RiskManager):
    def __init__(self, limits: RiskLimits, *, error: Exception | None = None) -> None:
        super().__init__(limits)
        self.call_count = 0
        self.error = error

    def validate(self, intent, snapshot):
        self.call_count += 1
        if self.error is not None:
            raise self.error
        return super().validate(intent, snapshot)


class ScriptedContextProvider:
    def __init__(
        self,
        context: RiskExecutionContext,
        *,
        assert_error: BaseException | None = None,
        snapshot_error: BaseException | None = None,
    ) -> None:
        self.current = context
        self.assert_error = assert_error
        self.snapshot_error = snapshot_error

    def snapshot(self) -> RiskExecutionContext:
        if self.snapshot_error is not None:
            raise self.snapshot_error
        return self.current

    def assert_current(self, expected_version: int, expected_hash: str) -> None:
        if self.assert_error is not None:
            raise self.assert_error
        if expected_version != self.current.state_version or expected_hash != self.current.state_hash:
            raise RiskContextError("STALE_RISK_CONTEXT", "scripted provider state differs")


class RaisingSnapshotProvider:
    def snapshot(self) -> RiskExecutionContext:
        raise RuntimeError("synthetic snapshot failure")

    def assert_current(self, expected_version: int, expected_hash: str) -> None:
        raise AssertionError("assert_current must not be reached")


def _context(*, limits: RiskLimits | None = None, **changes: object) -> RiskExecutionContext:
    snapshot = empty_snapshot(initial_equity=100.0)
    values: dict[str, object] = {
        "provider_id": "provider-a",
        "state_version": 0,
        "trading_day": "2026-08-14",
        "risk_limits": limits or RiskLimits(max_position_size=5.0),
        "exposure_snapshot": snapshot,
        "signed_positions": {"ES": 0.0},
        "daily_realized_pnl": snapshot.daily_pnl,
        "current_equity": snapshot.current_equity,
        "peak_equity": snapshot.peak_equity,
        "execution_enabled": True,
        "kill_switch_active": False,
        "legacy_hard_deny": False,
    }
    values.update(changes)
    return RiskExecutionContext(**values)  # type: ignore[arg-type]


def _intent(**changes: object) -> ExecutionIntent:
    values: dict[str, object] = {
        "intent_id": "intent-1",
        "symbol": "ES",
        "side": IntentSide.BUY,
        "quantity": 1.0,
        "estimated_price": 100.0,
        "timestamp": datetime(2026, 8, 14, 8, 0, tzinfo=timezone.utc),
    }
    values.update(changes)
    return ExecutionIntent(**values)  # type: ignore[arg-type]


def _setup(
    *,
    context: RiskExecutionContext | None = None,
    manager_limits: RiskLimits | None = None,
    error: Exception | None = None,
) -> tuple[InMemoryRiskContextProvider, CountingRiskManager, RiskAuthorizationBoundary]:
    actual_context = context or _context()
    manager = CountingRiskManager(manager_limits or actual_context.risk_limits, error=error)
    provider = InMemoryRiskContextProvider(actual_context)
    return provider, manager, RiskAuthorizationBoundary(manager, provider)


def _authorize(boundary: RiskAuthorizationBoundary, provider: InMemoryRiskContextProvider, intent: object | None = None):
    context = provider.snapshot()
    return boundary.authorize(
        _intent() if intent is None else intent,
        expected_provider_id=context.provider_id,
        expected_context_state_version=context.state_version,
        expected_context_state_hash=context.state_hash,
    )


def test_allowed_decision_is_non_vacuous() -> None:
    provider, manager, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    assert decision.allowed is True
    assert decision.schema_version == AUTHORIZATION_SCHEMA_VERSION
    assert decision.intent_id == intent.intent_id
    assert decision.authorization_id == f"risk-auth-{decision.decision_hash}"
    assert len(decision.decision_hash) == 64
    assert manager.call_count == 1
    boundary.verify_for_execution(decision, intent)


def test_risk_manager_real_violation_blocks_decision() -> None:
    limits = RiskLimits(max_position_size=0.5)
    provider, manager, boundary = _setup(context=_context(limits=limits))
    decision = _authorize(boundary, provider)
    assert decision.allowed is False
    assert manager.call_count == 1
    assert [violation.code for violation in decision.violations] == ["POSITION_SIZE_EXCEEDED"]
    assert decision.guard_codes == ("RISK_MANAGER_BLOCKED",)


def test_evaluated_path_calls_validate_exactly_once() -> None:
    provider, manager, boundary = _setup()
    _authorize(boundary, provider)
    assert manager.call_count == 1


def test_execution_disabled_blocks_without_validate() -> None:
    provider, manager, boundary = _setup(context=_context(execution_enabled=False))
    decision = _authorize(boundary, provider)
    assert not decision.allowed
    assert "EXECUTION_DISABLED" in decision.guard_codes
    assert manager.call_count == 0


def test_kill_switch_blocks_without_validate() -> None:
    provider, manager, boundary = _setup(context=_context(kill_switch_active=True))
    decision = _authorize(boundary, provider)
    assert not decision.allowed
    assert "KILL_SWITCH_ACTIVE" in decision.guard_codes
    assert manager.call_count == 0


def test_legacy_hard_deny_blocks_without_validate() -> None:
    provider, manager, boundary = _setup(context=_context(legacy_hard_deny=True))
    decision = _authorize(boundary, provider)
    assert not decision.allowed
    assert "LEGACY_HARD_DENY" in decision.guard_codes
    assert manager.call_count == 0


def test_stale_context_version_is_rejected_before_validate() -> None:
    provider, manager, boundary = _setup()
    current = provider.snapshot()
    decision = boundary.authorize(
        _intent(),
        expected_provider_id=current.provider_id,
        expected_context_state_version=current.state_version + 1,
        expected_context_state_hash=current.state_hash,
    )
    assert decision.guard_codes == ("STALE_RISK_CONTEXT",)
    assert manager.call_count == 0


def test_incorrect_expected_state_hash_is_rejected_before_validate() -> None:
    provider, manager, boundary = _setup()
    current = provider.snapshot()
    decision = boundary.authorize(
        _intent(),
        expected_provider_id=current.provider_id,
        expected_context_state_version=current.state_version,
        expected_context_state_hash="0" * 64,
    )
    assert decision.guard_codes == ("STALE_RISK_CONTEXT",)
    assert manager.call_count == 0


def test_manager_limits_mismatch_blocks_before_validate() -> None:
    provider, manager, boundary = _setup(manager_limits=RiskLimits(max_position_size=4.0))
    decision = _authorize(boundary, provider)
    assert decision.guard_codes == ("RISK_LIMITS_MISMATCH",)
    assert manager.call_count == 0


def test_risk_manager_exception_becomes_controlled_fail_closed_decision() -> None:
    provider, manager, boundary = _setup(error=RuntimeError("synthetic failure"))
    decision = _authorize(boundary, provider)
    assert decision.allowed is False
    assert decision.guard_codes == ("RISK_MANAGER_EXCEPTION",)
    assert decision.violations == ()
    assert manager.call_count == 1


def test_identical_inputs_produce_identical_decision_identity() -> None:
    provider, manager, boundary = _setup()
    left = _authorize(boundary, provider)
    right = _authorize(boundary, provider)
    assert left.decision_hash == right.decision_hash
    assert left.authorization_id == right.authorization_id
    assert manager.call_count == 2


def test_different_risk_result_timestamps_do_not_change_identity(monkeypatch) -> None:
    first = datetime(2026, 8, 14, 8, 1, tzinfo=timezone.utc)
    moments = iter((first, first + timedelta(seconds=10)))
    monkeypatch.setattr("agicore.risk.risk_manager._utcnow", lambda: next(moments))
    provider, _, boundary = _setup()
    left = _authorize(boundary, provider)
    right = _authorize(boundary, provider)
    assert left.decision_hash == right.decision_hash
    assert left.authorization_id == right.authorization_id


def test_changed_intent_changes_intent_and_decision_hashes() -> None:
    provider, _, boundary = _setup()
    left = _authorize(boundary, provider, _intent())
    right = _authorize(boundary, provider, _intent(quantity=2.0))
    assert left.intent_hash != right.intent_hash
    assert left.decision_hash != right.decision_hash


def test_changed_context_version_changes_decision_hash() -> None:
    provider, _, boundary = _setup()
    before = _authorize(boundary, provider)
    current = provider.snapshot()
    provider.start_trading_day(current.state_version, current.state_hash, "2026-08-15")
    after = _authorize(boundary, provider)
    assert after.context_state_version == before.context_state_version + 1
    assert after.context_state_hash != before.context_state_hash
    assert after.decision_hash != before.decision_hash


def test_changed_limits_change_limits_and_decision_hashes() -> None:
    left_provider, _, left_boundary = _setup(context=_context(limits=RiskLimits(max_position_size=5.0)))
    right_provider, _, right_boundary = _setup(context=_context(limits=RiskLimits(max_position_size=6.0)))
    left = _authorize(left_boundary, left_provider)
    right = _authorize(right_boundary, right_provider)
    assert left.risk_limits_hash != right.risk_limits_hash
    assert left.decision_hash != right.decision_hash


def test_decision_and_violations_are_deeply_immutable() -> None:
    limits = RiskLimits(max_position_size=0.5)
    provider, _, boundary = _setup(context=_context(limits=limits))
    decision = _authorize(boundary, provider)
    assert isinstance(decision.violations, tuple) and decision.violations
    assert isinstance(decision.guard_codes, tuple)
    with pytest.raises(FrozenInstanceError):
        decision.allowed = True  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        decision.violations[0].message = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        decision.canonical()["allowed"] = True  # type: ignore[index]


def test_tampered_decision_is_detected() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    forged = replace(decision, context_state_hash="0" * 64)
    with pytest.raises(RiskAuthorizationError, match="integrity"):
        boundary.verify_for_execution(forged, intent)


def test_pre_execution_verification_rejects_stale_decision() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    current = provider.snapshot()
    provider.start_trading_day(current.state_version, current.state_hash, "2026-08-15")
    with pytest.raises(RiskAuthorizationError, match="no longer current"):
        boundary.verify_for_execution(decision, intent)


def test_authorization_mutates_neither_context_nor_journal() -> None:
    provider, _, boundary = _setup()
    before_context, before_journal = provider.snapshot(), provider.journal
    decision = _authorize(boundary, provider)
    assert decision.allowed
    assert provider.snapshot() == before_context
    assert provider.journal == before_journal


def test_decision_canonical_form_has_no_implicit_nondeterministic_fields() -> None:
    provider, _, boundary = _setup()
    decision = _authorize(boundary, provider)

    def keys(value: object) -> list[str]:
        if hasattr(value, "items"):
            return [item for key, nested in value.items() for item in [str(key), *keys(nested)]]
        if isinstance(value, (list, tuple)):
            return [item for nested in value for item in keys(nested)]
        return []

    forbidden = {"timestamp", "generated_at", "uuid", "nonce", "random"}
    assert not (forbidden & {key.lower() for key in keys(decision.canonical())})


def test_invalid_intent_blocks_before_validate_with_deterministic_fallback_hash() -> None:
    provider, manager, boundary = _setup()
    left = _authorize(boundary, provider, object())
    right = _authorize(boundary, provider, object())
    assert left.guard_codes == ("INVALID_INTENT",)
    assert left.intent_hash == right.intent_hash
    assert left.decision_hash == right.decision_hash
    assert manager.call_count == 0


def test_provider_mismatch_blocks_before_validate() -> None:
    provider, manager, boundary = _setup()
    context = provider.snapshot()
    decision = boundary.authorize(
        _intent(),
        expected_provider_id="provider-b",
        expected_context_state_version=context.state_version,
        expected_context_state_hash=context.state_hash,
    )
    assert decision.guard_codes == ("PROVIDER_MISMATCH",)
    assert manager.call_count == 0


def test_rehashed_allowed_decision_not_issued_by_boundary_is_rejected() -> None:
    limits = RiskLimits(max_position_size=0.5)
    context = _context(limits=limits)
    provider, manager, boundary = _setup(context=context)
    intent = _intent()
    blocked = _authorize(boundary, provider, intent)
    assert not blocked.allowed and blocked.violations
    forged = RiskAuthorizationDecision.create(
        allowed=True,
        provider_id=context.provider_id,
        intent_id=intent.intent_id,
        intent_hash=blocked.intent_hash,
        context=context,
        risk_limits_hash=blocked.risk_limits_hash,
    )
    assert forged.is_intact()
    assert manager.call_count == 1
    with pytest.raises(RiskAuthorizationError, match="UNISSUED_AUTHORIZATION"):
        boundary.verify_for_execution(forged, intent)


def test_decision_issued_by_same_boundary_is_accepted() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    boundary.verify_for_execution(decision, intent)


def test_decision_issued_by_other_boundary_is_rejected() -> None:
    provider, manager, issuing_boundary = _setup()
    verifying_boundary = RiskAuthorizationBoundary(manager, provider)
    intent = _intent()
    decision = _authorize(issuing_boundary, provider, intent)
    with pytest.raises(RiskAuthorizationError, match="UNISSUED_AUTHORIZATION"):
        verifying_boundary.verify_for_execution(decision, intent)


def test_snapshot_a_confirmation_of_state_b_blocks_without_validate() -> None:
    snapshot_a = _context()
    snapshot_b = _context(state_version=1, trading_day="2026-08-15")
    provider = ScriptedContextProvider(snapshot_b)
    provider.current = snapshot_a

    def confirm_only_b(expected_version: int, expected_hash: str) -> None:
        if expected_version != snapshot_b.state_version or expected_hash != snapshot_b.state_hash:
            raise RiskContextError("STALE_RISK_CONTEXT", "only state B is current")

    provider.assert_current = confirm_only_b  # type: ignore[method-assign]
    manager = CountingRiskManager(snapshot_a.risk_limits)
    boundary = RiskAuthorizationBoundary(manager, provider)
    decision = boundary.authorize(
        _intent(),
        expected_provider_id=snapshot_a.provider_id,
        expected_context_state_version=snapshot_a.state_version,
        expected_context_state_hash=snapshot_a.state_hash,
    )
    assert decision.guard_codes == ("STALE_RISK_CONTEXT",)
    assert manager.call_count == 0


def test_snapshot_provider_runtime_error_becomes_controlled_error() -> None:
    manager = CountingRiskManager(RiskLimits(max_position_size=5.0))
    boundary = RiskAuthorizationBoundary(manager, RaisingSnapshotProvider())  # type: ignore[arg-type]
    with pytest.raises(RiskAuthorizationError, match="CONTEXT_PROVIDER_ERROR"):
        boundary.authorize(
            _intent(),
            expected_provider_id="provider-a",
            expected_context_state_version=0,
            expected_context_state_hash="0" * 64,
        )
    assert manager.call_count == 0


def test_assert_current_runtime_error_blocks_without_validate() -> None:
    context = _context()
    provider = ScriptedContextProvider(context, assert_error=RuntimeError("synthetic CAS failure"))
    manager = CountingRiskManager(context.risk_limits)
    boundary = RiskAuthorizationBoundary(manager, provider)
    decision = boundary.authorize(
        _intent(),
        expected_provider_id=context.provider_id,
        expected_context_state_version=context.state_version,
        expected_context_state_hash=context.state_hash,
    )
    assert decision.guard_codes == ("CONTEXT_PROVIDER_ERROR",)
    assert manager.call_count == 0


def test_model_construct_invalid_intent_blocks_without_raw_exception() -> None:
    malformed = ExecutionIntent.model_construct(
        intent_id="",
        symbol="ES",
        side="BUY",
        quantity=float("nan"),
        estimated_price=100.0,
        timestamp="not-a-datetime",
    )
    provider, manager, boundary = _setup()
    decision = _authorize(boundary, provider, malformed)
    assert decision.guard_codes == ("INVALID_INTENT",)
    assert manager.call_count == 0


def test_verify_rejects_different_intent() -> None:
    provider, _, boundary = _setup()
    decision = _authorize(boundary, provider, _intent())
    with pytest.raises(RiskAuthorizationError, match="INTENT_MISMATCH"):
        boundary.verify_for_execution(decision, _intent(quantity=2.0))


def test_verify_rejects_blocked_decision() -> None:
    limits = RiskLimits(max_position_size=0.5)
    provider, _, boundary = _setup(context=_context(limits=limits))
    decision = _authorize(boundary, provider)
    with pytest.raises(RiskAuthorizationError, match="RISK_AUTHORIZATION_BLOCKED"):
        boundary.verify_for_execution(decision, _intent())


def test_verify_rejects_manager_limits_changed_after_authorization() -> None:
    provider, manager, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    manager._limits = RiskLimits(max_position_size=4.0)
    with pytest.raises(RiskAuthorizationError, match="RISK_LIMITS_MISMATCH"):
        boundary.verify_for_execution(decision, intent)


def test_verify_rejects_current_provider_incoherence() -> None:
    initial = _context()
    provider = ScriptedContextProvider(initial)
    manager = CountingRiskManager(initial.risk_limits)
    boundary = RiskAuthorizationBoundary(manager, provider)
    intent = _intent()
    decision = boundary.authorize(
        intent,
        expected_provider_id=initial.provider_id,
        expected_context_state_version=initial.state_version,
        expected_context_state_hash=initial.state_hash,
    )
    provider.current = _context(provider_id="provider-b")
    with pytest.raises(RiskAuthorizationError, match="PROVIDER_MISMATCH"):
        boundary.verify_for_execution(decision, intent)


def test_structurally_falsified_violations_make_is_intact_false() -> None:
    provider, _, boundary = _setup()
    decision = _authorize(boundary, provider)
    forged = replace(decision, violations=({"code": "BLOCK"},))
    assert forged.is_intact() is False


def test_allowed_decision_with_blocking_guard_is_impossible() -> None:
    provider, _, boundary = _setup()
    issued = _authorize(boundary, provider)
    with pytest.raises(RiskAuthorizationError, match="blocking cause"):
        RiskAuthorizationDecision.create(
            allowed=True,
            provider_id=issued.provider_id,
            intent_id=issued.intent_id,
            intent_hash=issued.intent_hash,
            context=provider.snapshot(),
            risk_limits_hash=issued.risk_limits_hash,
            guard_codes=("EXECUTION_DISABLED",),
        )


@pytest.mark.parametrize("mode", ["allowed", "blocked", "exception"])
def test_context_and_journal_remain_unchanged_for_all_authorization_outcomes(mode: str) -> None:
    if mode == "blocked":
        limits = RiskLimits(max_position_size=0.5)
        provider, _, boundary = _setup(context=_context(limits=limits))
    elif mode == "exception":
        provider, _, boundary = _setup(error=RuntimeError("synthetic"))
    else:
        provider, _, boundary = _setup()
    before = (provider.snapshot(), provider.journal)
    decision = _authorize(boundary, provider)
    assert decision.allowed is (mode == "allowed")
    assert (provider.snapshot(), provider.journal) == before


def test_identical_concurrent_authorizations_share_identity_and_consume_once() -> None:
    provider, manager, boundary = _setup()
    intent = _intent()
    with ThreadPoolExecutor(max_workers=8) as executor:
        decisions = list(executor.map(lambda _: _authorize(boundary, provider, intent), range(32)))
    assert len({decision.decision_hash for decision in decisions}) == 1
    assert len({decision.authorization_id for decision in decisions}) == 1
    assert manager.call_count == 32
    consumption = boundary.verify_for_execution(decisions[0], intent)
    assert consumption.is_intact()
    for decision in decisions[1:]:
        with pytest.raises(RiskAuthorizationError, match="AUTHORIZATION_ALREADY_CONSUMED"):
            boundary.verify_for_execution(decision, intent)


def test_first_verification_consumes_authorization_successfully() -> None:
    provider, manager, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    calls_before = manager.call_count
    consumption = boundary.verify_for_execution(decision, intent)
    assert consumption.is_intact()
    assert boundary.consumptions == (consumption,)
    assert manager.call_count == calls_before == 1


def test_consumption_record_is_complete_intact_and_immutable() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    consumption = boundary.verify_for_execution(decision, intent)
    assert consumption.schema_version == CONSUMPTION_SCHEMA_VERSION
    assert consumption.authorization_id == decision.authorization_id
    assert consumption.decision_hash == decision.decision_hash
    assert consumption.provider_id == decision.provider_id
    assert consumption.intent_id == intent.intent_id
    assert consumption.intent_hash == decision.intent_hash
    assert consumption.context_state_version == decision.context_state_version
    assert consumption.context_state_hash == decision.context_state_hash
    assert consumption.risk_limits_hash == decision.risk_limits_hash
    assert consumption.consumption_id == f"risk-consumption-{consumption.consumption_hash}"
    assert consumption.is_intact()
    with pytest.raises(FrozenInstanceError):
        consumption.intent_id = "changed"  # type: ignore[misc]
    with pytest.raises(TypeError):
        consumption.canonical()["intent_id"] = "changed"  # type: ignore[index]


def test_second_consumption_of_same_decision_is_rejected() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    first = boundary.verify_for_execution(decision, intent)
    with pytest.raises(RiskAuthorizationError, match="AUTHORIZATION_ALREADY_CONSUMED"):
        boundary.verify_for_execution(decision, intent)
    assert boundary.consumptions == (first,)


def test_identical_copy_of_consumed_decision_is_rejected() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    boundary.verify_for_execution(decision, intent)
    identical_copy = replace(decision)
    assert identical_copy == decision and identical_copy is not decision
    with pytest.raises(RiskAuthorizationError, match="AUTHORIZATION_ALREADY_CONSUMED"):
        boundary.verify_for_execution(identical_copy, intent)
    assert len(boundary.consumptions) == 1


def test_new_decision_with_consumed_intent_id_is_rejected() -> None:
    provider, _, boundary = _setup()
    first_intent = _intent(quantity=1.0)
    second_intent = _intent(quantity=2.0)
    first_decision = _authorize(boundary, provider, first_intent)
    second_decision = _authorize(boundary, provider, second_intent)
    assert first_decision.decision_hash != second_decision.decision_hash
    boundary.verify_for_execution(first_decision, first_intent)
    with pytest.raises(RiskAuthorizationError, match="INTENT_ALREADY_CONSUMED"):
        boundary.verify_for_execution(second_decision, second_intent)
    assert len(boundary.consumptions) == 1


def test_distinct_intents_are_consumed_independently() -> None:
    provider, _, boundary = _setup()
    intents = (_intent(intent_id="intent-a"), _intent(intent_id="intent-b", quantity=2.0))
    decisions = tuple(_authorize(boundary, provider, intent) for intent in intents)
    consumptions = tuple(
        boundary.verify_for_execution(decision, intent)
        for decision, intent in zip(decisions, intents, strict=True)
    )
    assert len(consumptions) == 2
    assert len({item.consumption_hash for item in consumptions}) == 2
    assert boundary.consumptions == tuple(sorted(consumptions, key=lambda item: (item.intent_id, item.decision_hash)))


def test_blocked_decision_is_rejected_without_consumption() -> None:
    limits = RiskLimits(max_position_size=0.5)
    provider, _, boundary = _setup(context=_context(limits=limits))
    decision = _authorize(boundary, provider)
    assert not decision.allowed
    with pytest.raises(RiskAuthorizationError, match="RISK_AUTHORIZATION_BLOCKED"):
        boundary.verify_for_execution(decision, _intent())
    assert boundary.consumptions == ()


def test_unissued_and_other_boundary_decisions_are_not_consumed() -> None:
    provider, manager, issuer = _setup()
    verifier = RiskAuthorizationBoundary(manager, provider)
    intent = _intent()
    issued = _authorize(issuer, provider, intent)
    manual = replace(issued)
    with pytest.raises(RiskAuthorizationError, match="UNISSUED_AUTHORIZATION"):
        verifier.verify_for_execution(manual, intent)
    assert verifier.consumptions == ()
    assert issuer.consumptions == ()


@pytest.mark.parametrize("failure", ["intent", "stale", "provider", "limits"])
def test_verification_failures_leave_consumption_registry_empty(failure: str) -> None:
    provider, manager, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    attempted_intent = intent
    expected_code = ""
    if failure == "intent":
        attempted_intent = _intent(quantity=2.0)
        expected_code = "AUTHORIZATION_INTENT_MISMATCH"
    elif failure == "stale":
        current = provider.snapshot()
        provider.start_trading_day(current.state_version, current.state_hash, "2026-08-15")
        expected_code = "STALE_RISK_CONTEXT"
    elif failure == "provider":
        boundary._context_provider = ScriptedContextProvider(_context(provider_id="provider-b"))  # type: ignore[attr-defined]
        expected_code = "AUTHORIZATION_PROVIDER_MISMATCH"
    else:
        manager._limits = RiskLimits(max_position_size=4.0)
        expected_code = "RISK_LIMITS_MISMATCH"
    with pytest.raises(RiskAuthorizationError, match=expected_code):
        boundary.verify_for_execution(decision, attempted_intent)
    assert boundary.consumptions == ()


@pytest.mark.parametrize("failure_point", ["snapshot", "assert_current"])
def test_provider_error_is_controlled_without_consumption(failure_point: str) -> None:
    context = _context()
    provider = ScriptedContextProvider(context)
    manager = CountingRiskManager(context.risk_limits)
    boundary = RiskAuthorizationBoundary(manager, provider)
    intent = _intent()
    decision = boundary.authorize(
        intent,
        expected_provider_id=context.provider_id,
        expected_context_state_version=context.state_version,
        expected_context_state_hash=context.state_hash,
    )
    if failure_point == "snapshot":
        provider.snapshot_error = RuntimeError("synthetic snapshot failure")
    else:
        provider.assert_error = RuntimeError("synthetic confirmation failure")
    with pytest.raises(RiskAuthorizationError, match="CONTEXT_PROVIDER_ERROR"):
        boundary.verify_for_execution(decision, intent)
    assert boundary.consumptions == ()


def test_consumption_does_not_revalidate_or_mutate_context_journal() -> None:
    provider, manager, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    before_context = provider.snapshot()
    before_journal = provider.journal
    calls_before = manager.call_count
    boundary.verify_for_execution(decision, intent)
    assert manager.call_count == calls_before == 1
    assert provider.snapshot() == before_context
    assert provider.journal == before_journal


def test_consumption_hash_is_deterministic_without_nondeterministic_fields() -> None:
    records = []
    for _ in range(2):
        provider, _, boundary = _setup()
        intent = _intent()
        records.append(boundary.verify_for_execution(_authorize(boundary, provider, intent), intent))
    left, right = records
    assert left == right
    assert left.consumption_hash == right.consumption_hash

    def keys(value: object) -> list[str]:
        if hasattr(value, "items"):
            return [item for key, nested in value.items() for item in [str(key), *keys(nested)]]
        if isinstance(value, (list, tuple)):
            return [item for nested in value for item in keys(nested)]
        return []

    forbidden = {"timestamp", "generated_at", "uuid", "nonce", "random"}
    assert not (forbidden & {key.lower() for key in keys(left.canonical())})


def test_falsified_consumption_record_is_not_intact() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    record = boundary.verify_for_execution(_authorize(boundary, provider, intent), intent)
    assert replace(record, intent_hash="0" * 64).is_intact() is False
    assert replace(record, consumption_hash="not-a-hash").is_intact() is False
    assert replace(record, context_state_version=True).is_intact() is False


def test_concurrent_consumption_of_same_decision_has_exactly_one_winner() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)

    def consume(_: int) -> str:
        try:
            boundary.verify_for_execution(decision, intent)
            return "SUCCESS"
        except RiskAuthorizationError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=16) as executor:
        outcomes = list(executor.map(consume, range(64)))
    assert outcomes.count("SUCCESS") == 1
    assert outcomes.count("AUTHORIZATION_ALREADY_CONSUMED") == 63
    assert len(boundary.consumptions) == 1


def test_concurrent_distinct_decisions_with_same_intent_id_have_one_winner() -> None:
    provider, _, boundary = _setup()
    intents = (_intent(quantity=1.0), _intent(quantity=2.0))
    decisions = tuple(_authorize(boundary, provider, intent) for intent in intents)
    assert decisions[0].decision_hash != decisions[1].decision_hash

    def consume(index: int) -> str:
        try:
            boundary.verify_for_execution(decisions[index], intents[index])
            return "SUCCESS"
        except RiskAuthorizationError as exc:
            return exc.code

    with ThreadPoolExecutor(max_workers=2) as executor:
        outcomes = list(executor.map(consume, (0, 1)))
    assert outcomes.count("SUCCESS") == 1
    assert outcomes.count("INTENT_ALREADY_CONSUMED") == 1
    assert len(boundary.consumptions) == 1


def test_consumption_audit_registry_is_canonical_and_deeply_immutable() -> None:
    provider, _, boundary = _setup()
    intents = tuple(_intent(intent_id=f"intent-{suffix}") for suffix in ("z", "a", "m"))
    decisions = tuple(_authorize(boundary, provider, intent) for intent in intents)
    with ThreadPoolExecutor(max_workers=3) as executor:
        list(executor.map(lambda pair: boundary.verify_for_execution(*pair), zip(decisions, intents, strict=True)))
    audit = boundary.consumptions
    assert isinstance(audit, tuple) and len(audit) == 3
    assert [item.intent_id for item in audit] == ["intent-a", "intent-m", "intent-z"]
    with pytest.raises(TypeError):
        audit[0].canonical()["provider_id"] = "changed"  # type: ignore[index]
    detached = audit + ()
    assert detached == boundary.consumptions


@pytest.mark.parametrize("interrupt", [KeyboardInterrupt(), SystemExit()])
def test_consumption_does_not_mask_process_control_exceptions(interrupt: BaseException) -> None:
    context = _context()
    provider = ScriptedContextProvider(context)
    manager = CountingRiskManager(context.risk_limits)
    boundary = RiskAuthorizationBoundary(manager, provider)
    intent = _intent()
    decision = boundary.authorize(
        intent,
        expected_provider_id=context.provider_id,
        expected_context_state_version=context.state_version,
        expected_context_state_hash=context.state_hash,
    )
    provider.snapshot_error = interrupt
    with pytest.raises(type(interrupt)):
        boundary.verify_for_execution(decision, intent)
    assert boundary.consumptions == ()


def test_recalculated_consumption_before_consumption_is_unissued() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    recalculated = RiskAuthorizationConsumption._from_decision(decision)
    assert not hasattr(RiskAuthorizationConsumption, "create")
    assert recalculated.is_intact()
    with pytest.raises(RiskAuthorizationError, match="UNISSUED_CONSUMPTION"):
        boundary.verify_consumption_evidence(recalculated)
    assert boundary.consumptions == ()


def test_consumption_from_another_boundary_is_unissued() -> None:
    first_provider, _, first_boundary = _setup()
    second_provider, _, second_boundary = _setup()
    intent = _intent()
    first_record = first_boundary.verify_for_execution(
        _authorize(first_boundary, first_provider, intent),
        intent,
    )
    second_decision = _authorize(second_boundary, second_provider, intent)
    assert second_decision.decision_hash == first_record.decision_hash
    with pytest.raises(RiskAuthorizationError, match="UNISSUED_CONSUMPTION"):
        second_boundary.verify_consumption_evidence(first_record)
    assert second_boundary.consumptions == ()


def test_consumption_evidence_issued_by_same_boundary_is_accepted() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    record = boundary.verify_for_execution(_authorize(boundary, provider, intent), intent)
    verified = boundary.verify_consumption_evidence(record)
    assert verified is record
    assert boundary.consumptions == (record,)


def test_rehashed_consumption_with_wrong_authorization_id_is_rejected() -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    record = boundary.verify_for_execution(_authorize(boundary, provider, intent), intent)
    wrong_authorization = replace(record, authorization_id=f"risk-auth-{'f' * 64}")
    canonical = json.dumps(
        wrong_authorization.fields_without_identity(),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    forged_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    forged = replace(
        wrong_authorization,
        consumption_hash=forged_hash,
        consumption_id=f"risk-consumption-{forged_hash}",
    )
    assert forged.consumption_hash != record.consumption_hash
    assert forged.is_intact() is False
    with pytest.raises(RiskAuthorizationError, match="INVALID_CONSUMPTION"):
        boundary.verify_consumption_evidence(forged)
    assert boundary.consumptions == (record,)


@pytest.mark.parametrize("failure", [MemoryError("synthetic"), KeyboardInterrupt(), SystemExit()])
def test_failure_exactly_before_publication_leaves_no_partial_state(
    monkeypatch,
    failure: BaseException,
) -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    proposed_states: list[tuple[RiskAuthorizationConsumption, ...]] = []

    def fail_before_publication(next_state) -> None:
        proposed_states.append(tuple(next_state.values()))
        raise failure

    monkeypatch.setattr(boundary, "_publish_consumption_state", fail_before_publication)
    expected_exception = RiskAuthorizationError if isinstance(failure, Exception) else type(failure)
    with pytest.raises(expected_exception):
        boundary.verify_for_execution(decision, intent)
    assert len(proposed_states) == 1
    assert len(proposed_states[0]) == 1
    assert proposed_states[0][0].decision_hash == decision.decision_hash
    assert boundary.consumptions == ()


def test_intent_remains_consumable_exactly_once_after_publication_failure(monkeypatch) -> None:
    provider, _, boundary = _setup()
    intent = _intent()
    decision = _authorize(boundary, provider, intent)
    publisher = boundary._publish_consumption_state

    def fail_before_publication(next_state) -> None:
        assert tuple(next_state) == (decision.decision_hash,)
        raise MemoryError("synthetic publication failure")

    monkeypatch.setattr(boundary, "_publish_consumption_state", fail_before_publication)
    with pytest.raises(RiskAuthorizationError, match="CONSUMPTION_PUBLICATION_ERROR"):
        boundary.verify_for_execution(decision, intent)
    assert boundary.consumptions == ()

    monkeypatch.setattr(boundary, "_publish_consumption_state", publisher)
    record = boundary.verify_for_execution(decision, intent)
    assert boundary.consumptions == (record,)
    with pytest.raises(RiskAuthorizationError, match="AUTHORIZATION_ALREADY_CONSUMED"):
        boundary.verify_for_execution(decision, intent)
    assert boundary.consumptions == (record,)
