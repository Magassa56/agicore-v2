"""Offline validation for AGIcore Delivery Factory files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


REQUIRED_FILES = (
    "docs/AGICORE_DELIVERY_FACTORY.md",
    "docs/AGICORE_TRADING_ROADMAP.md",
    "docs/AGICORE_DEFINITION_OF_DONE.md",
    ".github/pull_request_template.md",
    ".github/ISSUE_TEMPLATE/agicore_phase.yml",
    ".github/workflows/agicore-ci.yml",
)

DANGEROUS_TERMS = (
    "real broker execution",
    "live order execution",
    "read real API key",
    "connect real Alpaca",
    "external trading API",
)

DATA_ACCESS_OBLIGATIONS = (
    "must access data/",
    "requires data/",
    "require data/",
    "obligatoire data/",
)


@dataclass(frozen=True)
class DeliveryValidationResult:
    ok: bool
    missing_files: tuple[str, ...]
    dangerous_terms: tuple[str, ...]
    data_access_obligations: tuple[str, ...]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def validate_delivery_factory(root: str | Path | None = None) -> DeliveryValidationResult:
    """Validate Delivery Factory artifacts without network, secrets or runtime variable reads."""

    base = Path.cwd() if root is None else Path(root)
    missing = tuple(relative for relative in REQUIRED_FILES if not (base / relative).is_file())
    texts = []
    for relative in REQUIRED_FILES:
        path = base / relative
        if path.is_file():
            texts.append((relative, _read_text(path)))

    dangerous = []
    data_obligations = []
    for relative, text in texts:
        lowered = text.lower()
        for term in DANGEROUS_TERMS:
            if term.lower() in lowered:
                dangerous.append(f"{relative}: {term}")
        for term in DATA_ACCESS_OBLIGATIONS:
            if term in lowered:
                data_obligations.append(f"{relative}: {term}")

    return DeliveryValidationResult(
        ok=not missing and not dangerous and not data_obligations,
        missing_files=missing,
        dangerous_terms=tuple(dangerous),
        data_access_obligations=tuple(data_obligations),
    )


def main() -> int:
    result = validate_delivery_factory()
    if result.ok:
        print("AGICORE_DELIVERY_FACTORY_VALIDATION_OK")
        return 0
    print("AGICORE_DELIVERY_FACTORY_VALIDATION_FAILED")
    for missing in result.missing_files:
        print(f"missing: {missing}")
    for term in result.dangerous_terms:
        print(f"dangerous: {term}")
    for obligation in result.data_access_obligations:
        print(f"data_access_obligation: {obligation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
