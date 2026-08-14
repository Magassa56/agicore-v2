from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest

from agicore.cli.main import main
from agicore.trading.walk_forward_cost_scenarios import (
    WalkForwardCostScenarioError,
    create_walk_forward_cost_scenario_study,
)
from agicore.trading import walk_forward_cost_scenarios as scenarios_module


def _write_csv(path, count=600, *, mutation=0.0):
    start = datetime(2026, 1, 1)
    rows = ["timestamp,open,high,low,close,volume"]
    for index in range(count):
        value = 100.0 if index < 240 else (104.0 if index % 4 < 2 else 96.0)
        if index >= 500:
            value += mutation
        rows.append(f"{start + timedelta(minutes=index)},{value},{value + 1},{value - 1},{value},1")
    path.write_text("\n".join(rows), encoding="utf-8")


def _model(name, *, commission=0.5, entry=0.125, exit=0.125):
    return {
        "scenario_name": name,
        "instrument": "MNQ",
        "currency": "USD",
        "point_value_currency_per_point": 2.0,
        "commission_currency_per_side": commission,
        "round_trip_spread_points": 0.25,
        "entry_slippage_points": entry,
        "exit_slippage_points": exit,
    }


def _write_scenarios(path, *, reference="reference", reordered=False, same_total=False):
    scenarios = {
        "low_cost": _model("low_cost", commission=0.1),
        "reference": _model("reference"),
        "stress": _model("stress", commission=1.0),
    }
    if same_total:
        scenarios["reference"] = _model("reference", entry=0.10, exit=0.15)
    if reordered:
        scenarios = {"stress": scenarios["stress"], "reference": scenarios["reference"], "low_cost": scenarios["low_cost"]}
    path.write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")


def _write_raw_scenarios(path, scenarios):
    path.write_text(json.dumps({"scenarios": scenarios}), encoding="utf-8")


def _create(tmp_path, name, scenarios, **overrides):
    args = {
        "reference_scenario": "reference",
        "initial_train_bars": 300,
        "validation_bars": 100,
        "oos_bars": 100,
        "lookback_bars": 2,
    }
    args.update(overrides)
    return create_walk_forward_cost_scenario_study(tmp_path / "bars.csv", tmp_path / name, scenarios, **args)


def _load(bundle):
    return tuple(json.loads((bundle / name).read_text(encoding="utf-8")) for name in ("results.json", "summary.json", "manifest.json"))


def _trades(scenario):
    return [trade for row in scenario["results"] for trade in row["trades"]]


def _replay_projection(scenario):
    fields = ("side", "entry_timestamp", "exit_timestamp", "entry_bar_index", "exit_bar_index", "entry_price", "exit_price", "exit_reason", "gross_pnl_points")
    return [[tuple(trade[field] for field in fields) for trade in row["trades"]] for row in scenario["results"]], [row["decisions"] for row in scenario["results"]]


def test_cost_scenarios_preserve_replay_and_compare_net_costs(tmp_path):
    _write_csv(tmp_path / "bars.csv")
    scenarios = tmp_path / "scenarios.json"
    _write_scenarios(scenarios)
    results, summary, manifest = _load(_create(tmp_path, "out", scenarios))

    assert manifest["configuration"] == summary["configuration"]
    assert manifest["run_id"] and manifest["configuration_sha256"]
    assert [row["scenario_name"] for row in results] == ["low_cost", "reference", "stress"]
    trade_groups = [_trades(row) for row in results]
    assert all(group for group in trade_groups)
    assert all(row["results"] and all(segment["decisions"] for segment in row["results"]) for row in results)
    assert any(trade["exit_reason"] == "END_OF_DATA" for group in trade_groups for trade in group)
    assert [_replay_projection(row) for row in results].count(_replay_projection(results[0])) == 3
    assert all(trade["gross_pnl_points"] - trade["cost_points"] == pytest.approx(trade["net_pnl_points"]) for group in trade_groups for trade in group)

    costs = [row["effective_round_trip_cost_points"] for row in results]
    nets = [row["net_total_pnl_points"] for row in summary["scenarios"]]
    total_costs = [row["total_cost_points"] for row in summary["scenarios"]]
    assert costs == sorted(costs) and costs[0] < costs[1] < costs[2]
    assert total_costs[0] < total_costs[1] < total_costs[2]
    assert nets[0] >= nets[1] >= nets[2]
    assert all(row["reference_deltas"]["total_trades"] == 0 for row in summary["scenarios"])
    assert all(row["cost_breakdown"]["cost_mode"] == "detailed" for row in results)
    assert all(row["effective_round_trip_cost_points"] == row["cost_breakdown"]["total_round_trip_cost_points"] for row in results)


