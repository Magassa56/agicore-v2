"""Non-vacuous contract tests for the deterministic risk-context journal."""
from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from typing import Iterable

import pytest

from agicore.risk.exposure_models import ExposureSnapshot, RiskLimits, SymbolExposure, empty_snapshot
from agicore.risk.risk_execution_context import (
    FillTransition,
    GENESIS_EVENT_HASH,
    InMemoryRiskContextProvider,
    RiskContextError,
    RiskExecutionContext,
    RiskExecutionJournalEvent,
    SCHEMA_VERSION,
    replay_journal,
)


def _snapshot(
    *,
    daily_pnl: float = 0.0,
    current_equity: float = 100.0,
    peak_equity: float = 100.0,
    positions: dict[str, object] | None = None,
) -> ExposureSnapshot:
    return ExposureSnapshot(
        positions={} if positions is None else positions,
        realized_pnl_total=current_equity - 100.0,
        daily_pnl=daily_pnl,
        initial_equity=100.0,
        peak_equity=peak_equity,
    )


def _long_es_snapshot(
    *,
    daily_pnl: float = 2.0,
    current_equity: float = 102.0,
    peak_equity: float = 102.0,
) -> ExposureSnapshot:
    return _snapshot(
        daily_pnl=daily_pnl,
        current_equity=current_equity,
        peak_equity=peak_equity,
        positions={"ES": SymbolExposure(symbol="ES", quantity=1.0, avg_entry_price=100.0, mark_price=101.0)},
    )


def _context(**changes: object) -> RiskExecutionContext:
    values: dict[str, object] = {
        "provider_id": "provider-a",
        "state_version": 0,
        "trading_day": "2026-01-01",
        "risk_limits": RiskLimits(max_position_size=5),
        "exposure_snapshot": _snapshot(),
        "signed_positions": {"ES": 0.0},
        "daily_realized_pnl": 0.0,
        "current_equity": 100.0,
        "peak_equity": 100.0,
        "execution_enabled": True,
        "kill_switch_active": False,
        "legacy_hard_deny": False,
    }
    values.update(changes)
    return RiskExecutionContext(**values)  # type: ignore[arg-type]


def _transition(**changes: object) -> FillTransition:
    values: dict[str, object] = {
        "intent_id": "intent-1",
        "fill_id": "fill-1",
        "signed_positions": {"ES": 1.0},
        "exposure_snapshot": _long_es_snapshot(),
        "daily_realized_pnl": 2.0,
        "current_equity": 102.0,
        "expected_peak_equity": 102.0,
        "payload": {"accounting": {"source": "synthetic"}},
    }
    values.update(changes)
    if "exposure_snapshot" not in changes:
        values["exposure_snapshot"] = _long_es_snapshot(
            daily_pnl=float(values["daily_realized_pnl"]),
            current_equity=float(values["current_equity"]),
            peak_equity=float(values["expected_peak_equity"]),
        )
    return FillTransition(**values)  # type: ignore[arg-type]


def _provider_with_operations() -> tuple[InMemoryRiskContextProvider, RiskExecutionContext, RiskExecutionContext, RiskExecutionContext]:
    provider = InMemoryRiskContextProvider(_context())
    initial = provider.snapshot()
    filled = provider.commit_fill(initial.state_version, initial.state_hash, _transition())
    final = provider.start_trading_day(filled.state_version, filled.state_hash, "2026-01-02")
    return provider, initial, filled, final


def _replace_event(event: RiskExecutionJournalEvent, **changes: object) -> RiskExecutionJournalEvent:
    return replace(event, **changes)


