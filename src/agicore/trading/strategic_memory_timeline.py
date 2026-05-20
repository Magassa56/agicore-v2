"""Offline Strategic Memory Timeline for AGIcore Trading."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .executive_brain_models import ExecutiveBrainResult
from .strategic_memory_models import (
    StrategicCyclePhase,
    StrategicDriftSignal,
    StrategicMemorySnapshot,
    StrategicTimeline,
    StrategicTimelineAnalysis,
    StrategicTimelineEvent,
)
from .strategic_planning_models import StrategicObjective, StrategicPlanningResult


def create_strategic_snapshot(
    *,
    session_id: str,
    timestamp: datetime | None = None,
    capital_estimate: float = 0.0,
    drawdown_estimate: float = 0.0,
    executive_result: ExecutiveBrainResult | None = None,
    strategic_result: StrategicPlanningResult | None = None,
    policy_memory: AdaptivePolicyMemory | None = None,
    executive_mode: str | None = None,
    strategic_objective: str | None = None,
    risk_appetite: str | None = None,
    selected_policy: str | None = None,
    average_reward: float | None = None,
    consistency_score: float | None = None,
    safety_violations: int = 0,
    blocked_trades: int = 0,
    executed_trades: int = 0,
    market_regime_summary: str = "",
    behavior_summary: str = "",
    notes: str = "",
) -> StrategicMemorySnapshot:
    """Create one deterministic offline strategic memory snapshot."""
    plan = strategic_result.plan if strategic_result is not None else None
    state = executive_result.state if executive_result is not None else None
    best_policy = selected_policy or (plan.policy_to_test if plan is not None else None) or _best_policy(policy_memory)
    return StrategicMemorySnapshot(
        timestamp=timestamp or datetime.now(UTC),
        session_id=session_id,
        capital_estimate=float(capital_estimate),
        drawdown_estimate=max(0.0, float(drawdown_estimate)),
        executive_mode=executive_mode or (_enum_value(state.mode) if state is not None else "UNKNOWN"),
        strategic_objective=strategic_objective or (_enum_value(plan.primary_objective) if plan is not None else "UNKNOWN"),
        risk_appetite=risk_appetite or (_enum_value(state.risk_appetite) if state is not None else "UNKNOWN"),
        selected_policy=best_policy,
        average_reward=float(average_reward if average_reward is not None else _avg_reward(policy_memory)),
        consistency_score=float(consistency_score if consistency_score is not None else _progress_metric(strategic_result, "consistency")),
        safety_violations=max(0, int(safety_violations)),
        blocked_trades=max(0, int(blocked_trades)),
        executed_trades=max(0, int(executed_trades)),
        market_regime_summary=market_regime_summary,
        behavior_summary=behavior_summary,
        notes=notes,
    )


def update_strategic_timeline(
    timeline: StrategicTimeline | None = None,
    snapshot: StrategicMemorySnapshot | None = None,
    snapshots: Iterable[StrategicMemorySnapshot] = (),
    name: str = "agicore_strategic_memory_timeline",
) -> StrategicTimeline:
    """Append snapshots to an offline strategic timeline."""
    current = timeline or StrategicTimeline(snapshots=(), name=name)
    additions = list(snapshots)
    if snapshot is not None:
        additions.append(snapshot)
    ordered = tuple(sorted((*current.snapshots, *additions), key=lambda item: item.timestamp))
    events = list(current.events)
    for item in additions:
        events.append(
            StrategicTimelineEvent(
                event_type="SNAPSHOT_ADDED",
                message=f"Strategic snapshot added for session {item.session_id}.",
                timestamp=datetime.now(UTC),
                session_id=item.session_id,
            )
        )
    return StrategicTimeline(
        snapshots=ordered,
        events=tuple(events),
        name=current.name,
        version=current.version,
    )


def detect_strategic_drift(timeline: StrategicTimeline) -> tuple[StrategicDriftSignal, ...]:
    """Detect strategic improvement, degradation and behavioral drift."""
    snapshots = timeline.snapshots
    if len(snapshots) < 2:
        return ()
    first = snapshots[0]
    last = snapshots[-1]
    recent = snapshots[-3:]
    previous = snapshots[: max(1, len(snapshots) - len(recent))]
    signals: list[StrategicDriftSignal] = []

    if last.capital_estimate > first.capital_estimate and last.drawdown_estimate <= first.drawdown_estimate:
        signals.append(StrategicDriftSignal.STRATEGIC_IMPROVEMENT)
    if last.capital_estimate < first.capital_estimate or last.drawdown_estimate > first.drawdown_estimate + 2:
        signals.append(StrategicDriftSignal.STRATEGIC_DEGRADATION)
    if _avg(item.average_reward for item in recent) < _avg(item.average_reward for item in previous) - 10:
        signals.append(StrategicDriftSignal.REWARD_DECLINE)
    if _avg(item.consistency_score for item in recent) < _avg(item.consistency_score for item in previous) - 10:
        signals.append(StrategicDriftSignal.STABILITY_DECLINE)
    if _avg(item.safety_violations for item in recent) > _avg(item.safety_violations for item in previous) + 0.5:
        signals.append(StrategicDriftSignal.VIOLATIONS_INCREASE)
    if any("tilt" in item.behavior_summary.casefold() or "revenge" in item.behavior_summary.casefold() for item in recent):
        signals.append(StrategicDriftSignal.BEHAVIORAL_DRIFT)
    if len(recent) >= 2 and all(item.drawdown_estimate >= 5 for item in recent[-2:]):
        signals.append(StrategicDriftSignal.PERSISTENT_DRAWDOWN)
    if _dangerous_policy_detected(recent):
        signals.append(StrategicDriftSignal.DANGEROUS_POLICY)
    if last.drawdown_estimate <= first.drawdown_estimate - 2:
        signals.append(StrategicDriftSignal.CAPITAL_RECOVERY)
    if last.consistency_score > first.consistency_score + 10:
        signals.append(StrategicDriftSignal.CONSISTENCY_GAIN)
    return tuple(dict.fromkeys(signals))


def analyze_strategic_timeline(timeline: StrategicTimeline) -> StrategicTimelineAnalysis:
    """Analyze the strategic timeline and compute health metrics."""
    snapshots = timeline.snapshots
    if not snapshots:
        return StrategicTimelineAnalysis(
            snapshots_count=0,
            cycle_phases=(),
            drift_signals=(),
            best_period=None,
            worst_period=None,
            stability_score=0,
            strategic_health_score=0,
            improvement_detected=False,
            degradation_detected=False,
            recommendations=("Add strategic snapshots before analysis.",),
            summary="No strategic memory snapshots available.",
        )
    phases = tuple(_cycle_phase(item) for item in snapshots)
    drifts = detect_strategic_drift(timeline)
    best = max(snapshots, key=_snapshot_score)
    worst = min(snapshots, key=_snapshot_score)
    stability = _stability_score(snapshots, drifts)
    health = _health_score(snapshots, stability, drifts)
    improvement = any(signal in drifts for signal in (StrategicDriftSignal.STRATEGIC_IMPROVEMENT, StrategicDriftSignal.CAPITAL_RECOVERY, StrategicDriftSignal.CONSISTENCY_GAIN))
    degradation = any(signal in drifts for signal in _negative_signals())
    return StrategicTimelineAnalysis(
        snapshots_count=len(snapshots),
        cycle_phases=phases,
        drift_signals=drifts,
        best_period=best,
        worst_period=worst,
        stability_score=stability,
        strategic_health_score=health,
        improvement_detected=improvement,
        degradation_detected=degradation,
        recommendations=_recommendations(drifts, health),
        summary=f"{len(snapshots)} strategic snapshots analyzed; health {health}/100.",
    )


def render_strategic_timeline_markdown(
    timeline: StrategicTimeline,
    analysis: StrategicTimelineAnalysis | None = None,
) -> str:
    """Render the strategic memory timeline as Markdown."""
    result = analysis or analyze_strategic_timeline(timeline)
    first = timeline.snapshots[0] if timeline.snapshots else None
    last = timeline.snapshots[-1] if timeline.snapshots else None
    lines = [
        "# Strategic Memory Timeline",
        "",
        "## Resume timeline",
        "",
        f"- Snapshots: {result.snapshots_count}",
        f"- Events: {len(timeline.events)}",
        "",
        "## Evolution capital/drawdown",
        "",
        *_capital_lines(first, last),
        "",
        "## Evolution politiques",
        "",
        *_policy_lines(timeline.snapshots),
        "",
        "## Cycles detectes",
        "",
        *_bullet_lines(tuple(phase.value for phase in result.cycle_phases)),
        "",
        "## Derives detectees",
        "",
        *_bullet_lines(tuple(signal.value for signal in result.drift_signals)),
        "",
        "## Meilleure periode",
        "",
        *_snapshot_lines(result.best_period),
        "",
        "## Pire periode",
        "",
        *_snapshot_lines(result.worst_period),
        "",
        "## Sante strategique",
        "",
        f"- Stability score: {result.stability_score}/100",
        f"- Strategic health score: {result.strategic_health_score}/100",
        "",
        "## Recommandations AGIcore",
        "",
        *_bullet_lines(result.recommendations),
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def save_strategic_timeline(path: str | Path, timeline: StrategicTimeline) -> None:
    """Save a strategic timeline as simple offline JSON."""
    Path(path).write_text(json.dumps(_timeline_to_payload(timeline), indent=2, sort_keys=True), encoding="utf-8")


def load_strategic_timeline(path: str | Path) -> StrategicTimeline:
    """Load a strategic timeline saved by save_strategic_timeline."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return StrategicTimeline(
        name=str(payload.get("name", "agicore_strategic_memory_timeline")),
        version=str(payload.get("version", "1.0")),
        snapshots=tuple(_snapshot_from_payload(item) for item in payload.get("snapshots", ())),
        events=tuple(_event_from_payload(item) for item in payload.get("events", ())),
    )