def test_scenario_identity_is_deterministic_sensitive_and_json_order_independent(tmp_path):
    _write_csv(tmp_path / "bars.csv")
    first, reordered, reallocated = (tmp_path / name for name in ("first.json", "reordered.json", "reallocated.json"))
    _write_scenarios(first)
    _write_scenarios(reordered, reordered=True)
    _write_scenarios(reallocated, same_total=True)
    _, _, first_manifest = _load(_create(tmp_path, "one", first))
    _, _, repeated_manifest = _load(_create(tmp_path, "repeat", first))
    _, _, reordered_manifest = _load(_create(tmp_path, "two", reordered))
    changed_results, _, changed_manifest = _load(_create(tmp_path, "three", reallocated))
    assert first_manifest["run_id"] == repeated_manifest["run_id"] == reordered_manifest["run_id"]
    assert first_manifest["run_id"] != changed_manifest["run_id"]
    assert first_manifest["configuration_sha256"] != changed_manifest["configuration_sha256"]
    original_results, _, _ = _load(_create(tmp_path, "four", first))
    assert original_results[1]["effective_round_trip_cost_points"] == changed_results[1]["effective_round_trip_cost_points"] != 0
    assert _replay_projection(original_results[1]) == _replay_projection(changed_results[1])
    assert [trade["net_pnl_points"] for trade in _trades(original_results[1])] == [trade["net_pnl_points"] for trade in _trades(changed_results[1])]
    assert original_results[1]["scenario_sha256"] != changed_results[1]["scenario_sha256"]


def test_source_and_reference_change_identity(tmp_path):
    _write_csv(tmp_path / "bars.csv")
    scenarios = tmp_path / "scenarios.json"
    _write_scenarios(scenarios)
    _, _, first = _load(_create(tmp_path, "one", scenarios))
    _, _, reference_changed = _load(_create(tmp_path, "two", scenarios, reference_scenario="low_cost"))
    _write_csv(tmp_path / "bars.csv", mutation=0.5)
    _, _, source_changed = _load(_create(tmp_path, "three", scenarios))
    assert first["run_id"] != reference_changed["run_id"]
    assert first["run_id"] != source_changed["run_id"]
    assert reference_changed["run_id"] != source_changed["run_id"]


@pytest.mark.parametrize(
    "content, reference_scenario",
    [
        ("{", "reference"),
        (json.dumps({"scenarios": {"reference": _model("reference")}}), "reference"),
        (json.dumps({"scenarios": {"low_cost": _model("low_cost"), "reference": _model("reference"), "stress": _model("stress"), " ": _model("extra")}}), "reference"),
        (json.dumps({"scenarios": {"low_cost": _model("low_cost"), "reference": _model("reference"), "stress": _model("stress", commission=-1)}}), "reference"),
        (json.dumps({"scenarios": {"low_cost": _model("low_cost"), "reference": _model("reference"), "stress": _model("stress")}}), "missing"),
    ],
)
def test_invalid_scenarios_publish_nothing(tmp_path, content, reference_scenario):
    _write_csv(tmp_path / "bars.csv")
    scenarios = tmp_path / "invalid.json"
    scenarios.write_text(content, encoding="utf-8")
    output = tmp_path / "out"
    with pytest.raises(WalkForwardCostScenarioError):
        _create(tmp_path, "out", scenarios, reference_scenario=reference_scenario)
    assert not output.exists()