def _rechain(events: Iterable[RiskExecutionJournalEvent]) -> tuple[RiskExecutionJournalEvent, ...]:
    """Create a validly chained but different journal for anchor tests."""
    previous = GENESIS_EVENT_HASH
    rewritten: list[RiskExecutionJournalEvent] = []
    for sequence, original in enumerate(events, start=1):
        event = RiskExecutionJournalEvent.create(
            sequence_number=sequence,
            event_type=original.event_type,
            provider_id=original.provider_id,
            intent_id=original.intent_id,
            state_version_before=original.state_version_before,
            state_version_after=original.state_version_after,
            context_hash_before=original.context_hash_before,
            context_hash_after=original.context_hash_after,
            payload=original.payload,
            previous_event_hash=previous,
        )
        rewritten.append(event)
        previous = event.event_hash
    return tuple(rewritten)


def _assert_raises_without_mutation(provider: InMemoryRiskContextProvider, action: object) -> None:
    before_context, before_journal = provider.snapshot(), provider.journal
    with pytest.raises(RiskContextError):
        action()  # type: ignore[operator]
    assert provider.snapshot() == before_context
    assert provider.journal == before_journal


def test_provider_initializes_journal_with_context_snapshot() -> None:
    provider = InMemoryRiskContextProvider(_context())
    events = provider.journal
    assert isinstance(events, tuple)
    assert len(events) == 1
    event = events[0]
    assert event.event_type == "CONTEXT_SNAPSHOTTED"
    assert event.schema_version == SCHEMA_VERSION
    assert event.sequence_number == 1
    assert event.previous_event_hash == GENESIS_EVENT_HASH
    assert event.payload["context"] == provider.snapshot().canonical()


def test_commit_fill_appends_fill_received_then_state_committed() -> None:
    provider, _, _, _ = _provider_with_operations()
    events = provider.journal
    assert [event.event_type for event in events[:3]] == ["CONTEXT_SNAPSHOTTED", "FILL_RECEIVED", "STATE_COMMITTED"]
    transition = events[1].payload["transition"]
    assert transition["intent_id"] == "intent-1"
    assert transition["fill_id"] == "fill-1"
    assert transition["exposure_snapshot"]["daily_pnl"] == 2.0
    assert transition["exposure_snapshot"]["peak_equity"] == 102.0


def test_start_trading_day_appends_started_then_state_committed() -> None:
    provider, _, _, _ = _provider_with_operations()
    assert [event.event_type for event in provider.journal[3:]] == ["TRADING_DAY_STARTED", "STATE_COMMITTED"]


def test_successful_commit_increments_version_and_changes_state_hash() -> None:
    _, initial, filled, _ = _provider_with_operations()
    assert filled.state_version == initial.state_version + 1
    assert filled.state_hash != initial.state_hash


def test_peak_equity_is_monotonic_after_fill() -> None:
    provider = InMemoryRiskContextProvider(_context())
    before = provider.snapshot()
    after = provider.commit_fill(before.state_version, before.state_hash, _transition(current_equity=90, expected_peak_equity=100))
    assert after.peak_equity == before.peak_equity


def test_daily_realized_pnl_resets_only_on_explicit_trading_day_start() -> None:
    _, _, filled, final = _provider_with_operations()
    assert filled.daily_realized_pnl == 2.0
    assert final.daily_realized_pnl == 0.0
    assert final.trading_day == "2026-01-02"


def test_stale_cas_changes_neither_context_nor_journal() -> None:
    provider = InMemoryRiskContextProvider(_context())
    current = provider.snapshot()
    _assert_raises_without_mutation(provider, lambda: provider.commit_fill(current.state_version + 1, current.state_hash, _transition()))
    _assert_raises_without_mutation(provider, lambda: provider.commit_fill(current.state_version, current.state_hash, _transition(expected_peak_equity=999)))


def test_provider_mismatch_changes_neither_context_nor_journal() -> None:
    provider = InMemoryRiskContextProvider(_context())
    other = _context(provider_id="provider-b")
    _assert_raises_without_mutation(provider, lambda: provider.assert_current(other.state_version, other.state_hash))