def _cycle_phase(snapshot: StrategicMemorySnapshot) -> StrategicCyclePhase:
    mode = snapshot.executive_mode.upper()
    objective = snapshot.strategic_objective.upper()
    if mode == "SURVIVAL":
        return StrategicCyclePhase.SURVIVAL
    if mode == "PAUSED" or objective == StrategicObjective.PAUSE_AND_REVIEW.value:
        return StrategicCyclePhase.PAUSED
    if mode == "DEFENSIVE" or objective in {StrategicObjective.CAPITAL_PRESERVATION.value, StrategicObjective.RISK_REDUCTION.value}:
        return StrategicCyclePhase.DEFENSIVE
    if mode == "RECOVERY" or objective == StrategicObjective.DRAWDOWN_RECOVERY.value:
        return StrategicCyclePhase.RECOVERY
    if objective == StrategicObjective.LEARNING_PHASE.value:
        return StrategicCyclePhase.LEARNING
    if objective == StrategicObjective.POLICY_VALIDATION.value:
        return StrategicCyclePhase.POLICY_VALIDATION
    if mode == "OPPORTUNITY" or objective == StrategicObjective.CONTROLLED_GROWTH.value:
        return StrategicCyclePhase.GROWTH
    return StrategicCyclePhase.UNKNOWN


