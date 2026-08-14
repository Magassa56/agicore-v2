"""Deterministic factual cost-scenario comparison for breakout walk-forward."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

from .breakout_execution_costs import BreakoutExecutionCostModel
from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file
from .walk_forward_breakout import WalkForwardBreakoutError, create_walk_forward_breakout_study


class WalkForwardCostScenarioError(ValueError):
    """Raised when a factual cost-scenario comparison cannot be published."""


_SCENARIO_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")


def create_walk_forward_cost_scenario_study(
    csv_path: str | Path,
    output_dir: str | Path,
    scenarios_path: str | Path,
    *,
    reference_scenario: str,
    initial_train_bars: int,
    validation_bars: int,
    oos_bars: int,
    lookback_bars: int = 240,
    side_policy: str = "BOTH",
) -> Path:
    """Compare fixed detailed-cost scenarios without changing the replay path."""
    final = Path(output_dir).resolve()
    scratch_root: Path | None = None
    try:
        if final.exists():
            raise WalkForwardCostScenarioError(f"Output directory already exists: {final}")
        _validate_scenario_name(reference_scenario)

        source = Path(csv_path).resolve()
        scenario_file = Path(scenarios_path).resolve()
        scenarios = _load_scenarios(scenario_file)
        if reference_scenario not in scenarios:
            raise WalkForwardCostScenarioError("reference scenario is not present")
        _validate_cost_order(scenarios)

        source_sha256 = sha256_file(source)
        final.parent.mkdir(parents=True, exist_ok=True)
        scratch_root = Path(tempfile.mkdtemp(prefix=f".{final.name}.scenarios-", dir=final.parent))
        scenario_rows = []
        for index, (scenario_name, model) in enumerate(scenarios.items()):
            bundle = create_walk_forward_breakout_study(
                source,
                scratch_root / f"scenario-{index:04d}",
                initial_train_bars=initial_train_bars,
                validation_bars=validation_bars,
                oos_bars=oos_bars,
                lookback_bars=lookback_bars,
                round_trip_cost_points=0.0,
                side_policy=side_policy,
                execution_cost_model=model,
            )
            scenario_rows.append(_scenario_row(scenario_name, model, bundle))

        reference = next(row for row in scenario_rows if row["scenario_name"] == reference_scenario)
        for row in scenario_rows:
            _assert_same_replay(reference, row)
        _cleanup_scratch(scratch_root)
        scratch_root = None
        for row in scenario_rows:
            row["reference_deltas"] = {
                "gross_total_pnl_points": _gross(row) - _gross(reference),
                "total_cost_points": _cost(row) - _cost(reference),
                "net_total_pnl_points": _net(row) - _net(reference),
                "total_trades": _trades(row) - _trades(reference),
                "end_of_data_close_count": _end_of_data_closes(row) - _end_of_data_closes(reference),
            }

        configuration = {
            "reference_scenario": reference_scenario,
            "initial_train_bars": initial_train_bars,
            "validation_bars": validation_bars,
            "oos_bars": oos_bars,
            "lookback_bars": lookback_bars,
            "side_policy": side_policy,
            "mode": "expanding",
            "execution": "next_bar_open",
            "scenarios": {name: model.serialize() for name, model in scenarios.items()},
        }
        configuration_sha256 = _sha256(configuration)
        run_id = f"breakout-cost-scenarios-{_sha256({'source_sha256': source_sha256, 'configuration': configuration})[:16]}"
        summary = {
            "schema_version": "1.0",
            "source_sha256": source_sha256,
            "configuration": configuration,
            "scenarios": [_scenario_summary(row) for row in scenario_rows],
            "warning": "Factual cost comparison only; no proof of profitability or paper-trading readiness.",
        }
        manifest = {
            "schema_version": "1.0",
            "run_id": run_id,
            "source_sha256": source_sha256,
            "configuration": configuration,
            "configuration_sha256": configuration_sha256,
            "status": "completed",
            "generated_files": ["manifest.json", "results.json", "summary.json"],
            "warnings": [
                "Scenarios are factual inputs; none is automatically selected, ranked, optimized, or recommended.",
                "This comparison is not proof of profitability or paper-trading readiness.",
            ],
        }
        return publish_local_bundle(
            final,
            {
                "results.json": deterministic_json(scenario_rows),
                "summary.json": deterministic_json(summary),
                "manifest.json": deterministic_json(manifest),
            },
        )
    except (OSError, TypeError, ValueError, LocalBundleError, WalkForwardBreakoutError) as exc:
        if isinstance(exc, WalkForwardCostScenarioError):
            raise
        raise WalkForwardCostScenarioError(str(exc)) from exc
    finally:
        if scratch_root is not None and scratch_root.exists():
            _cleanup_scratch(scratch_root)


def _load_scenarios(path: Path) -> dict[str, BreakoutExecutionCostModel]:
    if not path.is_file():
        raise WalkForwardCostScenarioError(f"Scenario JSON file not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        raise WalkForwardCostScenarioError("Scenario JSON is invalid") from exc
    except ValueError as exc:
        raise WalkForwardCostScenarioError(str(exc)) from exc
    items = raw.get("scenarios") if isinstance(raw, dict) else raw
    if not isinstance(items, dict) or len(items) < 3:
        raise WalkForwardCostScenarioError("At least three named scenarios are required")
    required_names = {"low_cost", "reference", "stress"}
    if not required_names.issubset(items):
        raise WalkForwardCostScenarioError("Scenarios must include low_cost, reference, and stress")
    models = {}
    for name, value in items.items():
        _validate_scenario_name(name)
        if not isinstance(value, dict):
            raise WalkForwardCostScenarioError("Scenario model must be an object")
        try:
            model = BreakoutExecutionCostModel(**value)
        except (TypeError, ValueError) as exc:
            raise WalkForwardCostScenarioError(f"Invalid scenario {name!r}: {exc}") from exc
        if model.scenario_name != name:
            raise WalkForwardCostScenarioError(
                f"Scenario key {name!r} must equal model scenario_name {model.scenario_name!r}"
            )
        models[name] = model
    return dict(sorted(models.items()))


def _validate_scenario_name(name: object) -> None:
    if not isinstance(name, str) or not _SCENARIO_NAME.fullmatch(name):
        raise WalkForwardCostScenarioError(
            "Scenario names must be portable identifiers beginning with a letter and containing only letters, digits, underscores, or hyphens"
        )


def _validate_cost_order(scenarios: dict[str, BreakoutExecutionCostModel]) -> None:
    low = scenarios["low_cost"].total_round_trip_cost_points
    reference = scenarios["reference"].total_round_trip_cost_points
    stress = scenarios["stress"].total_round_trip_cost_points
    if not low < reference < stress:
        raise WalkForwardCostScenarioError(
            "Scenario costs must satisfy low_cost < reference < stress"
        )


def _cleanup_scratch(path: Path) -> None:
    try:
        shutil.rmtree(path)
    except OSError as exc:
        raise WalkForwardCostScenarioError(
            f"Unable to clean temporary scenario bundles: {exc}"
        ) from exc


def _assert_same_replay(reference: dict[str, object], candidate: dict[str, object]) -> None:
    reference_rows = _rows(reference)
    candidate_rows = _rows(candidate)
    if len(reference_rows) != len(candidate_rows):
        raise WalkForwardCostScenarioError("Cost scenarios produced a different number of walk-forward segments")
    row_fields = (
        "fold_index", "role", "source_start_index", "source_end_index",
        "start_timestamp", "end_timestamp", "bar_count", "starts_flat",
        "local_lookback_warmup_bar_count", "cross_boundary_warmup_bar_count",
        "boundary_forced_close_count", "decisions",
    )
    trade_fields = (
        "side", "entry_timestamp", "exit_timestamp", "entry_bar_index",
        "exit_bar_index", "entry_price", "exit_price", "exit_reason",
        "gross_pnl_points",
    )
    for reference_row, candidate_row in zip(reference_rows, candidate_rows, strict=True):
        if any(reference_row[field] != candidate_row[field] for field in row_fields):
            raise WalkForwardCostScenarioError("Cost scenarios changed walk-forward decisions or boundaries")
        reference_trades = reference_row["trades"]
        candidate_trades = candidate_row["trades"]
        if len(reference_trades) != len(candidate_trades):
            raise WalkForwardCostScenarioError("Cost scenarios produced a different number of trades")
        for reference_trade, candidate_trade in zip(reference_trades, candidate_trades, strict=True):
            if any(reference_trade[field] != candidate_trade[field] for field in trade_fields):
                raise WalkForwardCostScenarioError("Cost scenarios changed trade economics before costs")


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Scenario JSON contains a duplicate key: {key}")
        result[key] = value
    return result


def _scenario_row(name: str, model: BreakoutExecutionCostModel, bundle: Path) -> dict[str, object]:
    return {
        "scenario_name": name,
        "scenario_sha256": _sha256(model.serialize()),
        "cost_breakdown": model.serialize(),
        "effective_round_trip_cost_points": model.total_round_trip_cost_points,
        "results": json.loads((bundle / "results.json").read_text(encoding="utf-8")),
        "summary": json.loads((bundle / "summary.json").read_text(encoding="utf-8")),
        "manifest": json.loads((bundle / "manifest.json").read_text(encoding="utf-8")),
    }


def _scenario_summary(row: dict[str, object]) -> dict[str, object]:
    return {
        "scenario_name": row["scenario_name"],
        "scenario_sha256": row["scenario_sha256"],
        "cost_breakdown": row["cost_breakdown"],
        "effective_round_trip_cost_points": row["effective_round_trip_cost_points"],
        "total_trades": _trades(row),
        "gross_total_pnl_points": _gross(row),
        "total_cost_points": _cost(row),
        "net_total_pnl_points": _net(row),
        "end_of_data_close_count": _end_of_data_closes(row),
        "reference_deltas": row["reference_deltas"],
    }


def _rows(row: dict[str, object]) -> list[dict[str, object]]:
    return row["results"]  # type: ignore[return-value]


def _trades(row: dict[str, object]) -> int:
    return sum(item["metrics"]["total_trades"] for item in _rows(row))


def _gross(row: dict[str, object]) -> float:
    return sum(item["metrics"]["gross_total_pnl_points"] for item in _rows(row))


def _net(row: dict[str, object]) -> float:
    return sum(item["metrics"]["net_total_pnl_points"] for item in _rows(row))


def _cost(row: dict[str, object]) -> float:
    return _gross(row) - _net(row)


def _end_of_data_closes(row: dict[str, object]) -> int:
    return sum(item["boundary_forced_close_count"] for item in _rows(row))


def _sha256(value: object) -> str:
    return hashlib.sha256(deterministic_json(value).encode("utf-8")).hexdigest()


__all__ = ["WalkForwardCostScenarioError", "create_walk_forward_cost_scenario_study"]
