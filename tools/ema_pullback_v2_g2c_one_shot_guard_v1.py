"""Inert G2C claim protocol: injected API only, no HTTP client or worker entrypoint.

Activation trust must come from an independent owner approval, never dispatch inputs.
The only shipped configuration is unapproved. Tests exercise the protocol with fakes.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from threading import Lock
from typing import Protocol

REPOSITORY = "Magassa56/agicore-v2"
OWNER_ID = 166902290
BASE_SHA = "b86453d880b32245b046e5cb7dfa3bf74862dc7c"
CAMPAIGN = "g2c-parity-v3-5000-campaign-1"
CLAIM_REF = "refs/heads/agicore-execution-claims/" + CAMPAIGN
PLAN_SHA256 = "4baa39605bd3b05bd177681d0c382e923237541c770af648f35b83f47dcf552c"
PLAN_FILE = "AGICORE_G2C_PARITY_V3_5000_REGISTERED_PLAN_20261116.json"
LIMITS = {
    "address_space_bytes": 2 << 30,
    "cpu_seconds": 150,
    "file_bytes": 64 << 20,
    "logical_bytes": 256 << 20,
    "physical_bytes": 256 << 20,
    "tier_physical_bytes": 1 << 30,
    "wall_seconds": 240,
}
FROZEN_FILES = {
    PLAN_FILE: "056fc349af0258132af5ced20b114db42bcdfc9ae4817ff2ddc6b4d3fa1a3774",
    "EMA_PULLBACK_V2_G2C_REFERENCE_PARITY_V2.json": "a7debadeec3b5038699216b3abb6142086617296677dcb37b9fd01f6010c9699",
    "EMA_PULLBACK_V2_G2C_REFERENCE_PARITY_V3.json": "cff5ae162ec68b03904b0f8fb18e8fb68c456ecc97214da500d41206fd195424",
    "EMA_PULLBACK_V2_G2C_SYNTHETIC_CONTRACT_V3.json": "5de23f01bb157b2d7575a54dcc0d36033f6ba3ae751f6338067088c895bf6663",
    "EMA_PULLBACK_V2_G2C_SYNTHETIC_CONTRACT_V4.json": "e36c6a8985c383c9794cf3188e49940ddf28d7074d070f042661f6534629961f",
    "EMA_PULLBACK_V2_G2C_VERIFIER_V5.json": "95e836f3897a973d08e8a38e3845bc4e15d53e67996f03f718dc6f9f05445a35",
    "EMA_PULLBACK_V2_G2C_VERIFIER_V5_1.json": "9dc2cfcaf37909004d084456dadbc6c896699033b5e3428d62ae56ece7e87bf6",
    "EMA_PULLBACK_V2_G2C_SUPERVISION_V5_1.json": "d7b6179c5815286a52479eecf48528f03a32c08ceb1515774395df6854bf2006",
    "AGICORE_G2C_1000_9E6E_TIER_REPORT_20261111.json": "c7b1c48c69f81439892082cc23bb7ddb34190775b93f528177df6a6d49dad555",
    "AGICORE_G2C_1000_9E6E_NEGATIVE_20261111.json": "ead441231b611d445ece5d4489d748a0fc51e8a2c7c9e39348f2af86070e25f4",
    "AGICORE_G2C_1000_9E6E_BUNDLES_20261111.zip": "8dfa4e7aa278cbc1503aae4ea48489f0330c720b2a6f6f0d49966b065c349fa7",
    "AGICORE_G2C_PARITY_V3_5000_READONLY_VALIDATION_20261116.json": "73ef1673d2a0993ad61cb1ccbc24b15aaf43c234a65a2bf0a4dfa8c8718c0b43",
    "EMA_PULLBACK_V2_REGIME_GATED_BASELINE_MANIFEST.json": "965b44c837477bac8a81bbcde5df354997fcd84a0afd4f66f76a30e0a654240a",
    "EMA_PULLBACK_V2_DEVELOPMENT_PROTOCOL.json": "68dc6e6409aea4efb88e4a19e09a7ba17a68043a79f14ec23e569d3353267402",
}


class GuardRefused(RuntimeError):
    """The campaign cannot proceed; do not retry or remove its evidence."""


def require(condition: bool, reason: str) -> None:
    """Reject an unknown or invalid prerequisite."""
    if not condition:
        raise GuardRefused(reason)


def canonical(value: object) -> bytes:
    """Encode protocol evidence independently of trading serialization."""
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
    ).encode()


def digest(raw: bytes) -> str:
    """Return a SHA-256 commitment."""
    return hashlib.sha256(raw).hexdigest()


def _sha1(value: object) -> bool:
    return type(value) is str and re.fullmatch(r"[0-9a-f]{40}", value) is not None


def _positive(value: object) -> bool:
    return type(value) is int and value > 0


def _read(root: Path, relative: str) -> bytes:
    path = PurePosixPath(relative)
    require(
        not path.is_absolute() and ".." not in path.parts and "data" not in path.parts,
        "forbidden identity path",
    )
    target = root / path
    require(
        "data" not in target.parts
        and target.is_file()
        and not any(p.is_symlink() for p in (target, *target.parents)),
        "unsafe identity file",
    )
    require(target.stat().st_size <= 16 << 20, "oversized identity file")
    return target.read_bytes()


def verify_identities(root: Path) -> str:
    """Hash pinned metadata and source bytes; never import or run any trading component."""
    records = {}
    documents = {}
    for name, expected in FROZEN_FILES.items():
        raw = _read(root, "docs/evidence/" + name)
        require(digest(raw) == expected, "historical identity changed: " + name)
        records[name] = expected
        if name.endswith(".json"):
            documents[name] = json.loads(raw)
    packet = documents[PLAN_FILE]
    require(
        packet["plan_sha256"] == digest(canonical(packet["plan"])) == PLAN_SHA256,
        "canonical plan mismatch",
    )
    v4 = documents["EMA_PULLBACK_V2_G2C_SYNTHETIC_CONTRACT_V4.json"]
    require(v4["tiers"]["5000"] == LIMITS, "resource limits changed")
    entries = list(v4["source_closure"])
    require(digest(canonical(entries)) == v4["source_closure_sha256"], "source closure mismatch")
    # Predecessor registrations are immutable evidence, not current source bindings.
    active = (
        "EMA_PULLBACK_V2_G2C_REFERENCE_PARITY_V2.json",
        "EMA_PULLBACK_V2_G2C_REFERENCE_PARITY_V3.json",
        "EMA_PULLBACK_V2_G2C_VERIFIER_V5_1.json",
        "EMA_PULLBACK_V2_G2C_SUPERVISION_V5_1.json",
    )
    for name in active:
        doc = documents[name]
        for item in doc.values():
            if isinstance(item, dict) and {"path", "sha256"} <= item.keys():
                entries.append(item)
    for entry in entries:
        raw = _read(root, entry["path"])
        require(digest(raw) == entry["sha256"], "registered source changed: " + entry["path"])
        records[entry["path"]] = entry["sha256"]
    return digest(canonical(records))


@dataclass(frozen=True)
class Activation:
    """Independent trusted owner anchors, absent in the shipped configuration.

    A future adapter must authenticate these outside workflow_dispatch inputs.
    The authorization document also pins one run_id, including before reservation.
    """

    sha: str | None = None
    authorization_sha256: str | None = None
    guard_sha256: str | None = None
    ruleset_id: int | None = None


@dataclass(frozen=True)
class Run:
    """Trusted Actions context, obtained by the future adapter rather than user inputs."""

    repository: str
    event: str
    ref: str
    sha: str
    workflow_sha: str
    checkout_sha: str
    run_id: int
    run_attempt: int
    actor_id: int
    triggering_actor_id: int


@dataclass(frozen=True)
class Reply:
    """One API response; redirects, transport errors and retries are adapter concerns."""

    status: int
    body: dict


class GitHubPort(Protocol):
    """No implementation is shipped; tests supply an atomic fake Git database.

    A future HTTPS adapter must disable automatic mutation retries and redirects.
    """

    def request(self, method: str, path: str, payload: dict | None = None) -> Reply:
        """Perform exactly one request or raise; never synthesize success."""
        ...


def verify_ruleset(rule: dict, expected_id: int) -> None:
    """Require an active, non-bypassable exact-claim or claim-namespace ruleset."""
    names = rule.get("conditions", {}).get("ref_name", {})
    require(
        type(rule.get("id")) is int
        and rule["id"] == expected_id
        and rule.get("source") == REPOSITORY
        and rule.get("source_type") == "Repository"
        and rule.get("enforcement") == "active"
        and rule.get("target") == "branch"
        and rule.get("bypass_actors") == []
        and names.get("exclude") == []
        and names.get("include") in ([CLAIM_REF], ["refs/heads/agicore-execution-claims/*"]),
        "claim ruleset absent or unsafe",
    )
    types = {entry.get("type") for entry in rule.get("rules", [])}
    require(
        {"update", "deletion"} <= types and "creation" not in types,
        "claim updates/deletions must be forbidden and creation allowed",
    )


def verify_preflight(proof: dict, claim_sha: str, run: Run) -> None:
    """Validate an injected future host attestation; never probe resources or spawn here.

    The future adapter must measure these locally after reservation. Dispatch inputs
    and caller-supplied booleans are not an authenticated host attestation.
    """
    require(
        proof.get("claim_sha") == claim_sha
        and proof.get("run_id") == run.run_id
        and type(proof.get("run_id")) is int
        and proof.get("activation_sha") == run.sha,
        "unbound preflight",
    )
    for name in (
        "linux",
        "cgroup_v2_ancestry_verified",
        "group_and_descendants_stopped",
        "output_fresh",
        "output_symlink_free",
        "output_outside_data",
    ):
        require(proof.get(name) is True, "unknown or failed preflight: " + name)
    for name, minimum in (("effective_memory_available", 4 << 30), ("disk_free", 2 << 30)):
        value = proof.get(name)
        require(type(value) is int and value >= minimum, "insufficient or unknown " + name)
    require(
        proof.get("limits") == LIMITS and canonical(proof["limits"]) == canonical(LIMITS),
        "preflight resource limits changed",
    )
    output = proof.get("output")
    require(
        type(output) is str
        and PurePosixPath(output).is_absolute()
        and not {"data", ".."}.intersection(PurePosixPath(output).parts),
        "unsafe output path",
    )


class Guard:
    """One reservation or calculation entry per instance; every failure is terminal.

    Git's create-only ref is the cross-run arbiter. run_attempt is checked again
    in the calculation job, including when Actions retains old job outputs.
    """

    def __init__(self, root: Path, api: GitHubPort, activation: Activation = Activation()):
        self.root, self.api, self.activation = root, api, activation
        self._lock = Lock()
        self._entered = False
        self.events: list[dict] = []

    def _enter(self, operation: str) -> None:
        with self._lock:
            require(not self._entered, "guard instance already consumed; no retry")
            self._entered = True
        self._record({"operation": operation, "state": "ENTERED"})

    def _record(self, event: dict) -> None:
        self.events.append(
            {
                "utc": datetime.now(UTC).isoformat(),
                "task_id": CAMPAIGN,
                "agent_id": "agicore:g2c-one-shot-guard:v1",
                **event,
            }
        )

    def _api(
        self, method: str, path: str, payload: dict | None = None, *, status: int = 200
    ) -> dict:
        response = self.api.request(method, "/repos/" + REPOSITORY + path, payload)
        require(
            type(response.status) is int and response.status == status, "API refused or ambiguous"
        )
        require(type(response.body) is dict, "malformed API response")
        return response.body

    def _validate(self, run: Run, authorization: bytes) -> tuple[dict, str]:
        pin = self.activation
        require(
            _sha1(pin.sha)
            and type(pin.authorization_sha256) is str
            and re.fullmatch(r"[0-9a-f]{64}", pin.authorization_sha256) is not None
            and _positive(pin.ruleset_id),
            "activation not independently approved",
        )
        require(
            type(run) is Run
            and run.repository == REPOSITORY
            and run.event == "workflow_dispatch"
            and run.ref == "refs/heads/main"
            and run.sha == run.workflow_sha == run.checkout_sha == pin.sha
            and _positive(run.run_id)
            and type(run.run_attempt) is int
            and run.run_attempt == 1
            and type(run.actor_id) is int
            and run.actor_id == OWNER_ID
            and type(run.triggering_actor_id) is int
            and run.triggering_actor_id == OWNER_ID,
            "unapproved context or rerun",
        )
        require(
            type(authorization) is bytes
            and len(authorization) <= 16384
            and digest(authorization) == pin.authorization_sha256,
            "owner authorization mismatch",
        )
        identities = verify_identities(self.root)
        guard_sha = digest(Path(__file__).read_bytes())
        require(guard_sha == pin.guard_sha256, "guard source not independently approved")
        expected = {
            "schema": "agicore:g2c-one-shot-owner-authorization:v1",
            "repository": REPOSITORY,
            "owner_id": OWNER_ID,
            "campaign": CAMPAIGN,
            "activation_sha": pin.sha,
            "run_id": run.run_id,
            "plan_sha256": PLAN_SHA256,
            "identities_sha256": identities,
            "guard_sha256": guard_sha,
            "ruleset_id": pin.ruleset_id,
            "scope": "ONE_INVENTED_5000_CAMPAIGN",
        }
        require(authorization == canonical(expected), "noncanonical or unbound owner authorization")
        main = self._api("GET", "/git/ref/heads/main")
        require(
            main.get("ref") == "refs/heads/main"
            and main.get("object", {}).get("type") == "commit"
            and main.get("object", {}).get("sha") == pin.sha,
            "main SHA mismatch",
        )
        verify_ruleset(self._api("GET", f"/rulesets/{pin.ruleset_id}"), pin.ruleset_id)
        parent = self._api("GET", "/git/commits/" + pin.sha)
        tree = parent.get("tree", {}).get("sha")
        require(parent.get("sha") == pin.sha and _sha1(tree), "activation commit unknown")
        claim = {
            **expected,
            "schema": "agicore:g2c-one-shot-claim:v1",
            "run_attempt": 1,
            "authorization_sha256": pin.authorization_sha256,
            "claim_ref": CLAIM_REF,
        }
        return claim, tree

    def reserve(self, run: Run, authorization: bytes) -> bytes:
        """Create a claim commit and atomically create its fixed ref once; never retry.

        A lost 201 consumes the claim but returns no receipt. Exceptions, including
        interrupts, propagate; events and remote objects are never cleaned up.
        """
        self._enter("reserve")
        claim, tree = self._validate(run, authorization)
        existing = self.api.request(
            "GET", "/repos/" + REPOSITORY + "/git/ref/" + CLAIM_REF.removeprefix("refs/")
        )
        require(
            type(existing.status) is int and existing.status == 404, "claim exists or is unknown"
        )
        commit = self._api(
            "POST",
            "/git/commits",
            {
                "message": canonical(claim).decode(),
                "tree": tree,
                "parents": [run.sha],
            },
            status=201,
        )
        sha = commit.get("sha")
        require(_sha1(sha), "invalid claim commit")
        self._record({"state": "CLAIM_CREATE_SENT", "claim_sha": sha, "run_id": run.run_id})
        ref = self._api("POST", "/git/refs", {"ref": CLAIM_REF, "sha": sha}, status=201)
        self._verify_ref(ref, sha)
        self._verify_commit(self._api("GET", "/git/commits/" + sha), sha, tree, claim, run)
        receipt = {
            "schema": "agicore:g2c-one-shot-reservation:v1",
            "ref": CLAIM_REF,
            "claim_sha": sha,
            "claim_sha256": digest(canonical(claim)),
            "run_id": run.run_id,
        }
        self._record({"state": "RESERVED", **receipt})
        return canonical(receipt)

    def calculation_gate(
        self, run: Run, authorization: bytes, receipt: bytes, preflight: dict
    ) -> dict:
        """Reauthenticate the immutable claim and this attempt; return metadata, never launch."""
        self._enter("calculation")
        claim, tree = self._validate(run, authorization)
        require(type(receipt) is bytes and len(receipt) <= 4096, "invalid reservation receipt")
        item = json.loads(receipt)
        require(
            type(item) is dict and _sha1(item.get("claim_sha")), "malformed reservation receipt"
        )
        sha = item["claim_sha"]
        expected = {
            "schema": "agicore:g2c-one-shot-reservation:v1",
            "ref": CLAIM_REF,
            "claim_sha": sha,
            "claim_sha256": digest(canonical(claim)),
            "run_id": run.run_id,
        }
        require(receipt == canonical(expected), "forged or noncanonical reservation receipt")
        ref = self._api("GET", "/git/ref/" + CLAIM_REF.removeprefix("refs/"))
        self._verify_ref(ref, sha)
        self._verify_commit(self._api("GET", "/git/commits/" + sha), sha, tree, claim, run)
        verify_preflight(preflight, sha, run)
        result = {
            "state": "SIMULATED_PREREQUISITES_VERIFIED",
            "run_id": run.run_id,
            "claim_sha": sha,
            "plan_sha256": PLAN_SHA256,
            "workers_launched": 0,
        }
        self._record(result)
        return result

    @staticmethod
    def _verify_ref(ref: dict, sha: str) -> None:
        obj = ref.get("object", {})
        require(
            ref.get("ref") == CLAIM_REF and obj.get("type") == "commit" and obj.get("sha") == sha,
            "claim ref mismatch",
        )

    @staticmethod
    def _verify_commit(commit: dict, sha: str, tree: str, claim: dict, run: Run) -> None:
        require(
            commit.get("sha") == sha
            and commit.get("message") == canonical(claim).decode()
            and commit.get("tree", {}).get("sha") == tree
            and [p.get("sha") for p in commit.get("parents", [])] == [run.sha],
            "claim commit provenance mismatch",
        )


if __name__ == "__main__":
    raise SystemExit(
        "INERT: no live API adapter, approved activation or worker launcher is shipped"
    )