def test_duplicate_names_and_insufficient_source_publish_nothing(tmp_path):
    _write_csv(tmp_path / "bars.csv", count=499)
    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(
        '{"scenarios":{"low_cost":{},"low_cost":{},"reference":{},"stress":{}}}',
        encoding="utf-8",
    )
    with pytest.raises(WalkForwardCostScenarioError):
        _create(tmp_path, "duplicate-out", duplicate)
    assert not (tmp_path / "duplicate-out").exists()

    scenarios = tmp_path / "scenarios.json"
    _write_scenarios(scenarios)
    with pytest.raises(WalkForwardCostScenarioError):
        _create(tmp_path, "short-out", scenarios)
    assert not (tmp_path / "short-out").exists()


@pytest.mark.parametrize("invalid_name", ["../escape", r"..\\escape", r"C:\\escape", "/absolute"])
def test_unsafe_scenario_names_publish_nothing(tmp_path, invalid_name):
    _write_csv(tmp_path / "bars.csv")
    scenarios = {
        "low_cost": _model("low_cost", commission=0.1),
        "reference": _model("reference"),
        "stress": _model("stress", commission=1.0),
        invalid_name: _model(invalid_name),
    }
    path = tmp_path / "unsafe.json"
    _write_raw_scenarios(path, scenarios)
    with pytest.raises(WalkForwardCostScenarioError):
        _create(tmp_path, "out", path)
    assert not (tmp_path / "out").exists()


@pytest.mark.parametrize(
    "mutate",
    [
        lambda model: model.pop("currency"),
        lambda model: model.__setitem__("unknown", 1),
        lambda model: model.__setitem__("scenario_name", "other"),
    ],
)
def test_invalid_model_contracts_publish_nothing(tmp_path, mutate):
    _write_csv(tmp_path / "bars.csv")
    scenarios = {
        "low_cost": _model("low_cost", commission=0.1),
        "reference": _model("reference"),
        "stress": _model("stress", commission=1.0),
    }
    mutate(scenarios["reference"])
    path = tmp_path / "invalid-model.json"
    _write_raw_scenarios(path, scenarios)
    with pytest.raises(WalkForwardCostScenarioError):
        _create(tmp_path, "out", path)
    assert not (tmp_path / "out").exists()


def test_cost_order_and_replay_divergence_publish_nothing(tmp_path, monkeypatch):
    _write_csv(tmp_path / "bars.csv")
    unordered = tmp_path / "unordered.json"
    _write_raw_scenarios(
        unordered,
        {
            "low_cost": _model("low_cost", commission=1.0),
            "reference": _model("reference", commission=0.5),
            "stress": _model("stress", commission=0.1),
        },
    )
    with pytest.raises(WalkForwardCostScenarioError, match="low_cost < reference < stress"):
        _create(tmp_path, "unordered-out", unordered)
    assert not (tmp_path / "unordered-out").exists()

    valid = tmp_path / "valid.json"
    _write_scenarios(valid)
    original = scenarios_module.create_walk_forward_breakout_study

    def divergent(*args, **kwargs):
        bundle = original(*args, **kwargs)
        if kwargs["execution_cost_model"].scenario_name == "stress":
            results_path = bundle / "results.json"
            rows = json.loads(results_path.read_text(encoding="utf-8"))
            rows[0]["decisions"] = [*rows[0]["decisions"], {"action": "DIVERGENCE"}]
            results_path.write_text(json.dumps(rows), encoding="utf-8")
        return bundle

    monkeypatch.setattr(scenarios_module, "create_walk_forward_breakout_study", divergent)
    with pytest.raises(WalkForwardCostScenarioError, match="changed walk-forward decisions"):
        _create(tmp_path, "divergent-out", valid)
    assert not (tmp_path / "divergent-out").exists()


def test_cleanup_failure_is_controlled_and_prevents_publication(tmp_path, monkeypatch):
    _write_csv(tmp_path / "bars.csv")
    scenarios = tmp_path / "scenarios.json"
    _write_scenarios(scenarios)
    original_rmtree = scenarios_module.shutil.rmtree
    calls = {"count": 0}

    def fail_once(path):
        calls["count"] += 1
        if calls["count"] == 1:
            raise OSError("simulated cleanup failure")
        original_rmtree(path)

    monkeypatch.setattr(scenarios_module.shutil, "rmtree", fail_once)
    with pytest.raises(WalkForwardCostScenarioError, match="Unable to clean temporary scenario bundles"):
        _create(tmp_path, "out", scenarios)
    assert not (tmp_path / "out").exists()


