"""Non-worker preflight for the versioned repaired storage harness binding."""

from __future__ import annotations

import ast
import copy
from pathlib import Path

import pytest

from agicore.trading.ema_pullback_v2_storage_format import (
    ROOT,
    StorageProofError,
    canonical,
    codec_profile,
    parse_canonical,
    sha,
)
from tools.ema_pullback_v2_storage_synthetic_proof import verify_registration


NEW_RELATIVE = (
    "docs/evidence/"
    "EMA_PULLBACK_V2_RECOVERY_STORAGE_HARNESS_BINDING_SOURCE_REGISTRATION_V1.json"
)
HISTORICAL_RELATIVE = (
    "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_SOURCE_REGISTRATION_V1.json"
)
PARSER_REPAIR_RELATIVE = (
    "docs/evidence/"
    "EMA_PULLBACK_V2_RECOVERY_STORAGE_PARSER_TARGETED_REPAIR_"
    "SOURCE_REGISTRATION_V1.json"
)
PLAN_RELATIVE = (
    "docs/evidence/"
    "EMA_PULLBACK_V2_RECOVERY_STORAGE_HARNESS_BINDING_REPAIR_"
    "PREFLIGHT_PLAN_V1.json"
)
HARNESS_RELATIVE = "tests/unit/trading/test_ema_pullback_v2_recovery_storage.py"
PREFLIGHT_RELATIVE = (
    "tests/unit/trading/"
    "test_ema_pullback_v2_recovery_storage_registration_v1.py"
)
WORKER_RELATIVE = "tools/ema_pullback_v2_storage_synthetic_proof.py"
FIXTURE_RELATIVE = (
    "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_FIXTURE_REGISTRATION_V1.json"
)

NEW_REGISTRATION = ROOT / NEW_RELATIVE
HISTORICAL_REGISTRATION = ROOT / HISTORICAL_RELATIVE
PARSER_REPAIR_REGISTRATION = ROOT / PARSER_REPAIR_RELATIVE
PLAN = ROOT / PLAN_RELATIVE
HARNESS = ROOT / HARNESS_RELATIVE
PREFLIGHT = ROOT / PREFLIGHT_RELATIVE
WORKER = ROOT / WORKER_RELATIVE
FIXTURE_REGISTRATION = ROOT / FIXTURE_RELATIVE

EXPECTED_FIXTURE_SHA256 = (
    "60038227f5b57bf777149fad00e37ce764fc77169c5d26443aeeda664b98a714"
)
EXPECTED_PRODUCER_SHA256 = (
    "bbfc658310f27af6a03b34e8771205af84843b97315266098f21725ebfec03d3"
)
EXPECTED_VERIFIER_SHA256 = (
    "9e04e9da8eef04eddaa0c7db53bca6831570416955b5d2c518d6d26a991a1da8"
)
EXPECTED_CODEC_PROFILE_SHA256 = (
    "9635d59d40eb747225a4c89c82302b0cbd87f38e337e3b6296039c70f139ce30"
)
EXPECTED_HISTORICAL_REGISTRATION_SHA256 = (
    "cb8650fa6997f021fc678b5cd28814472c4145b075572b7b06fae8876aa8d32c"
)
EXPECTED_PARSER_REPAIR_REGISTRATION_SHA256 = (
    "accd0fbe1501ae272cb7959930f9278ed3733b2c0277f9ebe9d3e6aa32db78cf"
)
PROHIBITED_CALLS = {
    "byte_case",
    "evaluate_synthetic_development_replay_v2",
    "execute_registered_development_replay_v2",
    "native_case",
    "statistics_cases",
    "tamper_case",
}


def registration() -> dict:
    """Load only the canonical registration document, without executing cases."""
    return parse_canonical([NEW_REGISTRATION.read_bytes()])


def closure_entry(document: dict, path: str) -> dict:
    """Return one exact source entry from the registered complete closure."""
    return next(
        item for item in document["complete_source_closure"]["files"] if item["path"] == path
    )


def assignment_strings(path: Path, target_name: str) -> list[str]:
    """Read a module assignment statically; importing the worker harness is forbidden."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for statement in tree.body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
            continue
        targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target]
        if not any(isinstance(target, ast.Name) and target.id == target_name for target in targets):
            continue
        value = statement.value
        return [
            node.value
            for node in ast.walk(value)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        ]
    raise AssertionError(f"missing assignment: {target_name}")


def called_names(path: Path) -> set[str]:
    """Collect statically visible calls without importing or running the module."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    result = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            result.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            result.add(node.func.attr)
    return result


def test_a_registration_exists_and_is_preflight_only():
    document = registration()
    assert document["schema"] == (
        "agicore:synthetic-storage-harness-binding-source-registration:v1"
    )
    assert document["harness_binding_repair_only"] is True
    assert document["non_worker_preflight_authorized"] is True
    assert document["automatic_worker_execution_authorized"] is False
    assert document["full_suite_authorized"] is False


def test_b_k_harness_resolves_only_to_new_registration():
    assert assignment_strings(HARNESS, "SOURCE_REGISTRATION") == [NEW_RELATIVE]
    harness_bytes = HARNESS.read_bytes()
    assert NEW_RELATIVE.encode("utf-8") in harness_bytes
    assert HISTORICAL_RELATIVE.encode("utf-8") not in harness_bytes
    assert PARSER_REPAIR_RELATIVE.encode("utf-8") not in harness_bytes