def test_replay_reconstructs_exact_provider_final_context() -> None:
    provider, _, _, final = _provider_with_operations()
    replayed, _ = replay_journal(provider.journal)
    assert replayed == final


def test_replay_final_hash_matches_journal_final_hash() -> None:
    provider, _, _, _ = _provider_with_operations()
    assert replay_journal(provider.journal)[1] == provider.journal[-1].event_hash


def test_replay_rejects_tampered_event() -> None:
    provider, _, _, _ = _provider_with_operations()
    copied = list(provider.journal)
    copied[-1] = _replace_event(copied[-1], payload={"context": {"tampered": True}})
    with pytest.raises(RiskContextError, match="stored event hash mismatch"):
        replay_journal(tuple(copied))
    assert provider.journal[-1].payload != copied[-1].payload


def test_replay_rejects_removed_event() -> None:
    provider, _, _, _ = _provider_with_operations()
    with pytest.raises(RiskContextError):
        replay_journal(provider.journal[:2] + provider.journal[3:])


def test_replay_rejects_reordered_events() -> None:
    provider, _, _, _ = _provider_with_operations()
    copied = list(provider.journal)
    copied[1], copied[2] = copied[2], copied[1]
    with pytest.raises(RiskContextError):
        replay_journal(tuple(copied))


def test_replay_rejects_wrong_provider_or_schema() -> None:
    provider, _, _, _ = _provider_with_operations()
    events = list(provider.journal)
    forged_provider = _replace_event(events[1], provider_id="provider-b")
    with pytest.raises(RiskContextError, match="stored event hash mismatch"):
        replay_journal(tuple([events[0], forged_provider, *events[2:]]))
    forged_schema = _replace_event(events[1], schema_version="risk-execution-journal/999")
    with pytest.raises(RiskContextError, match="unsupported schema version"):
        replay_journal(tuple([events[0], forged_schema, *events[2:]]))


def test_replay_rejects_orphan_operational_or_state_committed_event() -> None:
    provider, _, _, _ = _provider_with_operations()
    with pytest.raises(RiskContextError):
        replay_journal((provider.journal[0], provider.journal[2]))
    with pytest.raises(RiskContextError):
        replay_journal((provider.journal[0], provider.journal[1]))


def test_identical_context_and_operations_produce_identical_journals() -> None:
    left = _provider_with_operations()[0].journal
    right = _provider_with_operations()[0].journal
    assert left == right
    assert len(left) >= 5
    assert [event.sequence_number for event in left] == list(range(1, len(left) + 1))
    assert all(left[index].previous_event_hash == left[index - 1].event_hash for index in range(1, len(left)))


def test_external_mutation_does_not_change_context_transition_or_journal() -> None:
    positions = {"ES": 1.0}
    payload = {"nested": {"value": "fixed"}}
    context = _context(
        signed_positions=positions,
        exposure_snapshot=_long_es_snapshot(daily_pnl=0.0, current_equity=100.0, peak_equity=100.0),
    )
    transition = _transition(signed_positions=positions, payload=payload)
    provider = InMemoryRiskContextProvider(context)
    journal_hash = provider.journal[0].event_hash
    positions["ES"] = 999.0
    payload["nested"]["value"] = "mutated"
    assert context.signed_positions["ES"] == 1.0
    assert context.state_hash != ""
    assert transition.signed_positions["ES"] == 1.0
    assert transition.payload["nested"]["value"] == "fixed"
    assert provider.journal[0].event_hash == journal_hash
    with pytest.raises(TypeError):
        provider.journal[0].payload["new"] = "no"  # type: ignore[index]


def test_replay_rejects_rechained_journal_when_final_hash_anchor_is_supplied() -> None:
    provider, _, _, _ = _provider_with_operations()
    original_hash = provider.journal[-1].event_hash
    rewritten = list(provider.journal)
    payload = dict(rewritten[1].payload)
    transition = dict(payload["transition"])
    transition["payload"] = {"accounting": {"source": "rewritten"}}
    payload["transition"] = transition
    rewritten[1] = _replace_event(rewritten[1], payload=payload)
    forged = _rechain(rewritten)
    with pytest.raises(RiskContextError, match="expected anchor"):
        replay_journal(forged, expected_final_hash=original_hash)


