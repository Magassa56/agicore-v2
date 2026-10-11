"""Canonical recovery evidence only; no strategy imports or market-file access."""

import ast
import hashlib
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/evidence"
PREFIX = "EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_"
FAILURE_SHA = "6ac29d1c3703891726d882c3b128925c2232bd3d14e73d69ad24dd8be4d0544e"
PROTOCOL_SHA = "a0588f0df41f409456330553de5fb9720bce4297676b0bc85137edd64ebd6db4"
RECEIPT_SHA = "ef0330ff0fa4f3116ab6b39ac736d7211cd39235904262696b1f55fea04e3574"
RUN_ID = "d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4"
RUNNER_SHA = "c25000d5c180cceb0ed54fa12b5654c608936ae0c817b15e78fd9533e0467f92"
FROZEN_DOCUMENTS = {
    "EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json": (
        "strategy_manifest_sha256",
        "965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a",
    ),
    "EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.json": (
        "development_protocol_sha256",
        "68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402",
    ),
    "EMA_PULLBACK_V2_DEVELOPMENT_DATASET_LINEAGE.json": (
        "dataset_lineage_manifest_sha256",
        "d9a5d15a8746491391ba13417a099801ba6add44be1f275d2ca9e699adf56b89",
    ),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(document):
    return (
        json.dumps(
            document, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
        )
        + "\n"
    ).encode("utf-8")


def load(suffix):
    return json.loads((EVIDENCE / (PREFIX + suffix)).read_bytes())


@pytest.mark.parametrize(
    "suffix,expected",
    [("FAILED_ORIGINAL_EXECUTION", FAILURE_SHA), ("RECOVERY_PROTOCOL", PROTOCOL_SHA)],
)
def test_canonical_bytes_and_published_hashes(suffix, expected):
    raw = (EVIDENCE / (PREFIX + suffix + ".json")).read_bytes()
    assert raw == canonical(json.loads(raw))
    assert sha(raw) == expected
    assert expected in (EVIDENCE / (PREFIX + suffix + ".md")).read_text()
    assert expected in (ROOT / "AGICORE_CURRENT_STATE.md").read_text()


@pytest.mark.parametrize("filename", FROZEN_DOCUMENTS)
def test_both_evidence_documents_bind_unchanged_frozen_metadata(filename):
    field, expected = FROZEN_DOCUMENTS[filename]
    assert sha((EVIDENCE / filename).read_bytes()) == expected
    for suffix in ("FAILED_ORIGINAL_EXECUTION.json", "RECOVERY_PROTOCOL.json"):
        assert load(suffix)["frozen_bindings"][field] == expected


def test_failure_receipt_is_preserved_exactly_and_cross_bound():
    raw = (EVIDENCE / (PREFIX + "ORIGINAL_START_RECEIPT.json")).read_bytes()
    assert sha(raw) == RECEIPT_SHA
    receipt = json.loads(raw)
    failure = load("FAILED_ORIGINAL_EXECUTION.json")
    copied = failure["execution_start_receipt"]
    assert copied["sha256"] == RECEIPT_SHA
    assert copied["size_bytes"] == len(raw)
    assert (ROOT / copied["preserved_copy_path"]).read_bytes() == raw
    assert copied["copy_semantics"] == "EXACT_BYTES_NO_RESERIALIZATION"
    assert receipt["registered_run_id_sha256"] == RUN_ID
    assert receipt["execution_started_at_utc"] == failure["execution_start_utc"]
    assert receipt["output_path"] == failure["original_result"]["expected_path"]
    assert receipt["claim_path"] == failure["original_claim"]["path"]
    assert receipt["attempt_number"] == 1
    assert receipt["automatic_retry"] is False


def test_claim_binding_needs_no_operational_claim_or_raw_in_ci():
    failure = load("FAILED_ORIGINAL_EXECUTION.json")
    registration = load("IMPLEMENTATION.json")
    expected_claim_bytes = canonical(registration["run_identity"])
    claim = failure["original_claim"]
    assert sha(expected_claim_bytes) == claim["sha256"] == RUN_ID
    assert len(expected_claim_bytes) == claim["size_bytes"] == 371
    assert claim["git_tracking"] == "FORBIDDEN"
    assert claim["preservation"] == "IMMUTABLE_AT_EXISTING_PATH"
    assert failure["original_strategy_invocation_count"] == 1
    assert failure["original_run_claim_status"] == "CLAIMED"
    assert failure["original_run_result_status"] == "FAILED_NO_RESULT"
    assert failure["original_run_verdict_status"] == "NOT_AVAILABLE"


def test_failure_does_not_invent_progress_or_zero_performance():
    failure = load("FAILED_ORIGINAL_EXECUTION.json")
    assert failure["real_development_execution_progress"] == "UNKNOWN_AFTER_CLAIM"
    assert failure["real_performance_exposure"] == "NONE_FOUND_NOT_PROVEN_IMPOSSIBLE"
    assert failure["real_strategy_replay"] == "ORIGINAL_INVOKED_ONCE_NO_RESULT"
    assert failure["performance_values_found"] is False
    assert failure["root_cause"] == failure["termination_utc"] == "UNKNOWN"
    assert failure["forensic_termination_classification"] == "WORK_SESSION_LOST"
    assert failure["original_process_active"] is False
    assert failure["original_result"]["exists"] is False
    assert failure["original_result"]["result_sha256"] is None
    assert failure["execution_milestones"]["CLAIM_CREATED"] == "YES"
    assert failure["execution_milestones"]["REGISTRATION_VERIFIED"] == "YES"
    for step, status in failure["execution_milestones"].items():
        if step not in {"CLAIM_CREATED", "REGISTRATION_VERIFIED"}:
            assert status == "UNKNOWN"
    for field in ("real_trade_count", "real_pnl", "development_verdict"):
        assert failure[field] == "NOT_AVAILABLE"
    assert failure["oos_accessed"] is failure["second_execution_authorized"] is False


def test_recovery_exception_keeps_once_limit_and_failed_original_provenance():
    protocol = load("RECOVERY_PROTOCOL.json")
    failure = load("FAILED_ORIGINAL_EXECUTION.json")
    bound = protocol["original_failure_evidence"]
    assert sha((ROOT / bound["path"]).read_bytes()) == bound["sha256"] == FAILURE_SHA
    assert protocol["frozen_bindings"] == failure["frozen_bindings"]
    assert bound["original_failed_run_id_sha256"] == RUN_ID
    assert bound["original_claim_sha256"] == RUN_ID
    assert bound["original_start_receipt_sha256"] == RECEIPT_SHA
    governance = protocol["governance_exception"]
    assert governance["base_protocol_original_execution_limit"] == "ONCE"
    assert governance["base_protocol_reinterpreted_or_modified"] is False
    assert governance["original_attempt_consumed"] is True
    assert governance["recovery_exception_required"] is True
    assert governance["current_total_strategy_invocations"] == 1
    assert governance["total_strategy_invocations_if_recovery_invoked"] == 2
    assert governance["original_result_count"] == 0
    assert governance["max_recovery_attempts"] == 1
    assert governance["max_authoritative_development_results"] == 1
    assert governance["original_failed_run_can_be_authoritative"] is False


def test_precommitment_cannot_register_or_authorize_a_recovery_execution():
    protocol = load("RECOVERY_PROTOCOL.json")
    gate = protocol["current_gate"]
    assert gate["second_execution_authorized"] is False
    assert gate["recovery_runner_implementation_authorized"] is False
    assert gate["recovery_claim_created"] is False
    assert gate["real_recovery_execution"] == "NOT_EXECUTED"
    identity = protocol["future_recovery_identity"]
    assert identity["recovery_run_id_sha256"] is None
    assert identity["registration_status"] == "NOT_REGISTERED_YET"
    assert set(identity["fields"]) == {
        "strategy_manifest_sha256",
        "development_protocol_sha256",
        "dataset_raw_sha256",
        "runner_source_sha256",
    }
    assert identity["fields"]["runner_source_sha256"] is None
    assert identity["fields"]["dataset_raw_sha256"] == (
        "ee6eeed4871947b1fabe3c85bf4b5b319dc0d68e86edec7d2000815e22b2a126"
    )
    assert identity["compute_only_after_runner_source_final"] is True
    assert identity["register_before_real_execution"] is True
    assert (
        "SEPARATE_EXPLICIT_AGICOREMANAGER_EXECUTION_AUTHORIZATION"
        in (protocol["required_gates_before_recovery_execution"])
    )
    assert set(protocol["prohibitions"].values()) == {"FORBIDDEN"}


def test_original_runtime_and_all_component_sources_remain_frozen():
    protocol = load("RECOVERY_PROTOCOL.json")
    policy = protocol["recovery_runner_policy"]
    assert sha((ROOT / policy["original_runner_path"]).read_bytes()) == RUNNER_SHA
    manifest = json.loads(
        (EVIDENCE / "EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json").read_bytes()
    )
    paths = {"src/agicore/trading/" + item["name"] for item in manifest["components"]}
    assert set(policy["frozen_component_paths"]) == paths
    assert len(paths) == 13
    for component in manifest["components"]:
        path = ROOT / "src/agicore/trading" / component["name"]
        assert sha(path.read_bytes()) == component["source_sha256"]
    assembly = ROOT / "src/agicore/trading/ema_pullback_regime_gated_baseline_v2.py"
    assert sha(assembly.read_bytes()) == manifest["assembly_source_sha256"]
    assert policy["requires_new_runner_source_file"] is True
    assert policy["requires_new_runner_source_sha256"] is True
    assert policy["future_runner_path"] is policy["future_runner_source_sha256"] is None


def test_semantic_normalization_never_ignores_strategy_results():
    protocol = load("RECOVERY_PROTOCOL.json")
    semantics = protocol["semantic_equivalence"]
    assert semantics["input_domain"] == "SYNTHETIC_ONLY"
    assert semantics["tolerance"] == "NONE"
    assert semantics["float_comparison"] == "FORBIDDEN"
    assert semantics["failure_status"] == "BLOCKED_SEMANTIC_EQUIVALENCE"
    assert semantics["execution_after_failed_equivalence"] == "FORBIDDEN"
    assert semantics["required_identical_fields"] == [
        "strategy_lifecycle",
        "regime_events",
        "contexts",
        "pullbacks",
        "confirmations",
        "stops",
        "risk_decisions",
        "entries",
        "exits",
        "suppressions",
        "terminal_states",
        "quantities",
        "base_fills",
        "effective_fills",
        "fees",
        "slippage",
        "closed_trade_records",
        "open_trade_records",
        "marked_equity_samples",
        "segment_attribution",
        "all_metrics",
        "failed_criteria",
        "mechanical_verdict",
        "next_gate",
    ]
    normalization = semantics["identity_normalization"]
    assert normalization["permitted_identity_fields"] == [
        "run_identity.runner_source_sha256",
        "run_id_sha256",
    ]
    assert normalization["strategy_result_fields_may_not_be_ignored"] is True
    scale = protocol["scalability"]
    assert scale["synthetic_bar_counts"] == [1000, 5000, 10000, 20000]
    assert scale["real_development_benchmarking"] == "FORBIDDEN"
    assert scale["measurements_in_current_gate"] == "NOT_RUN"


def test_distinct_recovery_claim_is_terminal_and_has_no_third_attempt():
    policy = load("RECOVERY_PROTOCOL.json")["recovery_claim_policy"]
    assert policy["distinct_from_original_claim"] is True
    assert policy["recovery_attempt"] == 1
    assert policy["recovery_claim_kind"] == "ONE_TIME_EXCLUSIVE_RECOVERY_EXECUTION_CLAIM"
    assert policy["must_be_created_before_real_recovery_data_processing"] is True
    assert policy["deletion_after_creation"] == policy["automatic_retry"] == "FORBIDDEN"
    assert policy["third_execution_authorized"] is False
    assert (
        policy["after_consumed_recovery_failure"] == "STOP_AND_RETURN_TO_AGICOREMANAGER_GOVERNANCE"
    )


def test_current_state_supersedes_historical_not_executed_snapshot():
    state = (ROOT / "AGICORE_CURRENT_STATE.md").read_text()
    current = state.split("## Acquis vérifiés", 1)[0]
    assert "REAL_STRATEGY_REPLAY = ORIGINAL_INVOKED_ONCE_NO_RESULT" in current
    assert "REAL_STRATEGY_REPLAY = NOT_EXECUTED" not in current
    assert "TRUE_DURING_FAILED_ORIGINAL_INVOCATION_PROGRESS_UNKNOWN" in current
    assert "REAL_TRADE_COUNT = NOT_AVAILABLE" in current
    assert "REAL_PNL = NOT_AVAILABLE" in current
    assert "DEVELOPMENT_VERDICT = NOT_AVAILABLE" in current
    assert "ORIGINAL_EXECUTION_CLAIM = PRESERVED" in current
    assert "RECOVERY_PROTOCOL = PASS_PRECOMMITTED" in current
    addendum = json.loads((EVIDENCE / (ADDENDUM + ".json")).read_bytes())
    assert "NEXT = " + addendum["outcome"]["next"] in current
    assert "RECOVERY_IMPLEMENTATION = BLOCKED_PENDING_NEW_IMPLEMENTATION" in current


ADDENDUM = "EMA_PULLBACK_V2_RECOVERY_ARCHITECTURE_ADDENDUM_V1"
ADDENDUM_SHA = "b36c1631308ea746a66d0c2312ad50796725957eef0e9e60d52a26c771bd3cc8"
BLOCKED_IMPLEMENTATION_SHA = "4b86ad9ce46a6f033447a79e393c4dfbc92bd7af78df725786d415cc969a954d"
NEXT_ENGINE = "EMA_PULLBACK_V2_RECOVERY_OPTIMIZED_ENGINE_IMPLEMENTATION_REQUIRED"


def architecture_addendum():
    """Read only documentary evidence, without importing any trading runtime."""
    return json.loads((EVIDENCE / (ADDENDUM + ".json")).read_bytes())


def assert_addendum_contract(document):
    """Audit precommitment boundaries; this test helper grants no execution authority."""
    assert document["schema"] == document["addendum_id"] == ADDENDUM
    assert type(document["version"]) is int and document["version"] == 1
    assert document["status"] == "PASS_PRECOMMITTED"
    parent = document["parent_protocol"]
    assert parent["sha256"] == PROTOCOL_SHA and parent["bytes_changed"] is False
    assert (
        parent["compatibility"]
        == "EXPLICIT_FORMALLY_RECORDED_EXCEPTION_REQUIRED_AND_PRECOMMITTED_HERE"
    )
    assert parent["exception_targets"] == [
        "recovery_runner_policy.allowed_replacement_scope",
        "scalability.scope",
    ]
    assert document["frozen_bindings"] == load("RECOVERY_PROTOCOL.json")["frozen_bindings"]
    authority = document["authorization"]
    assert authority["new_runtime_implementation_authorized"] is False
    assert authority["real_execution_authorized"] is False
    security = document["security"]
    for field, expected in {
        "original_strategy_invocation_count": 1,
        "max_recovery_attempts": 1,
        "recovery_invocation_count": 0,
    }.items():
        assert type(security[field]) is int and security[field] == expected
    for field in (
        "recovery_claim_created",
        "second_execution_authorized",
        "execution_authorization_created",
        "real_development_data_accessed_in_this_gate",
        "oos_accessed",
        "broker_accessed",
    ):
        assert security[field] is False
    assert security["original_claim"] == "IMMUTABLE_UNTRACKED_UNCHANGED"
    assert security["original_run_result_status"] == "FAILED_NO_RESULT"
    assert security["original_progress"] == "UNKNOWN_AFTER_CLAIM"
    assert security["original_failure_cause"] == "UNKNOWN"
    assert security["recovery_run_id_status"] == "NOT_REGISTERED"
    assert security["real_recovery_execution"] == "NOT_EXECUTED"
    assert security["development_verdict"] == "NOT_AVAILABLE"
    outcome = document["outcome"]
    assert outcome["new_runtime_created"] is False
    assert outcome["new_runtime_source_sha256"] is outcome["recovery_run_id_sha256"] is None
    assert outcome["new_runtime_equivalence"] == "NOT_PROVEN"
    assert outcome["new_runtime_scalability"] == "NOT_RUN"
    assert outcome["recovery_implementation"] == "BLOCKED_PENDING_NEW_IMPLEMENTATION"
    assert outcome["real_execution_still_forbidden"] is True
    assert outcome["next"] == NEXT_ENGINE
    equivalents = document["equivalence_plan"]
    assert equivalents["input_domain"] == "INVENTED_SYNTHETIC_ONLY"
    assert equivalents["tolerance"] == "NONE"
    assert equivalents["proof_layers"] == [
        "A_FORMULA_INDUCTION",
        "B_EXACT_PREDICATE_AND_INVALID_INPUT_EQUALITY",
        "C_COMPLETE_IMMUTABLE_RESULT_EQUALITY",
        "D_LONG_STREAM_COMPUTATION_FEASIBILITY",
        "E_COMPLETE_NATIVE_EVIDENCE_SERIALIZATION_FEASIBILITY",
    ]
    normalization = equivalents["identity_normalization"]
    assert normalization["permitted_identity_fields"] == [
        "run_identity.runner_source_sha256",
        "run_id_sha256",
    ]
    assert normalization["strategy_fields_ignored"] == []
    assert normalization["pre_normalization_hash_verification"] == "REQUIRED_FOR_BOTH_OUTPUTS"
    assert normalization["derived_hash_field"] == "output_sha256"
    scale = document["scalability_plan"]
    assert scale["status"] == "PRECOMMITTED_FUTURE_TESTS_ONLY_NOT_RUN"
    assert scale["synthetic_observation_counts"] == [1000, 5000, 10000, 20000]
    assert scale["real_dataset_benchmark"] == "FORBIDDEN"
    assert scale["fresh_processes_per_family_and_size"] == 2
    assert set(scale["families"]) == {
        "CONSTANT_CONTROL",
        "ONE_TICK_PULSE_THEN_CONSTANT",
        "NONCONSTANT_TICK_GRID_DRIFT_AND_OSCILLATION",
        "DENSE_LIFECYCLE_LONG_SHORT_WITH_GAPS_AND_OFF_SESSION_DATA",
    }
    assert scale["bounded_execution"]["wall_clock_deadline_seconds"] == {
        "1000": 120,
        "5000": 600,
        "10000": 1800,
        "20000": 3600,
    }
    assert scale["bounded_execution"]["peak_memory_cap_bytes"] == 4 * 1024**3
    assert scale["bounded_execution"]["output_size_cap_bytes"] == 8 * 1024**3
    assert document["cost_analysis"]["not_an_original_crash_diagnosis"] is True


def test_addendum_canonical_hash_and_independent_gate_contract():
    """Require the versioned document's exact published bytes and deny boundaries."""
    raw = (EVIDENCE / (ADDENDUM + ".json")).read_bytes()
    assert raw == canonical(architecture_addendum())
    assert sha(raw) == ADDENDUM_SHA
    assert ADDENDUM_SHA in (EVIDENCE / (ADDENDUM + ".md")).read_text()
    assert ADDENDUM_SHA in (ROOT / "AGICORE_CURRENT_STATE.md").read_text()
    assert_addendum_contract(architecture_addendum())


@pytest.mark.parametrize(
    "path,value",
    [
        ("version", True),
        ("parent_protocol.sha256", "0" * 64),
        ("parent_protocol.bytes_changed", True),
        ("parent_protocol.compatibility", "AUTOMATICALLY_COMPATIBLE"),
        ("authorization.new_runtime_implementation_authorized", True),
        ("authorization.real_execution_authorized", True),
        ("security.original_strategy_invocation_count", 0),
        ("security.max_recovery_attempts", 2),
        ("security.recovery_invocation_count", 1),
        ("security.second_execution_authorized", True),
        ("security.recovery_claim_created", True),
        ("security.execution_authorization_created", True),
        ("security.real_development_data_accessed_in_this_gate", True),
        ("security.oos_accessed", True),
        ("security.original_progress", "REPLAY_COMPLETED"),
        ("security.original_failure_cause", "FRACTION_SLOWDOWN_PROVEN"),
        ("outcome.new_runtime_created", True),
        ("outcome.new_runtime_equivalence", "PASS"),
        ("outcome.recovery_run_id_sha256", "1" * 64),
        ("outcome.next", "REAL_RECOVERY_EXECUTION"),
        ("equivalence_plan.tolerance", "0.0001"),
        ("equivalence_plan.input_domain", "REAL_DEVELOPMENT"),
        ("equivalence_plan.identity_normalization.strategy_fields_ignored", ["metrics"]),
        ("equivalence_plan.identity_normalization.permitted_identity_fields", ["verdict"]),
        ("equivalence_plan.identity_normalization.pre_normalization_hash_verification", "SKIP"),
        ("scalability_plan.status", "PASS_MEASURED"),
        ("scalability_plan.real_dataset_benchmark", "ALLOWED"),
        ("scalability_plan.bounded_execution.peak_memory_cap_bytes", 0),
    ],
)
def test_addendum_rejects_governance_or_equivalence_drift(path, value):
    """Independently reject widened authority, lost failure provenance and approximate checks."""
    altered = deepcopy(architecture_addendum())
    parts = path.split(".")
    target = altered
    for key in parts[:-1]:
        target = target[key]
    target[parts[-1]] = value
    with pytest.raises(AssertionError):
        assert_addendum_contract(altered)


def test_addendum_preserves_blocked_snapshots_and_reference_source_closure():
    """Keep historical documents and every reference source immutable without needing RAW."""
    document = architecture_addendum()
    preserved = document["preserved_work"]
    for evidence in preserved["prior_evidence"]:
        assert sha((ROOT / evidence["path"]).read_bytes()) == evidence["sha256"]
    blocked = load("RECOVERY_IMPLEMENTATION.json")
    assert sha((EVIDENCE / (PREFIX + "RECOVERY_IMPLEMENTATION.json")).read_bytes()) == (
        BLOCKED_IMPLEMENTATION_SHA
    )
    assert blocked["status"] == "BLOCKED_ARCHITECTURE_CONFLICT"
    assert blocked["recovery_runner_source_sha256"] is None
    assert preserved["original_claim"] == blocked["original_claim"]
    assert preserved["original_claim_git_tracking"] == "FORBIDDEN"
    manifest = json.loads(
        (EVIDENCE / "EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json").read_bytes()
    )
    components = {
        "src/agicore/trading/" + c["name"]: c["source_sha256"] for c in manifest["components"]
    }
    sources = {s["path"]: s for s in document["reference_sources"]}
    assert len(sources) == len(document["reference_sources"]) == 16
    assert {
        p: s["sha256"] for p, s in sources.items() if s["role"] == "FROZEN_TRADING_COMPONENT"
    } == components
    for source in sources.values():
        assert sha((ROOT / source["path"]).read_bytes()) == source["sha256"]
    state = (ROOT / "AGICORE_CURRENT_STATE.md").read_text()
    assert "## 2026-10-11 — analyse de récupération, conflit d’interface gelée" in state
    assert "RECOVERY_RUNNER = NOT_CREATED_ARCHITECTURE_CONFLICT" in state


@pytest.mark.parametrize("evidence", architecture_addendum()["root_conflict"]["source_evidence"])
def test_architecture_source_proof_matches_actual_ast_and_hash(evidence):
    """Verify source-backed claims statically, without importing or invoking trading code."""
    raw = (ROOT / evidence["path"]).read_bytes()
    assert sha(raw) == evidence["source_sha256"]
    nodes = [
        n
        for n in ast.walk(ast.parse(raw))
        if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == evidence["symbol"]
    ]
    assert len(nodes) == 1
    node = nodes[0]
    assert (node.lineno, node.end_lineno) == (evidence["first_line"], evidence["last_line"])
    if evidence["parameters"] is not None:
        assert [
            a.arg for a in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
        ] == evidence["parameters"]


def test_exact_one_pulse_growth_is_an_algebraic_witness_not_a_benchmark():
    """Check the noncancelling rational identity independently on invented arithmetic only."""
    price = Fraction(20000)
    value = price + Fraction(1, 42)
    for step in range(129):
        expected = price + Fraction(19**step, 42 * 21**step)
        assert value == expected
        assert expected.denominator == 42 * 21**step
        value = (2 * price + 19 * value) / 21


@pytest.mark.parametrize(
    "envelope",
    architecture_addendum()["cost_analysis"]["tick_grid_denominator_envelopes"][
        "bit_length_envelopes"
    ],
)
def test_exact_symbolic_operand_envelopes_need_no_float_or_observations(envelope):
    """Confirm exact integer bounds, not a runtime or real-data performance claim."""
    index = envelope["observations"] - 1
    expected = {
        "ema20_divisor_envelope_bits": (80 * 21 ** (index - 19)).bit_length(),
        "ema12_divisor_envelope_bits": (4 * 13**index).bit_length(),
        "ema26_divisor_envelope_bits": (4 * 27**index).bit_length(),
        "macd_divisor_envelope_bits": (4 * 351**index).bit_length(),
        "signal_hist_divisor_envelope_bits": (4 * 1755**index).bit_length(),
        "one_pulse_ema20_exact_denominator_bits": (42 * 21 ** (index - 20)).bit_length(),
    }
    assert {k: v for k, v in envelope.items() if k != "observations"} == expected


def normalize_test_document(document):
    """Exercise only identity-normalization infrastructure on an invented metadata object."""
    result = deepcopy(document)
    digest = result.pop("output_sha256")
    assert sha(canonical(result)) == digest
    result["run_identity"]["runner_source_sha256"] = RUNNER_SHA
    result["run_id_sha256"] = sha(canonical(result["run_identity"]))
    result["output_sha256"] = sha(canonical(result))
    return canonical(result)


def test_normalization_verifies_both_hashes_and_cannot_hide_a_payload_difference():
    """Reject tampering before normalization and preserve any nonidentity difference."""
    registration = load("IMPLEMENTATION.json")
    first = {
        "run_identity": registration["run_identity"],
        "run_id_sha256": RUN_ID,
        "payload": ["INVENTED_METADATA_ONLY", 1],
    }
    second = deepcopy(first)
    second["run_identity"]["runner_source_sha256"] = "2" * 64
    second["run_id_sha256"] = sha(canonical(second["run_identity"]))
    for document in (first, second):
        document["output_sha256"] = sha(canonical(document))
    assert first["output_sha256"] != second["output_sha256"]
    assert normalize_test_document(first) == normalize_test_document(second)
    tampered = deepcopy(second)
    tampered["payload"][1] = 2
    with pytest.raises(AssertionError):
        normalize_test_document(tampered)
    tampered.pop("output_sha256")
    tampered["output_sha256"] = sha(canonical(tampered))
    assert normalize_test_document(tampered) != normalize_test_document(first)
