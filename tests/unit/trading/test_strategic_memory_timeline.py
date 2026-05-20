"""Unit tests for the offline Strategic Memory Timeline."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from agicore.trading.strategic_memory_models import StrategicCyclePhase, StrategicDriftSignal
from agicore.trading.strategic_memory_timeline import (
    analyze_strategic_timeline,
    create_strategic_snapshot,
    detect_strategic_drift,
    load_strategic_timeline,
    render_strategic_timeline_markdown,
    save_strategic_timeline,
    update_strategic_timeline,
)


def _snapshot(
    session_id: str,
    offset: int,
    *,
    capital: float = 100_000,
    drawdown: float = 0,
    mode: str = "NORMAL",
    objective: str = "CONSISTENCY_BUILDING",
    policy: str = "BALANCED",
    reward: float = 20,
    consistency: float = 75,
    violations: int = 0,
    blocked: int = 1,
    executed: int = 2,
    behavior: str = "disciplined",
) -> object:
    return create_strategic_snapshot(
        timestamp=datetime(2026, 5, 21, tzinfo=UTC) + timedelta(days=offset),
        session_id=session_id,
        capital_estimate=capital,
        drawdown_estimate=drawdown,
        executive_mode=mode,
        strategic_objective=objective,
        risk_appetite="MODERATE",
        selected_policy=policy,
        average_reward=reward,
        consistency_score=consistency,
        safety_violations=violations,
        blocked_trades=blocked,
        executed_trades=executed,
        market_regime_summary="trend",
        behavior_summary=behavior,
        notes="offline snapshot",
    )


def test_create_strategic_snapshot_stores_required_fields() -> None:
    snapshot = _snapshot("s1", 0)

    assert snapshot.session_id == "s1"
    assert snapshot.capital_estimate == 100_000
    assert snapshot.selected_policy == "BALANCED"
    assert snapshot.notes == "offline snapshot"


def test_update_strategic_timeline_appends_and_sorts_snapshots() -> None:
    late = _snapshot("late", 2)
    early = _snapshot("early", 0)

    timeline = update_strategic_timeline(snapshots=(late, early))

    assert [item.session_id for item in timeline.snapshots] == ["early", "late"]
    assert len(timeline.events) == 2


def test_detect_strategic_improvement_and_consistency_gain() -> None:
    timeline = update_strategic_timeline(
        snapshots=(
            _snapshot("s1", 0, capital=100_000, drawdown=4, reward=10, consistency=60),
            _snapshot("s2", 1, capital=101_000, drawdown=2, reward=25, consistency=75),
        )
    )

    signals = detect_strategic_drift(timeline)

    assert StrategicDriftSignal.STRATEGIC_IMPROVEMENT in signals
    assert StrategicDriftSignal.CAPITAL_RECOVERY in signals
    assert StrategicDriftSignal.CONSISTENCY_GAIN in signals


def test_detect_degradation_reward_decline_and_persistent_drawdown() -> None:
    timeline = update_strategic_timeline(
        snapshots=(
            _snapshot("s1", 0, capital=100_000, drawdown=2, reward=35, consistency=80),
            _snapshot("s2", 1, capital=99_000, drawdown=6, reward=-5, consistency=55, violations=1),
            _snapshot("s3", 2, capital=98_500, drawdown=7, reward=-10, consistency=50, violations=2),
        )
    )

    signals = detect_strategic_drift(timeline)

    assert StrategicDriftSignal.STRATEGIC_DEGRADATION in signals
    assert StrategicDriftSignal.REWARD_DECLINE in signals
    assert StrategicDriftSignal.PERSISTENT_DRAWDOWN in signals


def test_detect_behavioral_drift_and_dangerous_policy() -> None:
    timeline = update_strategic_timeline(
        snapshots=(
            _snapshot("s1", 0, policy="AGGRESSIVE", reward=10, violations=0),
            _snapshot("s2", 1, policy="AGGRESSIVE", reward=-20, violations=2, behavior="revenge trading"),
            _snapshot("s3", 2, policy="AGGRESSIVE", reward=-30, violations=2, behavior="tilt"),
        )
    )

    signals = detect_strategic_drift(timeline)

    assert StrategicDriftSignal.BEHAVIORAL_DRIFT in signals
    assert StrategicDriftSignal.DANGEROUS_POLICY in signals


def test_analyze_timeline_identifies_best_worst_and_scores() -> None:
    timeline = update_strategic_timeline(
        snapshots=(
            _snapshot("bad", 0, capital=98_000, drawdown=8, reward=-20, consistency=40, violations=2),
            _snapshot("good", 1, capital=102_000, drawdown=1, reward=35, consistency=85),
        )
    )

    analysis = analyze_strategic_timeline(timeline)

    assert analysis.best_period is not None
    assert analysis.best_period.session_id == "good"
    assert analysis.worst_period is not None
    assert analysis.worst_period.session_id == "bad"
    assert 0 <= analysis.stability_score <= 100
    assert 0 <= analysis.strategic_health_score <= 100


def test_cycle_phases_are_detected_from_modes_and_objectives() -> None:
    timeline = update_strategic_timeline(
        snapshots=(
            _snapshot("growth", 0, mode="OPPORTUNITY", objective="CONTROLLED_GROWTH"),
            _snapshot("recovery", 1, mode="RECOVERY", objective="DRAWDOWN_RECOVERY"),
            _snapshot("validation", 2, objective="POLICY_VALIDATION"),
            _snapshot("paused", 3, mode="PAUSED", objective="PAUSE_AND_REVIEW"),
        )
    )

    phases = analyze_strategic_timeline(timeline).cycle_phases

    assert StrategicCyclePhase.GROWTH in phases
    assert StrategicCyclePhase.RECOVERY in phases
    assert StrategicCyclePhase.POLICY_VALIDATION in phases
    assert StrategicCyclePhase.PAUSED in phases


def test_analyze_empty_timeline_returns_safe_defaults() -> None:
    analysis = analyze_strategic_timeline(update_strategic_timeline())

    assert analysis.snapshots_count == 0
    assert analysis.strategic_health_score == 0
    assert analysis.recommendations


def test_save_and_load_strategic_timeline_round_trip(tmp_path) -> None:
    timeline = update_strategic_timeline(snapshot=_snapshot("s1", 0))
    path = tmp_path / "timeline.json"

    save_strategic_timeline(path, timeline)
    loaded = load_strategic_timeline(path)

    assert loaded.name == timeline.name
    assert loaded.snapshots[0].session_id == "s1"
    assert loaded.events[0].event_type == "SNAPSHOT_ADDED"


def test_render_strategic_timeline_markdown_contains_required_sections() -> None:
    timeline = update_strategic_timeline(
        snapshots=(
            _snapshot("s1", 0),
            _snapshot("s2", 1, capital=101_000, drawdown=1, reward=30, consistency=82),
        )
    )

    markdown = render_strategic_timeline_markdown(timeline)

    assert "# Strategic Memory Timeline" in markdown
    assert "## Resume timeline" in markdown
    assert "## Evolution capital/drawdown" in markdown
    assert "## Evolution politiques" in markdown
    assert "## Cycles detectes" in markdown
    assert "## Derives detectees" in markdown
    assert "## Meilleure periode" in markdown
    assert "## Pire periode" in markdown
    assert "## Sante strategique" in markdown
    assert "## Recommandations AGIcore" in markdown
    assert "no broker" in markdown
