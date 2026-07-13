from __future__ import annotations

import ast
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REQUIRED_FILES = (
    "docs/AGICORE_DELIVERY_FACTORY.md",
    "docs/AGICORE_TRADING_ROADMAP.md",
    "docs/AGICORE_DEFINITION_OF_DONE.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/agicore_phase.yml",
    ".github/workflows/agicore-ci.yml",
    "scripts/agicore_validate_delivery.py",
)


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def _load_validator():
    path = ROOT / "scripts/agicore_validate_delivery.py"
    spec = importlib.util.spec_from_file_location("agicore_validate_delivery", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_required_delivery_factory_files_exist():
    for relative in REQUIRED_FILES:
        assert (ROOT / relative).is_file(), relative


def test_validator_returns_ok_when_files_are_present():
    module = _load_validator()
    result = module.validate_delivery_factory(ROOT)

    assert result.ok is True
    assert result.missing_files == ()
    assert result.dangerous_terms == ()
    assert result.data_access_obligations == ()


def test_ci_workflow_exists_and_runs_required_checks():
    workflow = _read(".github/workflows/agicore-ci.yml")

    assert "pull_request" in workflow
    assert "branches:" in workflow
    assert "- main" in workflow
    assert "python -m pip install --upgrade pip" in workflow
    assert "python -m pip install -r requirements-dev.txt" in workflow
    assert "python -m pip install -e ." in workflow
    assert "python -m pytest -q" in workflow
    assert "python -m pytest tests/unit/ -q" not in workflow
    assert "git diff --check" in workflow
    assert "secrets." not in workflow


def test_cloud_run_deployment_requires_manual_confirmation_from_main():
    workflow = _read(".github/workflows/main-ci-cd.yml")

    assert "workflow_dispatch:" in workflow
    assert "confirm_deploy:" in workflow
    assert "inputs.confirm_deploy == true" in workflow
    assert "github.ref == 'refs/heads/main'" in workflow
    assert "\n  push:" not in workflow
    assert "\n  pull_request:" not in workflow


def test_pr_template_contains_security_confirmations():
    template = _read(".github/pull_request_template.md")

    assert "Aucun broker reel" in template
    assert "Aucune cle API" in template
    assert "Aucun HTTP/websocket/socket" in template
    assert "Aucun ordre reel" in template
    assert "Aucun acces compte reel" in template
    assert "`data/` non touche" in template


def test_issue_template_contains_required_phase_fields():
    template = _read(".github/ISSUE_TEMPLATE/agicore_phase.yml")

    for field in (
        "phase_name",
        "objective",
        "context",
        "allowed_files",
        "forbidden_files",
        "required_functions_or_deliverables",
        "safety_constraints",
        "required_tests",
        "acceptance_criteria",
        "stop_condition",
        "expected_final_decision",
        "next_phase",
    ):
        assert field in template


def test_roadmap_contains_concrete_next_phases():
    roadmap = _read("docs/AGICORE_TRADING_ROADMAP.md")

    for phase in (
        "Delivery Factory v1",
        "Controlled Offline Runner Minimal Implementation",
        "Synthetic Market Scenario",
        "Simulated Broker Stub",
        "Risk Guard Enforcement",
        "Journal Writer",
        "Offline Report Markdown/JSON",
        "CSV Replay Input",
        "Strategy Replay Engine",
        "AGIcore Trading v1 Candidate",
    ):
        assert phase in roadmap
    assert "Ne pas ajouter de nouvelle gate abstraite" in roadmap


def test_definition_of_done_contains_safety_criteria():
    dod = _read("docs/AGICORE_DEFINITION_OF_DONE.md")

    for criterion in (
        "Aucune cle API",
        "Aucun HTTP",
        "Aucun websocket",
        "Aucun socket",
        "Aucune API externe",
        "Aucun ordre reel",
        "Aucun acces compte reel",
        "Aucune mutation de position reelle",
        "`data/` non touche",
    ):
        assert criterion in dod


def test_validator_script_uses_no_network_or_environment_access():
    source = _read("scripts/agicore_validate_delivery.py")
    tree = ast.parse(source)
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_from_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }

    forbidden_imports = {"os", "socket", "requests", "httpx", "urllib", "websocket"}
    assert imported_modules.isdisjoint(forbidden_imports)
    assert imported_from_modules.isdisjoint(forbidden_imports)
    assert "environ" not in source
    assert "getenv" not in source
    assert "http://" not in source
    assert "https://" not in source
