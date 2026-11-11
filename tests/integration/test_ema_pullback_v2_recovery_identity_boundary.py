"""Preserve the reference-only storage boundary until a successor is registered."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

import pytest

from agicore.trading import ema_pullback_v2_development_replay as reference
from agicore.trading.ema_pullback_v2_recovery_storage import _witnesses, produce_synthetic_bundle
from agicore.trading.ema_pullback_v2_storage_audit import audit_native
from agicore.trading.ema_pullback_v2_storage_format import (
    MAX_OBSERVATIONS,
    ROOT,
    StorageProofError,
    codec_profile,
)
from tests.unit.trading.v2_recovery_storage_fixtures import synthetic_raw
from tools.ema_pullback_v2_storage_synthetic_proof import verify_registration

# The historical WIP engine is not present or approved as a reference runner on main.
OPTIMIZED_WIP_RUNNER_SHA256 = "854a6cbe7b89f3c6f0e9f49a8a5095745baf20693c2e89b115dfcadbfacbdf56"
REGISTRATION = (
    ROOT / "docs/evidence/EMA_PULLBACK_V2_RECOVERY_STORAGE_CI_PORTABLE_SOURCE_REGISTRATION_V1.json"
)


def test_foreign_runner_identity_is_rejected_without_rewriting_historical_bindings(tmp_path):
    """A coherent alternative identity is not the registered native reference."""
    raw = synthetic_raw("impulse_profit_LONG")
    bindings = reference.read_frozen_replay_bindings_v2()
    registration, _ = verify_registration(REGISTRATION, formal=False)
    document = reference.evaluate_synthetic_development_replay_v2(raw, bindings=bindings).document
    document["run_identity"]["runner_source_sha256"] = OPTIMIZED_WIP_RUNNER_SHA256
    identity = reference.screening.RunIdentity(**document["run_identity"])
    document["run_id_sha256"] = identity.sha256
    without_output_hash = {key: value for key, value in document.items() if key != "output_sha256"}
    document["output_sha256"] = hashlib.sha256(
        reference.canonical_replay_bytes_v2(without_output_hash)
    ).hexdigest()
    native_bytes = reference.canonical_replay_bytes_v2(document)

    with pytest.raises(reference.DevelopmentReplayV2Error, match="result identity/source binding"):
        produce_synthetic_bundle(
            native_bytes=native_bytes,
            synthetic_raw=raw,
            directory=tmp_path / "foreign-runner",
            profile=codec_profile(),
            complete_source_sha=registration["complete_source_closure_sha256"],
            verifier_source_sha=registration["verifier_source_closure_sha256"],
        )
    assert not (tmp_path / "foreign-runner").exists()
    with pytest.raises(StorageProofError, match="native reference run binding"):
        audit_native(document, _witnesses(raw), raw)


def test_historical_witness_storage_rejects_the_201st_invented_observation():
    """The 200-row profile must not be represented as 89,841-row evidence."""
    start = datetime(2099, 1, 1, tzinfo=UTC)
    rows = [
        f"{start + timedelta(minutes=i):%Y%m%d %H%M%S};20000;20001;19999;20000;100\n".encode()
        for i in range(MAX_OBSERVATIONS + 1)
    ]
    assert MAX_OBSERVATIONS == 200
    assert len(_witnesses(b"".join(rows[:-1]))) == MAX_OBSERVATIONS
    with pytest.raises(StorageProofError, match="bounded complete invented rows"):
        _witnesses(b"".join(rows))
