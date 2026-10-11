"""Canonical recovery evidence only; no strategy imports or market-file access."""

import hashlib
import json
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
    assert "NEXT = EMA_PULLBACK_V2_DEVELOPMENT_REPLAY_RECOVERY_IMPLEMENTATION_REQUIRED" in current
