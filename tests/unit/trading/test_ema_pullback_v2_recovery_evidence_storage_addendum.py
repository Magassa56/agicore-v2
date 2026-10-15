"""Documentary governance checks only: no runner, RAW, codec or strategy calls."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / "docs/evidence"
NAME = "EMA_PULLBACK_V2_RECOVERY_EVIDENCE_STORAGE_ADDENDUM_V1"
ADDENDUM_SHA = "9f0752d90f8cec746addcb97ded86664f9739e727951d47d9a04eeb29243b019"
NEXT = "EMA_PULLBACK_V2_RECOVERY_STORAGE_SYNTHETIC_PROOF_REQUIRED"
EXPECTED_PARENTS = {
    "recovery_protocol": "a0588f0df41f409456330553de5fb9720bce4297676b0bc85137edd64ebd6db4",
    "architecture_addendum": "b36c1631308ea746a66d0c2312ad50796725957eef0e9e60d52a26c771bd3cc8",
    "development_protocol": "68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402",
    "strategy_manifest": "965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a",
    "dataset_lineage": "d9a5d15a8746491391ba13417a099801ba6add44be1f275d2ca9e699adf56b89",
    "original_failure": "6ac29d1c3703891726d882c3b128925c2232bd3d14e73d69ad24dd8be4d0544e",
    "historical_architecture_conflict": "4b86ad9ce46a6f033447a79e393c4dfbc92bd7af78df725786d415cc969a954d",
}


def canonical(value):
    """Canonical documentary JSON; this is not a recovery result serializer."""
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=False, allow_nan=False) + "\n").encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def reject_float(value):
    raise ValueError("documentary number must not be a float/nonfinite token")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate documentary key")
        result[key] = value
    return result


def decode(raw):
    return json.loads(raw, parse_float=reject_float, parse_constant=reject_float,
                      object_pairs_hook=unique_object)


def load():
    return decode((EVIDENCE / (NAME + ".json")).read_bytes())


def assert_contract(d):
    """Fail closed on broadened authority or weakened logical/native commitments."""
    assert d["schema"] == d["addendum_id"] == NAME
    assert type(d["version"]) is int and d["version"] == 1
    assert d["status"] == "PASS_PRECOMMITTED"
    assert d["selected_option"] == "B"
    auth = d["authorization"]
    assert type(auth["real_recovery_attempts_authorized"]) is int
    assert auth["real_recovery_attempts_authorized"] == 0
    for name in ("real_raw_access", "real_execution_authorized",
                 "recovery_claim_creation_authorized", "new_real_runner_implementation_authorized",
                 "storage_implementation_authorized_in_this_gate", "implementation_pr_authorized"):
        assert auth[name] is False
    assert set(d["parents"]) == set(EXPECTED_PARENTS)
    for name, digest in EXPECTED_PARENTS.items():
        assert d["parents"][name]["sha256"] == digest
        assert d["parents"][name]["bytes_changed"] is False
    layers = d["frozen_semantic_layers"]
    for name in ("original_result_schema_changed", "trading_rules_changed",
                 "screening_thresholds_changed"):
        assert layers[name] is False
    exception = d["governance_exception"]
    assert exception["status"] == "PRECOMMITTED_CONDITIONAL_NOT_ACTIVE_FOR_EXECUTION"
    assert exception["cap_interpretation_change"] is True
    for name in ("original_documents_overwritten", "logical_schema_exception",
                 "logical_omission_exception", "logical_reference_placeholders_permitted",
                 "numeric_cap_change"):
        assert exception[name] is False
    assert exception["activation_requires"] == [
        "THIS_DOCUMENTARY_PRECOMMIT_MERGED_WITH_GREEN_CI",
        "SEPARATELY_AUTHORIZED_STORAGE_SYNTHETIC_PROOF_PASS",
        "INDEPENDENT_VERIFIER_IMPLEMENTATION_AND_EXACT_EQUIVALENCE_PASS",
        "COMPLETE_RECOVERY_IMPLEMENTATION_AND_REQUIRED_RESOURCE_VALIDATION_PASS",
        "EXPLICIT_AGICOREMANAGER_ACCEPTANCE_OF_PHYSICAL_CAP_INTERPRETATION",
        "FINAL_SOURCE_CLOSURES_AND_RUN_ID_REGISTERED_IN_FUTURE_GATE",
        "EXECUTION_READINESS_PASS_AND_DISTINCT_EXPLICIT_REAL_EXECUTION_AUTHORIZATION",
    ]
    resources = d["resource_contract"]
    assert type(resources["memory_cap_bytes"]) is int
    assert resources["memory_cap_bytes"] == 4294967296
    assert type(resources["output_storage_cap_bytes"]) is int
    assert resources["output_storage_cap_bytes"] == 8589934592
    for name in ("numeric_caps_relaxed", "large_benchmarks_in_this_gate",
                 "prior_mandatory_scalability_plan_waived"):
        assert resources[name] is False
    for name in ("original_cap_applies_until_exception_activated", "no_assumed_compression_ratio",
                 "no_unmeasured_feasibility_claim"):
        assert resources[name] is True
    assert resources["resource_feasibility"] == "NOT_PROVEN"
    assert resources["new_compression_measurements"] == "NOT_RUN"
    audit = d["layer_2_complete_audit"]
    assert audit["required_streams"] == ["logical_native_result", "mark_source_witnesses"]
    assert audit["all_original_native_fields_retained"] is True
    assert audit["hashes_do_not_replace_missing_bytes"] is True
    for name in ("logical_record_deduplication", "logical_reordering", "lossy_compression"):
        assert audit[name] is False
    reconstruction = d["reconstruction_contract"]
    assert reconstruction["target"] == "ORIGINAL_COMPLETE_CANONICAL_NATIVE_JSON_BYTE_STREAM"
    assert reconstruction["tolerance"] == "NONE"
    assert reconstruction["identity_normalization_during_storage_roundtrip"] == []
    assert reconstruction["field_omissions"] == []
    assert reconstruction["numerical_normalization_or_rounding"] is False
    assert reconstruction["symbolic_native_placeholders"] is False
    assert reconstruction["complete_stream_reconstruction_required"] is True
    assert reconstruction["monolithic_expanded_file_required"] is False
    assert reconstruction["acyclic_commitment_order"] == [
        "objects", "bundle_manifest", "decision_summary",
        "independent_verification_receipt", "completion_seal",
    ]
    storage = d["physical_storage_contract"]
    assert storage["chunk_uncompressed_bytes"] == 1048576
    assert storage["manifest_chunk_order"] == "CONTIGUOUS_ORDINAL_AND_BYTE_OFFSET"
    codec = storage["compression"]
    assert (codec["algorithm"], codec["level"], codec["window_bits"], codec["memory_level"],
            codec["strategy"], codec["metadata_headers"]) == (
        "RAW_DEFLATE", 9, -15, 8, "Z_DEFAULT_STRATEGY", "NONE",
    )
    assert codec["fallback"] == (
        "IDENTITY_IF_COMPRESSED_LENGTH_GREATER_THAN_OR_EQUAL_TO_UNCOMPRESSED_LENGTH"
    )
    assert codec["compression_ratio_guaranteed"] is False
    verifier = d["independent_verifier"]
    assert verifier["implementation_status"] == "FUTURE_GATE_NOT_IMPLEMENTED_HERE"
    assert verifier["separate_from_strategy_engine"] is True
    assert verifier["strategy_execution_or_signal_recomputation"] is False
    assert verifier["trusted_summary_metrics"] is False
    summary = d["layer_1_decision_summary"]
    assert summary["status_now"] == "SPECIFICATION_ONLY_NO_RESULT_VALUES"
    assert summary["cannot_be_used_alone_for_screening_or_validation_authorization"] is True
    proof = d["synthetic_proof_plan"]
    assert proof["status"] == "NOT_RUN_IN_THIS_DOCUMENTARY_GATE"
    assert proof["implementation_status"] == "NOT_IMPLEMENTED"
    assert proof["input_domain"] == "INVENTED_SYNTHETIC_ONLY"
    assert proof["failure_status"] == "BLOCKED_STORAGE_CONTRACT_EQUIVALENCE"
    assert proof["no_omitted_failures"] is True
    assert proof["passing_small_fixtures_proves_89841_feasibility"] is False
    future = d["future_execution_identity"]
    assert future["recovery_run_id"] is None
    assert future["registration_status"] == "NOT_REGISTERED"
    assert future["max_recovery_invocations"] == 1
    assert future["existing_parent_authorization_bindings_still_required"] is True
    for name in ("real_authorization_artifact_created", "recovery_claim_created",
                 "automatic_retry_or_resume"):
        assert future[name] is False
    outcome = d["security_and_outcome"]
    assert outcome["complete_recovery_implementation"] == "BLOCKED_TECHNICAL_FEASIBILITY"
    assert outcome["original_invocations"] == 1 and type(outcome["original_invocations"]) is int
    assert outcome["recovery_invocations"] == 0 and type(outcome["recovery_invocations"]) is int
    assert outcome["original_run_result_status"] == "FAILED_NO_RESULT"
    assert outcome["original_run_verdict_status"] == "NOT_AVAILABLE"
    assert outcome["original_failure_cause"] == "UNKNOWN"
    assert outcome["recovery_run_id"] == "NOT_REGISTERED"
    assert outcome["real_recovery_execution"] == "NOT_EXECUTED"
    assert outcome["development_verdict"] == "NOT_AVAILABLE"
    assert outcome["next"] == NEXT
    for name in ("real_development_data_accessed_this_gate", "oos_accessed", "broker_accessed",
                 "next_gate_started_automatically"):
        assert outcome[name] is False
    assert d["scientific_integrity"]["original_failed_attempt_reclassified_successful"] is False
    assert d["scientific_integrity"]["performance_result_used_to_select_contract"] is False


def test_canonical_document_hash_and_publication():
    raw = (EVIDENCE / (NAME + ".json")).read_bytes()
    assert raw == canonical(load())
    assert sha(raw) == ADDENDUM_SHA
    assert ADDENDUM_SHA in (EVIDENCE / (NAME + ".md")).read_text()
    state = (ROOT / "AGICORE_CURRENT_STATE.md").read_text()
    assert ADDENDUM_SHA in state
    assert "COMPLETE_RECOVERY_IMPLEMENTATION = BLOCKED_TECHNICAL_FEASIBILITY" in state
    assert "RECOVERY_RUN_ID = NOT_REGISTERED" in state
    assert "NEXT = " + NEXT in state
    assert_contract(load())


def test_frozen_sources_and_authority_documents_unchanged_without_raw_access():
    d = load()
    for binding in d["parents"].values():
        assert sha((ROOT / binding["path"]).read_bytes()) == binding["sha256"]
    assert len(d["reference_sources"]) == 16
    for source in d["reference_sources"]:
        assert sha((ROOT / source["path"]).read_bytes()) == source["sha256"]


def test_complete_logical_projection_matches_frozen_schema_and_metric_contracts():
    d = load()
    protocol = decode((ROOT / d["parents"]["development_protocol"]["path"]).read_bytes())
    layers = d["frozen_semantic_layers"]
    for name, digest in layers["authority_subdocument_sha256"].items():
        assert sha(canonical(protocol[name])) == digest
    schema = protocol["result_schema"]
    assert layers["required_native_fields"] == schema["required"]
    assert layers["required_lifecycle_fields"] == (
        schema["properties"]["immutable_lifecycle_records"]["required"]
    )
    detailed_arrays = {"closed_trade_records", "open_trade_records", "marked_equity_samples",
                       "immutable_lifecycle_records", "diagnostic_trades_per_trading_day_session"}
    summary = d["layer_1_decision_summary"]
    assert summary["native_projection_fields"] == [
        name for name in schema["required"] if name not in detailed_arrays
    ]
    assert summary["metric_coverage"] == schema["properties"]["metrics"]["required"]
    assert set(summary["native_projection_fields"]) | detailed_arrays == set(schema["required"])
    assert d["future_execution_identity"]["four_field_run_identity"] == (
        protocol["future_replay_contract"]["run_identity_fields"]
    )


def test_preservation_inventory_claim_exclusion_and_historical_limitations():
    d = load()
    p = d["preserved_work"]
    assert p["local_wip_commit"] == "273579e3643de5bce6d66f75524b3179972d3acc"
    assert p["published_wip_commit"] == "f40445911d3b8c8599c0228d1342fdba0a4aecff"
    assert p["identical_git_tree_sha"] == "9283af6eeb9458913681cd1b615f82baf87ff5f4"
    assert p["remote_published"] is True
    assert p["implementation_pr_created"] is False
    assert p["preservation_commit_is_not_implementation_approval"] is True
    assert p["complete_full_suite"] == "NOT_CERTIFIED"
    assert p["completed_native_comparisons"] == 126
    assert p["distinct_native_cases"] == 63
    assert p["focused_invalid_input_tests_passed"] == 22
    assert len(p["inventory"]) == 21
    assert len({e["path"] for e in p["inventory"]}) == 21
    assert sum(e["commit_inclusion"] for e in p["inventory"]) == 20
    assert sha(canonical(p["inventory"])) == p["inventory_sha256"]
    excluded = [e for e in p["inventory"] if not e["commit_inclusion"]]
    claim = p["original_claim"]
    assert [e["path"] for e in excluded] == [claim["path"]]
    assert claim["sha256"] == (
        "d2eb78fb5a1b97e71fcc323b71da216449b35e4298729a26d6d052f4f26f00f4"
    )
    assert claim["size_bytes"] == 371
    assert claim["preserved"] is True
    assert claim["git_tracked"] is claim["copied_to_documentary_worktree"] is False
    # Verify documentary commitments without reading an actual execution claim.
    recheck = p["preservation_recheck"]
    assert recheck["status"] == "PRESERVED_EXACT_DURABLE_COPY_VERIFIED"
    assert recheck["all_21_wip_inventory_files_unchanged"] is True
    assert recheck["original_claim_unchanged"] is True
    assert recheck["historical_archives_regenerated"] is False
    assert recheck["existing_files_overwritten"] is False
    assert recheck["local_incomplete_file_preserved_unchanged"] is True
    assert recheck["local_truncation_origin"] == "UNKNOWN"
    assert recheck["local_incomplete_bytes_are_exact_prefix"] is True
    original = p["existing_external_proofs"][0]
    complete = recheck["verified_complete_archive"]
    partial = recheck["local_incomplete_archive"]
    assert (complete["sha256"], complete["size_bytes"]) == (
        original["sha256"], original["size_bytes"],
    )
    assert partial["path"] != complete["path"]
    assert partial["sha256"] != complete["sha256"]
    assert partial["size_bytes"] < complete["size_bytes"]


def test_manifest_has_ordered_complete_shards_and_distinct_acyclic_hashes():
    d = load()
    s = d["physical_storage_contract"]
    assert s["chunk_fields"] == [
        "ordinal", "uncompressed_offset", "uncompressed_size_bytes", "uncompressed_sha256",
        "codec", "stored_size_bytes", "stored_sha256",
    ]
    assert s["stream_fields"] == [
        "stream_id", "uncompressed_size_bytes", "uncompressed_sha256", "chunk_count", "chunks",
    ]
    assert "summary_sha256" not in s["manifest_fields"]
    assert "bundle_manifest_sha256" not in s["manifest_fields"]
    hashes = d["reconstruction_contract"]["hash_distinction"]
    assert set(hashes) == {"native_output_sha256", "logical_native_file_sha256",
                           "bundle_manifest_sha256", "summary_sha256"}
    assert "omitted" in hashes["native_output_sha256"]
    assert "INCLUDING" in hashes["logical_native_file_sha256"]
    assert "ordinal" in s["integrity"] or "positions" in s["integrity"]
    assert len(d["synthetic_proof_plan"]["tamper_tests"]) >= 20
    witnesses = d["layer_2_complete_audit"]["mark_source_witnesses"]
    assert "raw_close_text" in witnesses["fields"]
    assert "source_row_sha256" in witnesses["fields"]
    assert witnesses["real_input_access_in_this_gate"] is False
    assert "INCOMPLETE" in witnesses["source_verification"]


@pytest.mark.parametrize("raw", [b'{"x":1,"x":2}', b'{"x":1.5}', b'{"x":NaN}'])
def test_documentary_decoder_rejects_ambiguous_or_inexact_metadata(raw):
    with pytest.raises(ValueError):
        decode(raw)


@pytest.mark.parametrize("path,value", [
    ("version", True),
    ("selected_option", "C"),
    ("authorization.real_recovery_attempts_authorized", 1),
    ("authorization.real_raw_access", True),
    ("authorization.real_execution_authorized", True),
    ("authorization.recovery_claim_creation_authorized", True),
    ("authorization.new_real_runner_implementation_authorized", True),
    ("authorization.implementation_pr_authorized", True),
    ("parents.development_protocol.sha256", "0" * 64),
    ("parents.architecture_addendum.bytes_changed", True),
    ("frozen_semantic_layers.original_result_schema_changed", True),
    ("frozen_semantic_layers.trading_rules_changed", True),
    ("frozen_semantic_layers.screening_thresholds_changed", True),
    ("governance_exception.status", "ACTIVE_FOR_REAL_EXECUTION"),
    ("governance_exception.cap_interpretation_change", False),
    ("governance_exception.activation_requires", []),
    ("governance_exception.logical_omission_exception", True),
    ("resource_contract.memory_cap_bytes", 8589934592),
    ("resource_contract.output_storage_cap_bytes", 68719476736),
    ("resource_contract.numeric_caps_relaxed", True),
    ("resource_contract.original_cap_applies_until_exception_activated", False),
    ("resource_contract.prior_mandatory_scalability_plan_waived", True),
    ("resource_contract.resource_feasibility", "PASS"),
    ("resource_contract.new_compression_measurements", "PASS"),
    ("layer_2_complete_audit.required_streams", ["summary_only"]),
    ("layer_2_complete_audit.hashes_do_not_replace_missing_bytes", False),
    ("layer_2_complete_audit.logical_record_deduplication", True),
    ("layer_2_complete_audit.logical_reordering", True),
    ("layer_2_complete_audit.lossy_compression", True),
    ("reconstruction_contract.tolerance", "0.0001"),
    ("reconstruction_contract.identity_normalization_during_storage_roundtrip", ["run_id_sha256"]),
    ("reconstruction_contract.field_omissions", ["immutable_lifecycle_records"]),
    ("reconstruction_contract.symbolic_native_placeholders", True),
    ("reconstruction_contract.complete_stream_reconstruction_required", False),
    ("reconstruction_contract.acyclic_commitment_order", ["summary", "manifest", "summary"]),
    ("physical_storage_contract.chunk_uncompressed_bytes", 0),
    ("physical_storage_contract.manifest_chunk_order", "UNORDERED"),
    ("physical_storage_contract.compression.compression_ratio_guaranteed", True),
    ("independent_verifier.trusted_summary_metrics", True),
    ("independent_verifier.separate_from_strategy_engine", False),
    ("layer_1_decision_summary.cannot_be_used_alone_for_screening_or_validation_authorization", False),
    ("synthetic_proof_plan.status", "PASS"),
    ("synthetic_proof_plan.input_domain", "REAL_DEVELOPMENT"),
    ("synthetic_proof_plan.no_omitted_failures", False),
    ("synthetic_proof_plan.passing_small_fixtures_proves_89841_feasibility", True),
    ("future_execution_identity.recovery_run_id", "1" * 64),
    ("future_execution_identity.recovery_claim_created", True),
    ("future_execution_identity.automatic_retry_or_resume", True),
    ("future_execution_identity.max_recovery_invocations", 2),
    ("security_and_outcome.original_run_result_status", "COMPLETED"),
    ("security_and_outcome.original_failure_cause", "FRACTION_SLOWDOWN_PROVEN"),
    ("security_and_outcome.complete_recovery_implementation", "PASS"),
    ("security_and_outcome.recovery_invocations", 1),
    ("security_and_outcome.oos_accessed", True),
    ("security_and_outcome.next", "REAL_RECOVERY_EXECUTION"),
    ("scientific_integrity.performance_result_used_to_select_contract", True),
])
def test_contract_rejects_authority_evidence_or_resource_drift(path, value):
    altered = deepcopy(load())
    parts = path.split(".")
    target = altered
    for key in parts[:-1]:
        target = target[key]
    target[parts[-1]] = value
    with pytest.raises(AssertionError):
        assert_contract(altered)
