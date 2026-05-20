"""Offline adaptive policy memory for AGIcore Trading."""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from .adaptive_policy_memory_models import (
    AdaptivePolicyMemory,
    PolicyContextSignature,
    PolicyMemoryEntry,
    PolicyMemoryRecommendation,
    PolicyPerformanceSnapshot,
)
from .behavior_models import BehaviorAnalysisResult
from .market_regime_models import MarketRegimeAnalysis
from .policy_evaluation_models import PolicyComparisonResult, PolicyEvaluationResult


def update_policy_memory(
    memory: AdaptivePolicyMemory | None = None,
    *,
    policy_results: Iterable[PolicyEvaluationResult] = (),
    comparison_result: PolicyComparisonResult | None = None,
    market_regime: MarketRegimeAnalysis | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    strategy_name: str | None = None,
) -> AdaptivePolicyMemory:
    """Update offline policy memory from policy evaluation results."""
    base = memory or AdaptivePolicyMemory()
    results = list(policy_results)
    if comparison_result is not None:
        results.extend(comparison_result.results)
    new_snapshots = tuple(
        _snapshot_from_result(
            result,
            market_regime=market_regime,
            behavior_result=behavior_result,
            strategy_name=strategy_name,
        )
        for result in results
    )
    snapshots = base.snapshots + new_snapshots
    entries = _build_entries(snapshots)
    disabled = tuple(sorted(name for name, entry in entries.items() if entry.recommendation == PolicyMemoryRecommendation.DISABLE_POLICY))
    now = _now()
    return AdaptivePolicyMemory(
        entries=entries,
        snapshots=snapshots,
        disabled_policies=disabled,
        last_updated=now,
    )


def compare_policy_performance(memory: AdaptivePolicyMemory) -> tuple[PolicyMemoryEntry, ...]:
    """Return policies ordered by confidence and reward, safest first."""
    return tuple(
        sorted(
            memory.entries.values(),
            key=lambda entry: (
                entry.recommendation == PolicyMemoryRecommendation.DISABLE_POLICY,
                -entry.confidence_score,
                -entry.average_reward,
                entry.dangerous_decision_rate,
            ),
        )
    )


def recommend_policy_for_context(
    memory: AdaptivePolicyMemory,
    context_signature: PolicyContextSignature | None = None,
    *,
    market_regime: MarketRegimeAnalysis | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    context_score: int | None = None,
    strategy_name: str | None = None,
) -> PolicyMemoryEntry | None:
    """Recommend the best remembered policy for a market/behavior context."""
    signature = context_signature or PolicyContextSignature(
        market_regime=_enum_value(market_regime.primary_regime) if market_regime is not None else None,
        behavior_classification=_behavior_classes(behavior_result),
        context_score_bucket=_score_bucket(context_score),
        strategy_name=strategy_name,
    )
    candidates = [entry for entry in memory.entries.values() if entry.policy_name not in memory.disabled_policies]
    if not candidates:
        return None
    return max(candidates, key=lambda entry: _context_match_score(entry, signature))


def identify_dangerous_policies(
    memory: AdaptivePolicyMemory,
    *,
    dangerous_rate_threshold: float = 0.25,
    min_confidence_score: int = 40,
) -> tuple[str, ...]:
    """Identify policies that should be disabled or reviewed."""
    dangerous = [
        entry.policy_name
        for entry in memory.entries.values()
        if entry.dangerous_decision_rate >= dangerous_rate_threshold
        or entry.confidence_score < min_confidence_score
        or entry.recommendation == PolicyMemoryRecommendation.DISABLE_POLICY
    ]
    return tuple(sorted(dict.fromkeys(dangerous)))