def _snapshot_score(snapshot: StrategicMemorySnapshot) -> float:
    return (
        snapshot.capital_estimate * 0.01
        + snapshot.average_reward
        + snapshot.consistency_score
        - snapshot.drawdown_estimate * 2
        - snapshot.safety_violations * 8
        - max(0, snapshot.executed_trades - snapshot.blocked_trades - 4) * 3
    )


def _stability_score(snapshots: tuple[StrategicMemorySnapshot, ...], drifts: tuple[StrategicDriftSignal, ...]) -> int:
    consistency = _avg(item.consistency_score for item in snapshots)
    violations = _avg(item.safety_violations for item in snapshots)
    drawdown = _avg(item.drawdown_estimate for item in snapshots)
    score = consistency - violations * 8 - drawdown * 1.5
    if StrategicDriftSignal.STABILITY_DECLINE in drifts:
        score -= 15
    if StrategicDriftSignal.CONSISTENCY_GAIN in drifts:
        score += 10
    return _clamp(score)


def _health_score(
    snapshots: tuple[StrategicMemorySnapshot, ...],
    stability_score: int,
    drifts: tuple[StrategicDriftSignal, ...],
) -> int:
    latest = snapshots[-1]
    reward = _clamp(latest.average_reward + 50)
    capital_component = 70 if latest.capital_estimate >= snapshots[0].capital_estimate else 45
    drawdown_penalty = min(35, int(round(latest.drawdown_estimate * 2)))
    score = int(round((stability_score + reward + capital_component) / 3)) - drawdown_penalty
    score -= 8 * sum(1 for signal in drifts if signal in _negative_signals())
    score += 5 * sum(1 for signal in drifts if signal in {StrategicDriftSignal.STRATEGIC_IMPROVEMENT, StrategicDriftSignal.CAPITAL_RECOVERY, StrategicDriftSignal.CONSISTENCY_GAIN})
    return _clamp(score)