def test_cli_errors_are_atomic_and_success_publishes_artifacts(tmp_path, capsys):
    source = tmp_path / "bars.csv"
    scenarios = tmp_path / "scenarios.json"
    _write_csv(source)
    _write_scenarios(scenarios)
    output = tmp_path / "cli"
    base = ["trading", "study-breakout-cost-scenarios", str(source), "--scenarios-json", str(scenarios), "--reference-scenario", "reference", "--initial-train-bars", "300", "--validation-bars", "100", "--oos-bars", "100", "--lookback-bars", "2"]
    assert main([*base, "--output-dir", str(output)]) == 0
    assert {path.name for path in output.iterdir()} == {"manifest.json", "results.json", "summary.json"}

    existing = tmp_path / "existing"
    existing.mkdir()
    sentinel = existing / "sentinel.txt"
    sentinel.write_text("unchanged", encoding="utf-8")
    assert main([*base, "--output-dir", str(existing)]) == 2
    assert capsys.readouterr().err.startswith("error:")
    assert list(existing.iterdir()) == [sentinel]
    assert sentinel.read_text(encoding="utf-8") == "unchanged"

    missing = tmp_path / "missing"
    assert main([*base, "--reference-scenario", "missing", "--output-dir", str(missing)]) == 2
    assert capsys.readouterr().err.startswith("error:") and not missing.exists()


def test_cli_rejects_invalid_file_and_invalid_walk_forward_sizes(tmp_path, capsys):
    source = tmp_path / "bars.csv"
    _write_csv(source)
    base = ["trading", "study-breakout-cost-scenarios", str(source), "--reference-scenario", "reference", "--initial-train-bars", "300", "--validation-bars", "100", "--oos-bars", "100", "--lookback-bars", "2"]
    missing_json_output = tmp_path / "missing-json"
    assert main([*base, "--scenarios-json", str(tmp_path / "missing.json"), "--output-dir", str(missing_json_output)]) == 2
    assert capsys.readouterr().err.startswith("error:") and not missing_json_output.exists()

    scenarios = tmp_path / "scenarios.json"
    _write_scenarios(scenarios)
    invalid_size_output = tmp_path / "invalid-size"
    assert main([*base, "--scenarios-json", str(scenarios), "--validation-bars", "0", "--output-dir", str(invalid_size_output)]) == 2
    assert capsys.readouterr().err.startswith("error:") and not invalid_size_output.exists()


def test_cli_model_errors_are_controlled_without_traceback(tmp_path, capsys):
    source = tmp_path / "bars.csv"
    _write_csv(source)
    scenarios = tmp_path / "invalid.json"
    _write_raw_scenarios(
        scenarios,
        {
            "low_cost": _model("low_cost", commission=0.1),
            "reference": {key: value for key, value in _model("reference").items() if key != "currency"},
            "stress": _model("stress", commission=1.0),
        },
    )
    output = tmp_path / "out"
    code = main(["trading", "study-breakout-cost-scenarios", str(source), "--scenarios-json", str(scenarios), "--reference-scenario", "reference", "--output-dir", str(output), "--initial-train-bars", "300", "--validation-bars", "100", "--oos-bars", "100", "--lookback-bars", "2"])
    stderr = capsys.readouterr().err
    assert code == 2 and stderr.startswith("error:") and "Traceback" not in stderr
    assert not output.exists()


def test_published_keys_remain_neutral(tmp_path):
    _write_csv(tmp_path / "bars.csv")
    scenarios = tmp_path / "scenarios.json"
    _write_scenarios(scenarios)
    results, summary, manifest = _load(_create(tmp_path, "out", scenarios))

    def keys(value):
        if isinstance(value, dict):
            for key, item in value.items():
                yield key
                yield from keys(item)
        elif isinstance(value, list):
            for item in value:
                yield from keys(item)

    forbidden = {"winner", "best", "ranking", "rank", "score", "selected", "recommended", "recommendation", "optimized", "optimization"}
    assert not (set(keys([results, summary, manifest])) & forbidden)