def test_replay_rejects_transition_and_exposure_snapshot_incompatible_with_commit() -> None:
    provider, _, _, _ = _provider_with_operations()
    events = list(provider.journal)
    payload = dict(events[1].payload)
    transition = dict(payload["transition"])
    transition["signed_positions"] = {"ES": 2.0}
    payload["transition"] = transition
    events[1] = _replace_event(events[1], payload=payload)
    with pytest.raises(RiskContextError):
        replay_journal(_rechain(events))
    events = list(provider.journal)
    payload = dict(events[1].payload)
    transition = dict(payload["transition"])
    transition["exposure_snapshot"] = empty_snapshot(initial_equity=999).model_dump(mode="json")
    payload["transition"] = transition
    events[1] = _replace_event(events[1], payload=payload)
    with pytest.raises(RiskContextError):
        replay_journal(_rechain(events))


def test_replay_rejects_incompatible_trading_day_before_version_and_context_provider() -> None:
    provider, _, _, _ = _provider_with_operations()
    events = list(provider.journal)
    events[3] = _replace_event(events[3], payload={"new_trading_day": "2026-01-01"})
    with pytest.raises(RiskContextError):
        replay_journal(_rechain(events))
    events = list(provider.journal)
    events[3] = _replace_event(events[3], state_version_before=99)
    with pytest.raises(RiskContextError):
        replay_journal(_rechain(events))
    events = list(provider.journal)
    commit_payload = dict(events[4].payload)
    context_payload = dict(commit_payload["context"])
    context_payload["provider_id"] = "provider-b"
    commit_payload["context"] = context_payload
    events[4] = _replace_event(events[4], payload=commit_payload)
    with pytest.raises(RiskContextError):
        replay_journal(_rechain(events))


def test_event_payloads_have_no_implicit_temporal_or_nondeterministic_keys() -> None:
    provider, _, _, _ = _provider_with_operations()

    def walk(value: object) -> list[str]:
        if isinstance(value, dict) or hasattr(value, "items"):
            return [key for key, nested in value.items() for key in [key, *walk(nested)]]
        if isinstance(value, tuple):
            return [key for nested in value for key in walk(nested)]
        return []

    forbidden = {"timestamp", "generated_at", "uuid", "random", "nonce"}
    assert not (forbidden & set(key.lower() for event in provider.journal for key in walk(event.payload)))