def _recommendations(drifts: tuple[StrategicDriftSignal, ...], health: int) -> tuple[str, ...]:
    recommendations: list[str] = []
    if StrategicDriftSignal.PERSISTENT_DRAWDOWN in drifts:
        recommendations.append("Switch to recovery planning and cap session loss.")
    if StrategicDriftSignal.DANGEROUS_POLICY in drifts:
        recommendations.append("Disable or review policies linked to high violations and negative rewards.")
    if StrategicDriftSignal.BEHAVIORAL_DRIFT in drifts:
        recommendations.append("Require behavioral review before new paper decisions.")
    if StrategicDriftSignal.REWARD_DECLINE in drifts or StrategicDriftSignal.STABILITY_DECLINE in drifts:
        recommendations.append("Reduce risk until reward and consistency stabilize.")
    if health >= 75 and not any(signal in drifts for signal in _negative_signals()):
        recommendations.append("Maintain the current strategic trajectory.")
    return tuple(recommendations or ("Continue collecting offline timeline snapshots.",))


def _dangerous_policy_detected(snapshots: tuple[StrategicMemorySnapshot, ...]) -> bool:
    by_policy: dict[str, list[StrategicMemorySnapshot]] = {}
    for snapshot in snapshots:
        if snapshot.selected_policy:
            by_policy.setdefault(snapshot.selected_policy, []).append(snapshot)
    return any(
        len(items) >= 2
        and _avg(item.average_reward for item in items) < 0
        and _avg(item.safety_violations for item in items) >= 1
        for items in by_policy.values()
    )


def _negative_signals() -> set[StrategicDriftSignal]:
    return {
        StrategicDriftSignal.STRATEGIC_DEGRADATION,
        StrategicDriftSignal.BEHAVIORAL_DRIFT,
        StrategicDriftSignal.VIOLATIONS_INCREASE,
        StrategicDriftSignal.REWARD_DECLINE,
        StrategicDriftSignal.STABILITY_DECLINE,
        StrategicDriftSignal.PERSISTENT_DRAWDOWN,
        StrategicDriftSignal.DANGEROUS_POLICY,
    }


def _timeline_to_payload(timeline: StrategicTimeline) -> dict[str, Any]:
    return {
        "name": timeline.name,
        "version": timeline.version,
        "snapshots": [_snapshot_to_payload(item) for item in timeline.snapshots],
        "events": [_event_to_payload(item) for item in timeline.events],
    }


def _snapshot_to_payload(snapshot: StrategicMemorySnapshot) -> dict[str, Any]:
    payload = asdict(snapshot)
    payload["timestamp"] = snapshot.timestamp.isoformat()
    return payload


def _event_to_payload(event: StrategicTimelineEvent) -> dict[str, Any]:
    payload = asdict(event)
    payload["timestamp"] = event.timestamp.isoformat()
    return payload


