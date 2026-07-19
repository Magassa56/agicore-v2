"""Regression guards for public repository trading-data privacy."""

from __future__ import annotations

import re
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
PRIVATE_REPORT = REPOSITORY_ROOT / "reports" / "bama_trader_profile_v1.md"
PUBLIC_EXAMPLE = REPOSITORY_ROOT / "reports" / "examples" / "nt8_sample_analysis.md"
PRIVACY_DOCUMENT = REPOSITORY_ROOT / "docs" / "PRIVACY_LOCAL_TRADING_DATA.md"

REQUIRED_IGNORE_RULES = {
    "/data/",
    "/reports/local/",
    "/reports/private/",
    "*.local.md",
    "*.local.json",
    "*trader_profile*.md",
    "!/reports/examples/",
    "!/reports/examples/**",
}


def _read_utf8(path: Path) -> str:
    """Read a public repository text fixture as UTF-8."""

    return path.read_text(encoding="utf-8")


def test_personal_trader_report_is_absent() -> None:
    """The known personal trader profile must not remain in the worktree."""

    assert not PRIVATE_REPORT.exists()


def test_gitignore_protects_local_trading_material() -> None:
    """Local trading paths are ignored while fictional examples stay public."""

    gitignore = _read_utf8(REPOSITORY_ROOT / ".gitignore")
    active_rules = {
        line.strip()
        for line in gitignore.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert REQUIRED_IGNORE_RULES <= active_rules


def test_public_example_is_fictional_and_safely_located() -> None:
    """The public example contains no known name or personal filesystem path."""

    assert PUBLIC_EXAMPLE.is_file()
    assert PUBLIC_EXAMPLE.parent == REPOSITORY_ROOT / "reports" / "examples"

    example = _read_utf8(PUBLIC_EXAMPLE)
    folded = example.casefold()

    assert "fictional" in folded
    assert "bama" not in folded
    assert "data/" not in folded
    assert "data\\" not in folded
    assert not re.search(r"(?i)[a-z]:[\\/]", example)
    assert not re.search(r"(?i)/(?:users|home)/[^/]+/", example)


def test_privacy_document_explains_git_history_limit() -> None:
    """Documentation must distinguish a HEAD deletion from history rewriting."""

    documentation = _read_utf8(PRIVACY_DOCUMENT).casefold()

    assert "a simple file deletion does not remove earlier copies from git history" in documentation
    assert "does not rewrite git history" in documentation
    assert "git-filter-repo" in documentation
    assert "bfg" in documentation
    assert "revoke and regenerate" in documentation