def test_genesis_event_hash_is_sha256_digest() -> None:
    assert len(GENESIS_EVENT_HASH) == 64
    assert all(character in "0123456789abcdef" for character in GENESIS_EVENT_HASH)
    expected = hashlib.sha256(json.dumps({"kind": "risk-execution-journal-genesis", "schema_version": SCHEMA_VERSION}, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()).hexdigest()
    assert GENESIS_EVENT_HASH == expected


@pytest.mark.parametrize("field,value", [("provider_id", " "), ("state_version", True), ("daily_realized_pnl", float("nan")), ("current_equity", float("inf")), ("signed_positions", {" ": 1.0}), ("signed_positions", {"ES": float("nan")})])
def test_context_model_validation_rejects_invalid_values(field: str, value: object) -> None:
    with pytest.raises(RiskContextError):
        _context(**{field: value})


def test_invalid_payload_and_cas_failure_leave_provider_unchanged() -> None:
    with pytest.raises(RiskContextError):
        _transition(payload={"bad": object()})
    provider = InMemoryRiskContextProvider(_context())
    before = (provider.snapshot(), provider.journal)
    with pytest.raises(RiskContextError):
        provider.commit_fill(0, "not-current", _transition())
    assert (provider.snapshot(), provider.journal) == before


def test_context_rejects_snapshot_equity_or_daily_pnl_divergence() -> None:
    with pytest.raises(RiskContextError, match="metrics must match"):
        _context(current_equity=101.0, peak_equity=101.0, exposure_snapshot=_snapshot())
    with pytest.raises(RiskContextError, match="metrics must match"):
        _context(daily_realized_pnl=1.0, exposure_snapshot=_snapshot())


def test_fill_transition_rejects_snapshot_peak_divergence() -> None:
    with pytest.raises(RiskContextError, match="metrics must match"):
        _transition(
            expected_peak_equity=103.0,
            exposure_snapshot=_long_es_snapshot(daily_pnl=2.0, current_equity=102.0, peak_equity=102.0),
        )


def test_invalid_commit_fill_leaves_context_and_journal_unchanged() -> None:
    provider = InMemoryRiskContextProvider(_context())
    current = provider.snapshot()
    invalid = _transition()
    object.__setattr__(invalid, "exposure_snapshot", _snapshot(daily_pnl=2.0, current_equity=102.0, peak_equity=103.0))
    _assert_raises_without_mutation(
        provider,
        lambda: provider.commit_fill(current.state_version, current.state_hash, invalid),
    )


def test_trading_day_reset_rebuilds_consistent_snapshot() -> None:
    _, _, filled, final = _provider_with_operations()
    assert final.daily_realized_pnl == 0.0
    assert final.exposure_snapshot.daily_pnl == 0.0
    assert final.current_equity == filled.current_equity == final.exposure_snapshot.current_equity
    assert final.peak_equity == filled.peak_equity == final.exposure_snapshot.peak_equity
    assert final.signed_positions == filled.signed_positions
    assert final.exposure_snapshot.realized_pnl_total == filled.exposure_snapshot.realized_pnl_total


def test_snapshot_positions_are_defensively_copied_and_deeply_immutable() -> None:
    source_snapshot = _snapshot(
        positions={"ES": SymbolExposure(symbol="ES", quantity=1.0, avg_entry_price=100.0, mark_price=101.0)}
    )
    context = _context(signed_positions={"ES": 1.0}, exposure_snapshot=source_snapshot)
    provider = InMemoryRiskContextProvider(context)
    state_hash = context.state_hash
    event_hash = provider.journal[0].event_hash
    source_snapshot.positions["NQ"] = SymbolExposure(symbol="NQ", quantity=1.0, avg_entry_price=200.0, mark_price=201.0)
    assert "NQ" not in context.exposure_snapshot.positions
    with pytest.raises(TypeError):
        context.exposure_snapshot.positions["NQ"] = source_snapshot.positions["NQ"]
    assert context.state_hash == state_hash
    assert provider.journal[0].event_hash == event_hash


def test_replay_rejects_rechained_state_committed_with_wrong_intent_id() -> None:
    provider, _, _, _ = _provider_with_operations()
    events = list(provider.journal)
    events[2] = _replace_event(events[2], intent_id="wrong-intent")
    with pytest.raises(RiskContextError, match="intent identifiers differ"):
        replay_journal(_rechain(events))


def test_replay_rejects_non_hex_event_hash() -> None:
    provider, _, _, _ = _provider_with_operations()
    events = list(provider.journal)
    events[-1] = _replace_event(events[-1], event_hash="g" * 64)
    with pytest.raises(RiskContextError, match="event hash is invalid"):
        replay_journal(tuple(events))


def test_replay_rejects_non_iterable_journal_cleanly() -> None:
    with pytest.raises(RiskContextError, match="journal must be an iterable"):
        replay_journal(42)


def test_positive_signed_position_without_snapshot_position_is_rejected() -> None:
    with pytest.raises(RiskContextError, match="position symbols must match"):
        _context(signed_positions={"ES": 1.0})


def test_snapshot_position_without_signed_position_is_rejected() -> None:
    with pytest.raises(RiskContextError, match="position symbols must match"):
        _context(exposure_snapshot=_long_es_snapshot(daily_pnl=0.0, current_equity=100.0, peak_equity=100.0))


def test_different_signed_and_snapshot_quantities_are_rejected() -> None:
    with pytest.raises(RiskContextError, match="quantities must match"):
        _context(
            signed_positions={"ES": 2.0},
            exposure_snapshot=_long_es_snapshot(daily_pnl=0.0, current_equity=100.0, peak_equity=100.0),
        )


def test_snapshot_key_different_from_symbol_exposure_symbol_is_rejected() -> None:
    mismatched = _snapshot(
        positions={"ES-key": SymbolExposure(symbol="ES", quantity=1.0, avg_entry_price=100.0, mark_price=101.0)}
    )
    with pytest.raises(RiskContextError, match="key must equal"):
        _context(signed_positions={"ES-key": 1.0}, exposure_snapshot=mismatched)


def test_negative_signed_position_is_rejected_fail_closed() -> None:
    with pytest.raises(RiskContextError, match="rejects short"):
        _context(signed_positions={"ES": -1.0})


def test_zero_signed_position_absent_from_snapshot_is_accepted() -> None:
    context = _context(signed_positions={"ES": 0.0}, exposure_snapshot=_snapshot())
    assert dict(context.signed_positions) == {"ES": 0.0}
    assert dict(context.exposure_snapshot.positions) == {}


def test_coherent_long_transition_is_accepted() -> None:
    transition = _transition()
    assert transition.signed_positions["ES"] == 1.0
    assert transition.exposure_snapshot.positions["ES"].symbol == "ES"
    assert transition.exposure_snapshot.positions["ES"].quantity == 1.0


def test_coherent_commit_has_exact_journal_and_replay() -> None:
    provider, _, filled, _ = _provider_with_operations()
    replayed, journal_hash = replay_journal(provider.journal)
    assert replayed == provider.snapshot()
    assert replayed.signed_positions["ES"] == replayed.exposure_snapshot.positions["ES"].quantity
    assert journal_hash == provider.journal[-1].event_hash
    assert filled.signed_positions["ES"] == 1.0


def test_trading_day_start_preserves_positions_in_both_representations() -> None:
    _, _, filled, final = _provider_with_operations()
    assert dict(final.signed_positions) == dict(filled.signed_positions)
    assert dict(final.exposure_snapshot.positions) == dict(filled.exposure_snapshot.positions)
    assert final.signed_positions["ES"] == final.exposure_snapshot.positions["ES"].quantity


def test_non_finite_snapshot_value_is_rejected_at_context_construction() -> None:
    non_finite_snapshot = ExposureSnapshot.model_construct(
        positions={"ES": SymbolExposure.model_construct(symbol="ES", quantity=float("nan"), avg_entry_price=100.0, mark_price=101.0)},
        realized_pnl_total=0.0,
        daily_pnl=0.0,
        initial_equity=100.0,
        peak_equity=100.0,
    )
    with pytest.raises(RiskContextError):
        _context(signed_positions={"ES": 1.0}, exposure_snapshot=non_finite_snapshot)


def test_non_finite_risk_limits_are_rejected_at_context_construction() -> None:
    non_finite_limits = RiskLimits.model_construct(max_position_size=float("inf"))
    with pytest.raises(RiskContextError):
        _context(risk_limits=non_finite_limits)


def test_position_validation_failures_leave_provider_context_and_journal_unchanged() -> None:
    provider = InMemoryRiskContextProvider(_context())
    before = (provider.snapshot(), provider.journal)
    invalid = _transition()
    object.__setattr__(invalid, "signed_positions", {"ES": -1.0})
    with pytest.raises(RiskContextError):
        provider.commit_fill(before[0].state_version, before[0].state_hash, invalid)
    assert (provider.snapshot(), provider.journal) == before