def _snapshot_from_payload(payload: dict[str, Any]) -> StrategicMemorySnapshot:
    return StrategicMemorySnapshot(
        timestamp=datetime.fromisoformat(payload["timestamp"]),
        session_id=str(payload["session_id"]),
        capital_estimate=float(payload.get("capital_estimate", 0.0)),
        drawdown_estimate=float(payload.get("drawdown_estimate", 0.0)),
        executive_mode=str(payload.get("executive_mode", "UNKNOWN")),
        strategic_objective=str(payload.get("strategic_objective", "UNKNOWN")),
        risk_appetite=str(payload.get("risk_appetite", "UNKNOWN")),
        selected_policy=payload.get("selected_policy"),
        average_reward=float(payload.get("average_reward", 0.0)),
        consistency_score=float(payload.get("consistency_score", 0.0)),
        safety_violations=int(payload.get("safety_violations", 0)),
        blocked_trades=int(payload.get("blocked_trades", 0)),
        executed_trades=int(payload.get("executed_trades", 0)),
        market_regime_summary=str(payload.get("market_regime_summary", "")),
        behavior_summary=str(payload.get("behavior_summary", "")),
        notes=str(payload.get("notes", "")),
    )


def _event_from_payload(payload: dict[str, Any]) -> StrategicTimelineEvent:
    return StrategicTimelineEvent(
        event_type=str(payload.get("event_type", "UNKNOWN")),
        message=str(payload.get("message", "")),
        timestamp=datetime.fromisoformat(payload["timestamp"]),
        session_id=payload.get("session_id"),
    )


def _best_policy(policy_memory: AdaptivePolicyMemory | None) -> str | None:
    if policy_memory is None or not policy_memory.entries:
        return None
    entries = sorted(policy_memory.entries.values(), key=lambda item: (item.confidence_score, item.average_reward), reverse=True)
    return entries[0].policy_name


def _avg_reward(policy_memory: AdaptivePolicyMemory | None) -> float:
    if policy_memory is None or not policy_memory.entries:
        return 0.0
    return _avg(item.average_reward for item in policy_memory.entries.values())


def _progress_metric(result: StrategicPlanningResult | None, key: str) -> float:
    if result is None:
        return 0.0
    return float(result.plan.progress_metrics.get(key, 0.0))


def _capital_lines(
    first: StrategicMemorySnapshot | None,
    last: StrategicMemorySnapshot | None,
) -> list[str]:
    if first is None or last is None:
        return ["- None"]
    return [
        f"- Capital start: {first.capital_estimate:.2f}",
        f"- Capital latest: {last.capital_estimate:.2f}",
        f"- Drawdown start: {first.drawdown_estimate:.2f}",
        f"- Drawdown latest: {last.drawdown_estimate:.2f}",
    ]


def _policy_lines(snapshots: tuple[StrategicMemorySnapshot, ...]) -> list[str]:
    policies = tuple(item.selected_policy or "none" for item in snapshots)
    if not policies:
        return ["- None"]
    return [f"- {policy}" for policy in policies]


def _snapshot_lines(snapshot: StrategicMemorySnapshot | None) -> list[str]:
    if snapshot is None:
        return ["- None"]
    return [
        f"- Session: {snapshot.session_id}",
        f"- Capital: {snapshot.capital_estimate:.2f}",
        f"- Drawdown: {snapshot.drawdown_estimate:.2f}",
        f"- Policy: {snapshot.selected_policy or 'none'}",
        f"- Reward: {snapshot.average_reward:.2f}",
    ]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _avg(values: Iterable[float | int]) -> float:
    items = tuple(float(value) for value in values)
    return mean(items) if items else 0.0


def _enum_value(value: Any) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "analyze_strategic_timeline",
    "create_strategic_snapshot",
    "detect_strategic_drift",
    "load_strategic_timeline",
    "render_strategic_timeline_markdown",
    "save_strategic_timeline",
    "update_strategic_timeline",
]
