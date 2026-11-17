"""Atomic fake Git database and sentinels only: no network, subprocess or G2C engine."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import os
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier, Lock

import pytest

from tools import ema_pullback_v2_g2c_one_shot_guard_v1 as guard

ROOT = Path(__file__).resolve().parents[2]
ACTIVATION = "a" * 40
TREE = "b" * 40
PREFIX = "/repos/" + guard.REPOSITORY
REF_PATH = PREFIX + "/git/ref/" + guard.CLAIM_REF.removeprefix("refs/")
PROPOSAL = ROOT / "docs/operations/g2c-parity-v3-one-shot.yml.example"


@pytest.fixture(autouse=True)
def forbid_processes_and_network(monkeypatch):
    def forbidden(*_args, **_kwargs):
        pytest.fail("process or network launch forbidden in guard simulation")

    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(os, "system", forbidden)
    monkeypatch.setattr(os, "fork", forbidden)
    monkeypatch.setattr(socket, "create_connection", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)


def ruleset():
    return {
        "id": 42,
        "source": guard.REPOSITORY,
        "source_type": "Repository",
        "target": "branch",
        "enforcement": "active",
        "bypass_actors": [],
        "conditions": {"ref_name": {"include": [guard.CLAIM_REF], "exclude": []}},
        "rules": [{"type": "update"}, {"type": "deletion"}],
    }


class FakeGitHub:
    """Only this fake implements writes; ref creation is atomic under a thread lock."""

    def __init__(self):
        self.lock = Lock()
        self.barrier = None
        self.ref = None
        self.calls = []
        self.commits = {ACTIVATION: {"sha": ACTIVATION, "tree": {"sha": TREE}}}
        self.ruleset = ruleset()
        self.fault = None
        self.main = ACTIVATION

    def request(self, method, path, payload=None):
        if path == PREFIX + "/git/refs" and self.barrier:
            self.barrier.wait(timeout=5)
        with self.lock:
            self.calls.append((method, path, copy.deepcopy(payload)))
            if self.fault == "before_commit" and path == PREFIX + "/git/commits":
                raise KeyboardInterrupt("before reservation")
            if method == "GET" and path == PREFIX + "/git/ref/heads/main":
                return guard.Reply(
                    200,
                    {
                        "ref": "refs/heads/main",
                        "object": {"type": "commit", "sha": self.main, "url": "fake-main-metadata"},
                    },
                )
            if method == "GET" and path == PREFIX + "/rulesets/42":
                if self.fault == "ruleset_absent":
                    return guard.Reply(404, {})
                if self.fault == "network_before_claim":
                    raise TimeoutError("network unavailable before claim")
                return guard.Reply(200, copy.deepcopy(self.ruleset))
            if method == "GET" and path == REF_PATH:
                return (
                    guard.Reply(200, copy.deepcopy(self.ref)) if self.ref else guard.Reply(404, {})
                )
            if method == "GET" and path.startswith(PREFIX + "/git/commits/"):
                sha = path.rsplit("/", 1)[1]
                return guard.Reply(200, copy.deepcopy(self.commits[sha]))
            if method == "POST" and path == PREFIX + "/git/commits":
                sha = hashlib.sha1(guard.canonical(payload)).hexdigest()
                self.commits[sha] = {
                    "sha": sha,
                    "tree": {"sha": payload["tree"]},
                    "message": payload["message"],
                    "parents": [{"sha": p} for p in payload["parents"]],
                }
                return guard.Reply(201, copy.deepcopy(self.commits[sha]))
            if method == "POST" and path == PREFIX + "/git/refs":
                if self.ref:
                    return guard.Reply(422, {"message": "Reference already exists"})
                if self.fault == "before_ref":
                    raise KeyboardInterrupt("before atomic ref create")
                self.ref = {
                    "ref": payload["ref"],
                    "object": {
                        "type": "commit",
                        "sha": payload["sha"],
                        "url": "fake-commit-metadata",
                    },
                }
                if self.fault == "lost_201":
                    raise TimeoutError("201 response lost after atomic reservation")
                if self.fault == "interrupt_after_ref":
                    raise KeyboardInterrupt("interruption after reservation")
                if self.fault == "ambiguous_202":
                    return guard.Reply(202, copy.deepcopy(self.ref))
                return guard.Reply(201, copy.deepcopy(self.ref))
            raise AssertionError((method, path))


@pytest.fixture(scope="module")
def identities():
    return guard.verify_identities(ROOT)


def setup_run(identities, run_id=1234):
    run = guard.Run(
        guard.REPOSITORY,
        "workflow_dispatch",
        "refs/heads/main",
        ACTIVATION,
        ACTIVATION,
        ACTIVATION,
        run_id,
        1,
        guard.OWNER_ID,
        guard.OWNER_ID,
    )
    code_sha = guard.digest(Path(guard.__file__).read_bytes())
    authorization = guard.canonical(
        {
            "schema": "agicore:g2c-one-shot-owner-authorization:v1",
            "repository": guard.REPOSITORY,
            "owner_id": guard.OWNER_ID,
            "campaign": guard.CAMPAIGN,
            "activation_sha": ACTIVATION,
            "run_id": run_id,
            "plan_sha256": guard.PLAN_SHA256,
            "identities_sha256": identities,
            "guard_sha256": code_sha,
            "ruleset_id": 42,
            "scope": "ONE_INVENTED_5000_CAMPAIGN",
        }
    )
    activation = guard.Activation(ACTIVATION, guard.digest(authorization), code_sha, 42)
    return run, authorization, activation


def host(receipt, run):
    return {
        "claim_sha": json.loads(receipt)["claim_sha"],
        "run_id": run.run_id,
        "activation_sha": run.sha,
        "linux": True,
        "cgroup_v2_ancestry_verified": True,
        "group_and_descendants_stopped": True,
        "output_fresh": True,
        "output_symlink_free": True,
        "output_outside_data": True,
        "effective_memory_available": 4 << 30,
        "disk_free": 2 << 30,
        "limits": dict(guard.LIMITS),
        "output": "/isolated/new-campaign",
    }


def calculation(api, activation, run, authorization, receipt, proof, launched):
    permit = guard.Guard(ROOT, api, activation).calculation_gate(run, authorization, receipt, proof)
    launched.append(permit)  # Pure sentinel, deliberately no callable or engine in the guard.


def test_shipped_guard_is_unapproved_and_has_no_live_entrypoint(identities):
    run, auth, _ = setup_run(identities)
    api = FakeGitHub()
    with pytest.raises(guard.GuardRefused, match="not independently approved"):
        guard.Guard(ROOT, api).reserve(run, auth)
    assert api.calls == [] and api.ref is None
    tree = ast.parse(Path(guard.__file__).read_text())
    imports = [
        node.module if isinstance(node, ast.ImportFrom) else node.names[0].name
        for node in ast.walk(tree)
        if isinstance(node, (ast.Import, ast.ImportFrom))
    ]
    assert set(imports) <= {
        "__future__",
        "hashlib",
        "json",
        "re",
        "dataclasses",
        "pathlib",
        "datetime",
        "threading",
        "typing",
    }
    assert not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"run_worker", "run_tier", "Popen", "system"}
        for node in ast.walk(tree)
    )


def test_successful_claim_is_bound_to_owner_run_sources_and_fresh_calculation(identities):
    run, auth, activation = setup_run(identities)
    api, launched = FakeGitHub(), []
    receipt = guard.Guard(ROOT, api, activation).reserve(run, auth)
    calculation(api, activation, run, auth, receipt, host(receipt, run), launched)
    assert len(launched) == 1 and launched[0]["workers_launched"] == 0
    creates = [c for c in api.calls if c[0] == "POST" and c[1].endswith("/git/refs")]
    assert len(creates) == 1 and creates[0][2]["ref"] == guard.CLAIM_REF
    assert all(method in {"GET", "POST"} for method, _, _ in api.calls)
    claim = json.loads(api.commits[json.loads(receipt)["claim_sha"]]["message"])
    assert claim["run_id"] == run.run_id and claim["plan_sha256"] == guard.PLAN_SHA256
    assert claim["authorization_sha256"] == activation.authorization_sha256


def test_two_concurrent_requests_have_one_atomic_winner(identities):
    api = FakeGitHub()
    api.barrier = Barrier(2)

    def request(number):
        run, auth, activation = setup_run(identities, number)
        try:
            return run, auth, activation, guard.Guard(ROOT, api, activation).reserve(run, auth)
        except guard.GuardRefused:
            return None

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(request, (1001, 1002)))
    winners = [result for result in results if result is not None]
    assert len(winners) == 1
    run, auth, activation, receipt = winners[0]
    launched = []
    calculation(api, activation, run, auth, receipt, host(receipt, run), launched)
    assert len(launched) == 1
    assert len([c for c in api.calls if c[0] == "POST" and c[1].endswith("/git/refs")]) == 2


def test_existing_claim_rejects_even_a_new_independently_approved_dispatch(identities):
    api = FakeGitHub()
    run, auth, activation = setup_run(identities)
    guard.Guard(ROOT, api, activation).reserve(run, auth)
    old = copy.deepcopy(api.ref)
    run2, auth2, activation2 = setup_run(identities, 1235)
    with pytest.raises(guard.GuardRefused, match="claim exists"):
        guard.Guard(ROOT, api, activation2).reserve(run2, auth2)
    assert api.ref == old
    assert len([c for c in api.calls if c[0] == "POST" and c[1].endswith("/git/refs")]) == 1


@pytest.mark.parametrize(
    "fault,error,claimed",
    [
        ("before_commit", KeyboardInterrupt, False),
        ("before_ref", KeyboardInterrupt, False),
        ("interrupt_after_ref", KeyboardInterrupt, True),
        ("lost_201", TimeoutError, True),
        ("ambiguous_202", guard.GuardRefused, True),
        ("network_before_claim", TimeoutError, False),
    ],
)
def test_interruptions_and_ambiguous_network_are_terminal(identities, fault, error, claimed):
    run, auth, activation = setup_run(identities)
    api = FakeGitHub()
    api.fault = fault
    instance = guard.Guard(ROOT, api, activation)
    with pytest.raises(error):
        instance.reserve(run, auth)
    count = len(api.calls)
    with pytest.raises(guard.GuardRefused, match="already consumed"):
        instance.reserve(run, auth)
    assert len(api.calls) == count and bool(api.ref) is claimed
    assert instance.events  # Caller retains these; remote objects are never cleaned up.
    api.fault = None
    for changed in (replace(run, run_attempt=2), replace(run, run_id=run.run_id + 1)):
        with pytest.raises(guard.GuardRefused):
            guard.Guard(ROOT, api, activation).reserve(changed, auth)
    assert (
        len(api.calls) == count
    )  # Approval run_id prevents redispatch even before marker creation.


@pytest.mark.parametrize(
    "changes",
    [
        {"repository": "attacker/fork"},
        {"event": "pull_request"},
        {"event": "push"},
        {"event": "workflow_run"},
        {"ref": "refs/heads/feature"},
        {"sha": "c" * 40},
        {"workflow_sha": "c" * 40},
        {"run_attempt": 2},
        {"run_attempt": True},
        {"checkout_sha": "c" * 40},
        {"actor_id": 7},
        {"triggering_actor_id": 7},
        {"run_id": True},
        {"run_id": 0},
    ],
)
def test_unapproved_context_is_rejected_before_api_calls(identities, changes):
    run, auth, activation = setup_run(identities)
    api = FakeGitHub()
    with pytest.raises(guard.GuardRefused):
        guard.Guard(ROOT, api, activation).reserve(replace(run, **changes), auth)
    assert api.calls == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("activation_sha", "c" * 40),
        ("owner_id", 7),
        ("plan_sha256", "0" * 64),
        ("identities_sha256", "0" * 64),
        ("scope", "RETRY_ALLOWED"),
        ("run_id", 999),
    ],
)
def test_rehashed_but_unbound_owner_authorization_fails(identities, field, value):
    run, auth, activation = setup_run(identities)
    forged = json.loads(auth)
    forged[field] = value
    raw = guard.canonical(forged)
    api = FakeGitHub()
    # Even an adapter accepting this external digest cannot skip the semantic bindings.
    pin = replace(activation, authorization_sha256=guard.digest(raw))
    with pytest.raises(guard.GuardRefused, match="unbound owner"):
        guard.Guard(ROOT, api, pin).reserve(run, raw)
    assert api.calls == []


def test_bad_authorization_digest_or_guard_source_is_refused(identities):
    run, auth, activation = setup_run(identities)
    for pin, raw in ((activation, auth + b" "), (replace(activation, guard_sha256="0" * 64), auth)):
        api = FakeGitHub()
        with pytest.raises(guard.GuardRefused):
            guard.Guard(ROOT, api, pin).reserve(run, raw)
        assert api.calls == []


@pytest.mark.parametrize("file", list(guard.FROZEN_FILES))
def test_changed_historical_bytes_are_refused_without_replay(monkeypatch, file):
    original = guard._read

    def altered(root, relative):
        raw = original(root, relative)
        return raw + b" " if relative == "docs/evidence/" + file else raw

    monkeypatch.setattr(guard, "_read", altered)
    with pytest.raises(guard.GuardRefused, match="historical identity changed"):
        guard.verify_identities(ROOT)


def test_changed_registered_worker_source_is_refused(monkeypatch):
    original = guard._read

    def altered(root, relative):
        raw = original(root, relative)
        return raw + b" " if relative == "tools/ema_pullback_v2_g2c_parity_v3.py" else raw

    monkeypatch.setattr(guard, "_read", altered)
    with pytest.raises(guard.GuardRefused, match="registered source changed"):
        guard.verify_identities(ROOT)


@pytest.mark.parametrize(
    "change",
    [
        "absent",
        "inactive",
        "bypass",
        "exclude",
        "wrong_namespace",
        "missing_update",
        "missing_delete",
        "creation",
        "wrong_id",
    ],
)
def test_absent_or_inadequate_claim_protection_refuses_reservation(identities, change):
    run, auth, activation = setup_run(identities)
    api = FakeGitHub()
    if change == "absent":
        api.fault = "ruleset_absent"
    elif change == "inactive":
        api.ruleset["enforcement"] = "evaluate"
    elif change == "bypass":
        api.ruleset["bypass_actors"] = [{"actor_id": 1}]
    elif change == "exclude":
        api.ruleset["conditions"]["ref_name"]["exclude"] = [guard.CLAIM_REF]
    elif change == "wrong_namespace":
        api.ruleset["conditions"]["ref_name"]["include"] = ["refs/heads/main"]
    elif change == "creation":
        api.ruleset["rules"].append({"type": "creation"})
    elif change == "wrong_id":
        api.ruleset["id"] = 43
    else:
        removed = "update" if change == "missing_update" else "deletion"
        api.ruleset["rules"] = [r for r in api.ruleset["rules"] if r["type"] != removed]
    with pytest.raises(guard.GuardRefused):
        guard.Guard(ROOT, api, activation).reserve(run, auth)
    assert api.ref is None and not any(c[0] == "POST" for c in api.calls)


def test_main_movement_refuses_reservation_and_calculation(identities):
    run, auth, activation = setup_run(identities)
    api = FakeGitHub()
    receipt = guard.Guard(ROOT, api, activation).reserve(run, auth)
    old_ref, launched = copy.deepcopy(api.ref), []
    api.main = "c" * 40
    with pytest.raises(guard.GuardRefused, match="main SHA mismatch"):
        calculation(api, activation, run, auth, receipt, host(receipt, run), launched)
    assert launched == [] and api.ref == old_ref
    with pytest.raises(guard.GuardRefused):
        guard.Guard(ROOT, api, activation).reserve(run, auth)


def test_full_and_calculation_only_reruns_refuse_retained_outputs(identities):
    run, auth, activation = setup_run(identities)
    api, launched = FakeGitHub(), []
    receipt = guard.Guard(ROOT, api, activation).reserve(run, auth)
    count = len(api.calls)
    rerun = replace(run, run_attempt=2)
    with pytest.raises(guard.GuardRefused, match="rerun"):
        guard.Guard(ROOT, api, activation).reserve(rerun, auth)
    with pytest.raises(guard.GuardRefused, match="rerun"):
        calculation(api, activation, rerun, auth, receipt, host(receipt, run), launched)
    assert launched == [] and len(api.calls) == count and api.ref is not None


@pytest.mark.parametrize(
    "field,value",
    [
        ("run_id", 1235),
        ("claim_sha", "c" * 40),
        ("claim_sha256", "0" * 64),
        ("ref", "refs/heads/main"),
    ],
)
def test_forged_reservation_receipt_is_not_a_calculation_permit(identities, field, value):
    run, auth, activation = setup_run(identities)
    api, launched = FakeGitHub(), []
    receipt = guard.Guard(ROOT, api, activation).reserve(run, auth)
    item = json.loads(receipt)
    item[field] = value
    with pytest.raises(guard.GuardRefused):
        calculation(api, activation, run, auth, guard.canonical(item), host(receipt, run), launched)
    assert launched == [] and api.ref is not None


@pytest.mark.parametrize("change", ["message", "parent", "tree", "ref", "missing_ref"])
def test_remote_claim_substitution_is_refused(identities, change):
    run, auth, activation = setup_run(identities)
    api, launched = FakeGitHub(), []
    receipt = guard.Guard(ROOT, api, activation).reserve(run, auth)
    commit = api.commits[json.loads(receipt)["claim_sha"]]
    if change == "message":
        commit["message"] = commit["message"] + " "
    elif change == "parent":
        commit["parents"] = [{"sha": "c" * 40}]
    elif change == "tree":
        commit["tree"]["sha"] = "c" * 40
    elif change == "ref":
        api.ref["object"]["sha"] = "c" * 40
    else:
        api.ref = None
    with pytest.raises(guard.GuardRefused):
        calculation(api, activation, run, auth, receipt, host(receipt, run), launched)
    assert launched == []


@pytest.mark.parametrize(
    "field,value",
    [
        ("linux", None),
        ("cgroup_v2_ancestry_verified", False),
        ("group_and_descendants_stopped", None),
        ("output_fresh", False),
        ("output_symlink_free", False),
        ("output_outside_data", None),
        ("effective_memory_available", (4 << 30) - 1),
        ("effective_memory_available", True),
        ("disk_free", (2 << 30) - 1),
        ("disk_free", None),
        ("output", "/tmp/data/campaign"),
        ("output", "/tmp/../campaign"),
        ("output", "relative"),
        ("claim_sha", "c" * 40),
        ("run_id", 999),
        ("activation_sha", "c" * 40),
    ],
)
def test_unknown_or_insufficient_host_proof_never_reaches_sentinel(identities, field, value):
    run, auth, activation = setup_run(identities)
    api, launched = FakeGitHub(), []
    receipt = guard.Guard(ROOT, api, activation).reserve(run, auth)
    proof = host(receipt, run)
    proof[field] = value
    with pytest.raises(guard.GuardRefused):
        calculation(api, activation, run, auth, receipt, proof, launched)
    assert launched == [] and api.ref is not None


@pytest.mark.parametrize("field", list(guard.LIMITS))
def test_every_resource_limit_is_exact_and_cannot_be_raised(identities, field):
    run, auth, activation = setup_run(identities)
    api, launched = FakeGitHub(), []
    receipt = guard.Guard(ROOT, api, activation).reserve(run, auth)
    proof = host(receipt, run)
    proof["limits"][field] += 1
    with pytest.raises(guard.GuardRefused, match="limits changed"):
        calculation(api, activation, run, auth, receipt, proof, launched)
    assert launched == []


def test_failed_host_proof_consumes_claim_and_guard_cannot_reenter(identities):
    run, auth, activation = setup_run(identities)
    api = FakeGitHub()
    receipt = guard.Guard(ROOT, api, activation).reserve(run, auth)
    instance = guard.Guard(ROOT, api, activation)
    with pytest.raises(guard.GuardRefused):
        instance.calculation_gate(run, auth, receipt, {})
    with pytest.raises(guard.GuardRefused, match="already consumed"):
        instance.calculation_gate(run, auth, receipt, host(receipt, run))
    with pytest.raises(guard.GuardRefused, match="claim exists"):
        guard.Guard(ROOT, api, activation).reserve(run, auth)
    assert api.ref is not None and instance.events


def test_sentinel_failure_keeps_claim_and_evidence_consumed(identities):
    run, auth, activation = setup_run(identities)
    api = FakeGitHub()
    reserver = guard.Guard(ROOT, api, activation)
    receipt = reserver.reserve(run, auth)
    calculation_guard = guard.Guard(ROOT, api, activation)
    permit = calculation_guard.calculation_gate(run, auth, receipt, host(receipt, run))
    with pytest.raises(RuntimeError, match="sentinel failure"):
        assert permit["workers_launched"] == 0
        raise RuntimeError("sentinel failure after reservation")
    with pytest.raises(guard.GuardRefused, match="already consumed"):
        calculation_guard.calculation_gate(run, auth, receipt, host(receipt, run))
    assert api.ref is not None and receipt
    assert reserver.events[-1]["state"] == "RESERVED"
    assert all(
        {"utc", "task_id", "agent_id"} <= event.keys()
        for event in reserver.events + calculation_guard.events
    )


def test_workflow_proposal_is_outside_actions_and_fail_closed():
    proposal = json.loads(PROPOSAL.read_bytes())  # JSON is also valid YAML.
    assert ".github" not in PROPOSAL.parts
    assert set(proposal["on"]) == {"workflow_dispatch"}
    assert proposal["concurrency"] == {"group": guard.CAMPAIGN, "cancel-in-progress": False}
    for name in ("reserve", "calculate"):
        job = proposal["jobs"][name]
        assert job["if"].startswith("${{ false &&") and "github.run_attempt == 1" in job["if"]
        assert job["steps"][-1]["run"] == "exit 1"
    assert proposal["jobs"]["reserve"]["permissions"] == {"contents": "write"}
    assert proposal["jobs"]["calculate"]["permissions"] == {"contents": "read"}