def test_c_future_controller_selection_is_explicit():
    document = registration()
    binding = document["future_worker_registration_binding"]
    assert binding["registration_path"] == NEW_RELATIVE
    assert binding["registration_argument"] == "--registration"
    source = WORKER.read_text(encoding="utf-8")
    assert 'parser.add_argument("--registration", type=Path, required=True)' in source
    assert "verify_registration(args.registration, formal=args.formal)" in source


def test_d_fixture_registration_is_unchanged():
    document = registration()
    assert sha(FIXTURE_REGISTRATION.read_bytes()) == EXPECTED_FIXTURE_SHA256
    assert document["fixture_registration_sha256"] == EXPECTED_FIXTURE_SHA256


def test_e_f_g_complete_closure_and_repaired_sources_match():
    document, _ = verify_registration(NEW_REGISTRATION, formal=False)
    producer = closure_entry(
        document, "src/agicore/trading/ema_pullback_v2_recovery_storage.py"
    )
    verifier = closure_entry(
        document, "src/agicore/trading/ema_pullback_v2_recovery_storage_verifier.py"
    )
    assert producer["sha256"] == EXPECTED_PRODUCER_SHA256
    assert verifier["sha256"] == EXPECTED_VERIFIER_SHA256
    assert sha((ROOT / producer["path"]).read_bytes()) == producer["sha256"]
    assert sha((ROOT / verifier["path"]).read_bytes()) == verifier["sha256"]


def test_h_independent_verifier_closure_matches_every_source():
    document = registration()
    for entry in document["verifier_source_closure"]["files"]:
        payload = (ROOT / entry["path"]).read_bytes()
        assert len(payload) == entry["size_bytes"]
        assert sha(payload) == entry["sha256"]
    assert sha(canonical(document["verifier_source_closure"])) == document[
        "verifier_source_closure_sha256"
    ]


def test_i_formal_codec_profile_is_unchanged():
    document, fixtures = verify_registration(NEW_REGISTRATION, formal=True)
    assert codec_profile() == fixtures["codec_profile"]
    assert document["formal_codec_profile_sha256"] == EXPECTED_CODEC_PROFILE_SHA256
    assert sha(canonical(codec_profile())) == EXPECTED_CODEC_PROFILE_SHA256


def test_j_registration_has_no_source_hash_cycle():
    document = registration()
    paths = {entry["path"] for entry in document["complete_source_closure"]["files"]}
    paths.update(entry["path"] for entry in document["verifier_source_closure"]["files"])
    assert NEW_RELATIVE not in paths
    assert HISTORICAL_RELATIVE not in paths
    assert PARSER_REPAIR_RELATIVE not in paths
    assert not any(path.endswith("SOURCE_REGISTRATION_V1.json") for path in paths)


def test_l_deliberate_source_drift_fails_closed(tmp_path):
    mutated = copy.deepcopy(registration())
    entry = closure_entry(
        mutated, "src/agicore/trading/ema_pullback_v2_recovery_storage.py"
    )
    entry["sha256"] = "0" * 64
    mutated["complete_source_closure_sha256"] = sha(
        canonical(mutated["complete_source_closure"])
    )
    path = tmp_path / "deliberately-mismatched-registration.json"
    path.write_bytes(canonical(mutated))
    with pytest.raises(StorageProofError, match="registered executable source changed"):
        verify_registration(path, formal=False)


def test_m_preflight_source_cannot_call_worker_or_replay_cases():
    assert called_names(PREFLIGHT).isdisjoint(PROHIBITED_CALLS)
    plan = parse_canonical([PLAN.read_bytes()])
    command = plan["commands"]["non_worker_preflight"]
    assert command[-1] == PREFLIGHT_RELATIVE
    assert HARNESS_RELATIVE not in command


def test_registration_binds_preflight_and_parent_identities():
    document = registration()
    assert document["non_worker_preflight"]["path"] == PREFLIGHT_RELATIVE
    assert document["non_worker_preflight"]["sha256"] == sha(PREFLIGHT.read_bytes())
    assert document["parent_registrations"] == [
        {
            "complete_source_closure_sha256": (
                "8a188999dfeee33ea71a21327360f1d17962ab7b4083b690b08beef72233dc5c"
            ),
            "path": HISTORICAL_RELATIVE,
            "role": "HISTORICAL_STORAGE_SOURCE",
            "sha256": EXPECTED_HISTORICAL_REGISTRATION_SHA256,
        },
        {
            "complete_source_closure_sha256": (
                "7a730b86b51fd1c063cc7ea637763009d2bf303a9d1b4afa879e99116ec077ec"
            ),
            "path": PARSER_REPAIR_RELATIVE,
            "role": "PARSER_REPAIR_SOURCE",
            "sha256": EXPECTED_PARSER_REPAIR_REGISTRATION_SHA256,
        },
    ]
    assert sha(HISTORICAL_REGISTRATION.read_bytes()) == (
        EXPECTED_HISTORICAL_REGISTRATION_SHA256
    )
    assert sha(PARSER_REPAIR_REGISTRATION.read_bytes()) == (
        EXPECTED_PARSER_REPAIR_REGISTRATION_SHA256
    )