def render_policy_memory_markdown(memory: AdaptivePolicyMemory) -> str:
    """Render policy memory as Markdown."""
    ranked = compare_policy_performance(memory)
    lines = [
        "# Adaptive Policy Memory",
        "",
        "## Resume memoire",
        "",
        f"- Policies tracked: {len(memory.entries)}",
        f"- Snapshots: {len(memory.snapshots)}",
        f"- Disabled policies: {len(memory.disabled_policies)}",
        f"- Last updated: {memory.last_updated or 'None'}",
        "",
        "## Classement politiques",
        "",
        "| Policy | Recommendation | Confidence | Avg reward | Dangerous | Accepted | Blocked | Reduced |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        *_ranking_lines(ranked),
        "",
        "## Politiques dangereuses",
        "",
        *_bullet_lines(identify_dangerous_policies(memory)),
        "",
        "## Meilleurs contextes",
        "",
        *_context_lines(ranked, best=True),
        "",
        "## Pires contextes",
        "",
        *_context_lines(ranked, best=False),
        "",
        "## Recommandations AGIcore",
        "",
        *_recommendation_lines(ranked),
        "",
        "- Offline memory only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def save_policy_memory(path: str | Path, memory: AdaptivePolicyMemory) -> None:
    """Save adaptive policy memory to JSON."""
    Path(path).write_text(json.dumps(_memory_to_payload(memory), indent=2, sort_keys=True), encoding="utf-8")


def load_policy_memory(path: str | Path) -> AdaptivePolicyMemory:
    """Load adaptive policy memory from JSON."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = {
        name: _entry_from_payload(item)
        for name, item in payload.get("entries", {}).items()
    }
    return AdaptivePolicyMemory(
        entries=entries,
        snapshots=tuple(_snapshot_from_payload(item) for item in payload.get("snapshots", ())),
        disabled_policies=tuple(str(item) for item in payload.get("disabled_policies", ())),
        last_updated=str(payload.get("last_updated", "")),
    )


def _snapshot_from_result(
    result: PolicyEvaluationResult,
    *,
    market_regime: MarketRegimeAnalysis | None,
    behavior_result: BehaviorAnalysisResult | None,
    strategy_name: str | None,
) -> PolicyPerformanceSnapshot:
    count = max(1, result.scenario_count)
    return PolicyPerformanceSnapshot(
        policy_name=result.policy.value,
        reward=float(result.average_reward),
        normalized_reward=result.normalized_reward,
        average_context_score=result.average_context_score,
        dangerous_decision_rate=result.dangerous_decisions / count,
        blocked_trade_rate=result.blocked_trades / count,
        accepted_trade_rate=result.accepted_trades / count,
        reduced_risk_rate=result.reduced_risk_trades / count,
        context_signature=PolicyContextSignature(
            market_regime=_enum_value(market_regime.primary_regime) if market_regime is not None else None,
            behavior_classification=_behavior_classes(behavior_result),
            context_score_bucket=_score_bucket(int(round(result.average_context_score))),
            strategy_name=strategy_name,
        ),
    )


def _build_entries(snapshots: tuple[PolicyPerformanceSnapshot, ...]) -> dict[str, PolicyMemoryEntry]:
    grouped: dict[str, list[PolicyPerformanceSnapshot]] = defaultdict(list)
    for snapshot in snapshots:
        grouped[snapshot.policy_name].append(snapshot)
    now = _now()
    entries: dict[str, PolicyMemoryEntry] = {}
    for policy_name, items in grouped.items():
        avg_reward = mean(item.reward for item in items)
        avg_context = mean(item.average_context_score for item in items)
        dangerous = mean(item.dangerous_decision_rate for item in items)
        blocked = mean(item.blocked_trade_rate for item in items)
        accepted = mean(item.accepted_trade_rate for item in items)
        reduced = mean(item.reduced_risk_rate for item in items)
        regime_perf = _performance_by_regime(items)
        behavior_perf = _performance_by_behavior(items)
        confidence = _confidence_score(avg_reward, avg_context, dangerous, accepted, blocked, len(items))
        recommendation = _recommendation(confidence, avg_reward, dangerous)
        entries[policy_name] = PolicyMemoryEntry(
            policy_name=policy_name,
            total_evaluations=len(items),
            average_reward=round(avg_reward, 2),
            average_context_score=round(avg_context, 2),
            dangerous_decision_rate=round(dangerous, 4),
            blocked_trade_rate=round(blocked, 4),
            accepted_trade_rate=round(accepted, 4),
            reduced_risk_rate=round(reduced, 4),
            confidence_score=confidence,
            recommendation=recommendation,
            best_contexts=_ranked_contexts(items, reverse=True),
            worst_contexts=_ranked_contexts(items, reverse=False),
            regime_performance=regime_perf,
            behavior_context_performance=behavior_perf,
            last_updated=now,
        )
    return entries


def _confidence_score(
    average_reward: float,
    average_context_score: float,
    dangerous_rate: float,
    accepted_rate: float,
    blocked_rate: float,
    evaluations: int,
) -> int:
    score = 50 + average_reward / 2 + (average_context_score - 50) / 4
    score += min(10, evaluations * 2)
    score += min(8, accepted_rate * 8)
    if blocked_rate > 0.8:
        score -= 8
    score -= dangerous_rate * 70
    return _clamp(score)


def _recommendation(
    confidence: int,
    average_reward: float,
    dangerous_rate: float,
) -> PolicyMemoryRecommendation:
    if dangerous_rate >= 0.35:
        return PolicyMemoryRecommendation.DISABLE_POLICY
    if dangerous_rate >= 0.20 or confidence < 35:
        return PolicyMemoryRecommendation.REQUIRE_REVIEW
    if average_reward < 0 or confidence < 50:
        return PolicyMemoryRecommendation.REDUCE_POLICY_USAGE
    if confidence >= 75 and average_reward >= 10:
        return PolicyMemoryRecommendation.PRIORITIZE_POLICY
    return PolicyMemoryRecommendation.KEEP_POLICY


def _performance_by_regime(items: list[PolicyPerformanceSnapshot]) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for item in items:
        grouped[item.context_signature.market_regime or "UNKNOWN"].append(item.reward)
    return {name: round(mean(values), 2) for name, values in grouped.items()}


def _performance_by_behavior(items: list[PolicyPerformanceSnapshot]) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for item in items:
        behaviors = item.context_signature.behavior_classification or ("UNKNOWN",)
        for behavior in behaviors:
            grouped[behavior].append(item.reward)
    return {name: round(mean(values), 2) for name, values in grouped.items()}


def _ranked_contexts(items: list[PolicyPerformanceSnapshot], *, reverse: bool) -> tuple[str, ...]:
    ranked = sorted(items, key=lambda item: item.reward, reverse=reverse)
    labels = [_context_label(item.context_signature) for item in ranked[:3]]
    return tuple(dict.fromkeys(labels))


def _context_match_score(entry: PolicyMemoryEntry, signature: PolicyContextSignature) -> float:
    score = entry.confidence_score + entry.average_reward
    if signature.market_regime and signature.market_regime in entry.regime_performance:
        score += entry.regime_performance[signature.market_regime]
    for behavior in signature.behavior_classification:
        if behavior in entry.behavior_context_performance:
            score += entry.behavior_context_performance[behavior] / 2
    if signature.market_regime and any(signature.market_regime in context for context in entry.best_contexts):
        score += 10
    if signature.market_regime and any(signature.market_regime in context for context in entry.worst_contexts):
        score -= 15
    return score


def _context_label(signature: PolicyContextSignature) -> str:
    behaviors = ",".join(signature.behavior_classification) if signature.behavior_classification else "UNKNOWN"
    return (
        f"regime={signature.market_regime or 'UNKNOWN'}; "
        f"behavior={behaviors}; "
        f"score={signature.context_score_bucket or 'UNKNOWN'}; "
        f"strategy={signature.strategy_name or 'UNKNOWN'}"
    )


def _score_bucket(score: int | None) -> str | None:
    if score is None:
        return None
    if score >= 80:
        return "HIGH"
    if score >= 60:
        return "MEDIUM"
    return "LOW"


def _behavior_classes(behavior: BehaviorAnalysisResult | None) -> tuple[str, ...]:
    if behavior is None:
        return ()
    return tuple(_enum_value(item) for item in behavior.classifications)


def _ranking_lines(entries: tuple[PolicyMemoryEntry, ...]) -> list[str]:
    if not entries:
        return ["| None | None | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |"]
    return [
        (
            f"| {entry.policy_name} | {entry.recommendation.value} | {entry.confidence_score} | "
            f"{entry.average_reward:.2f} | {entry.dangerous_decision_rate:.2f} | "
            f"{entry.accepted_trade_rate:.2f} | {entry.blocked_trade_rate:.2f} | {entry.reduced_risk_rate:.2f} |"
        )
        for entry in entries
    ]


def _context_lines(entries: tuple[PolicyMemoryEntry, ...], *, best: bool) -> list[str]:
    lines: list[str] = []
    for entry in entries:
        contexts = entry.best_contexts if best else entry.worst_contexts
        if contexts:
            lines.append(f"- {entry.policy_name}: {' | '.join(contexts)}")
    return lines or ["- None"]


def _recommendation_lines(entries: tuple[PolicyMemoryEntry, ...]) -> list[str]:
    if not entries:
        return ["- Collect policy evaluation results before recommending a policy."]
    return [f"- {entry.policy_name}: {entry.recommendation.value}" for entry in entries]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _memory_to_payload(memory: AdaptivePolicyMemory) -> dict[str, Any]:
    return {
        "entries": {name: _entry_to_payload(entry) for name, entry in memory.entries.items()},
        "snapshots": [_snapshot_to_payload(snapshot) for snapshot in memory.snapshots],
        "disabled_policies": list(memory.disabled_policies),
        "last_updated": memory.last_updated,
    }


def _entry_to_payload(entry: PolicyMemoryEntry) -> dict[str, Any]:
    payload = asdict(entry)
    payload["recommendation"] = entry.recommendation.value
    return payload


def _snapshot_to_payload(snapshot: PolicyPerformanceSnapshot) -> dict[str, Any]:
    return asdict(snapshot)


def _entry_from_payload(payload: dict[str, Any]) -> PolicyMemoryEntry:
    return PolicyMemoryEntry(
        policy_name=str(payload["policy_name"]),
        total_evaluations=int(payload["total_evaluations"]),
        average_reward=float(payload["average_reward"]),
        average_context_score=float(payload["average_context_score"]),
        dangerous_decision_rate=float(payload["dangerous_decision_rate"]),
        blocked_trade_rate=float(payload["blocked_trade_rate"]),
        accepted_trade_rate=float(payload["accepted_trade_rate"]),
        reduced_risk_rate=float(payload["reduced_risk_rate"]),
        confidence_score=int(payload["confidence_score"]),
        recommendation=PolicyMemoryRecommendation(payload["recommendation"]),
        best_contexts=tuple(str(item) for item in payload.get("best_contexts", ())),
        worst_contexts=tuple(str(item) for item in payload.get("worst_contexts", ())),
        regime_performance={str(key): float(value) for key, value in payload.get("regime_performance", {}).items()},
        behavior_context_performance={str(key): float(value) for key, value in payload.get("behavior_context_performance", {}).items()},
        last_updated=str(payload.get("last_updated", "")),
    )


def _snapshot_from_payload(payload: dict[str, Any]) -> PolicyPerformanceSnapshot:
    return PolicyPerformanceSnapshot(
        policy_name=str(payload["policy_name"]),
        reward=float(payload["reward"]),
        normalized_reward=int(payload["normalized_reward"]),
        average_context_score=float(payload["average_context_score"]),
        dangerous_decision_rate=float(payload["dangerous_decision_rate"]),
        blocked_trade_rate=float(payload["blocked_trade_rate"]),
        accepted_trade_rate=float(payload["accepted_trade_rate"]),
        reduced_risk_rate=float(payload["reduced_risk_rate"]),
        context_signature=_signature_from_payload(payload["context_signature"]),
        source=str(payload.get("source", "policy_evaluation")),
    )


def _signature_from_payload(payload: dict[str, Any]) -> PolicyContextSignature:
    return PolicyContextSignature(
        market_regime=payload.get("market_regime"),
        behavior_classification=tuple(str(item) for item in payload.get("behavior_classification", ())),
        context_score_bucket=payload.get("context_score_bucket"),
        strategy_name=payload.get("strategy_name"),
    )


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _enum_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _clamp(value: float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "compare_policy_performance",
    "identify_dangerous_policies",
    "load_policy_memory",
    "recommend_policy_for_context",
    "render_policy_memory_markdown",
    "save_policy_memory",
    "update_policy_memory",
]
