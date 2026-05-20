"""Offline meta strategy selector for AGIcore Trading."""
from __future__ import annotations

from .adaptive_policy_memory_models import (
    AdaptivePolicyMemory,
    PolicyMemoryEntry,
    PolicyMemoryRecommendation,
)
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult, TradeContextDecision
from .market_regime_models import MarketRegimeAnalysis
from .meta_strategy_models import (
    MetaStrategyCandidate,
    MetaStrategyDecision,
    MetaStrategyReason,
    MetaStrategySelectionInput,
    MetaStrategySelectionResult,
)
from .playbook_models import TraderProfile
from .policy_evaluation_models import PolicyEvaluationResult
from .safe_rl_models import SafeRLExperimentResult, SafeRLStatus
from .semi_auto_decision_models import SemiAutoDecision, SemiAutoDecisionResult
from .strategy_dna_models import StrategyDNA


def select_meta_strategy(
    selection_input: MetaStrategySelectionInput | None = None,
    *,
    adaptive_policy_memory: AdaptivePolicyMemory | None = None,
    policy_results: tuple[PolicyEvaluationResult, ...] = (),
    safe_rl_result: SafeRLExperimentResult | None = None,
    context_score: ContextScoringResult | None = None,
    market_regime: MarketRegimeAnalysis | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    semi_auto_decision: SemiAutoDecisionResult | None = None,
    strategy_dna: StrategyDNA | None = None,
    trader_profile: TraderProfile | None = None,
) -> MetaStrategySelectionResult:
    """Select the best offline policy/strategy for the current context."""
    if selection_input is not None:
        adaptive_policy_memory = selection_input.adaptive_policy_memory
        policy_results = selection_input.policy_results
        safe_rl_result = selection_input.safe_rl_result
        context_score = selection_input.context_score
        market_regime = selection_input.market_regime
        behavior_result = selection_input.behavior_result
        semi_auto_decision = selection_input.semi_auto_decision
        strategy_dna = selection_input.strategy_dna
        trader_profile = selection_input.trader_profile

    hard_block_reasons = _hard_block_reasons(context_score, market_regime, semi_auto_decision)
    base_candidates = _build_candidates(
        adaptive_policy_memory=adaptive_policy_memory,
        policy_results=policy_results,
        safe_rl_result=safe_rl_result,
        context_score=context_score,
        market_regime=market_regime,
        behavior_result=behavior_result,
        strategy_dna=strategy_dna,
        trader_profile=trader_profile,
    )
    ranked = rank_strategy_candidates(base_candidates)
    if hard_block_reasons:
        return MetaStrategySelectionResult(
            selected_policy_name=None,
            decision=MetaStrategyDecision.BLOCK_ALL_POLICIES,
            confidence_score=0,
            ranked_candidates=ranked,
            reasons=tuple(dict.fromkeys(hard_block_reasons)),
            risk_notes=_risk_notes(ranked) + ("Hard context block: no offline policy should be selected.",),
            required_manual_review=True,
            recommendation="Block all policies and keep the session in review-only mode.",
        )

    if not ranked:
        fallback = _fallback_result(context_score, safe_rl_result)
        return fallback

    best = ranked[0]
    if best.disabled or best.score < 35:
        return MetaStrategySelectionResult(
            selected_policy_name=None,
            decision=MetaStrategyDecision.NO_STRATEGY,
            confidence_score=max(0, best.score),
            ranked_candidates=ranked,
            reasons=(MetaStrategyReason.DANGEROUS_POLICY,),
            risk_notes=_risk_notes(ranked),
            required_manual_review=True,
            recommendation="No policy is safe enough for this offline context.",
        )

    reasons = tuple(dict.fromkeys(best.reasons))
    if safe_rl_result is not None and safe_rl_result.status == SafeRLStatus.BLOCKED:
        return MetaStrategySelectionResult(
            selected_policy_name=None,
            decision=MetaStrategyDecision.REQUIRE_REVIEW,
            confidence_score=min(best.score, 50),
            ranked_candidates=ranked,
            reasons=reasons + (MetaStrategyReason.SAFE_RL_BLOCKED,),
            risk_notes=_risk_notes(ranked) + tuple(safe_rl_result.risks_detected),
            required_manual_review=True,
            recommendation="Safe RL is blocked; require manual review before any offline selection.",
        )

    if _behavior_high_risk(behavior_result) or best.score < 60:
        return MetaStrategySelectionResult(
            selected_policy_name=best.policy_name,
            decision=MetaStrategyDecision.SELECT_REDUCED_RISK_POLICY,
            confidence_score=best.score,
            ranked_candidates=ranked,
            reasons=reasons + (MetaStrategyReason.BEHAVIOR_RISK_HIGH,),
            risk_notes=_risk_notes(ranked),
            required_manual_review=True,
            recommendation=f"Use {best.policy_name} only as a reduced-risk offline candidate.",
        )

    return MetaStrategySelectionResult(
        selected_policy_name=best.policy_name,
        decision=MetaStrategyDecision.SELECT_POLICY,
        confidence_score=best.score,
        ranked_candidates=ranked,
        reasons=reasons,
        risk_notes=_risk_notes(ranked),
        required_manual_review=False,
        recommendation=f"Select {best.policy_name} for offline decision support.",
    )


def rank_strategy_candidates(candidates: tuple[MetaStrategyCandidate, ...] | list[MetaStrategyCandidate]) -> tuple[MetaStrategyCandidate, ...]:
    """Rank meta-strategy candidates by score, safety, and confidence."""
    return tuple(
        sorted(
            candidates,
            key=lambda item: (
                item.disabled,
                -item.score,
                item.dangerous_decision_rate,
                -item.confidence_score,
                -item.average_reward,
            ),
        )
    )


def render_meta_strategy_markdown(result: MetaStrategySelectionResult) -> str:
    """Render a meta-strategy selection result as Markdown."""
    lines = [
        "# Meta Strategy Selector",
        "",
        "## Decision meta-strategie",
        "",
        f"- Decision: {result.decision.value}",
        f"- Confidence: {result.confidence_score}/100",
        "",
        "## Politique selectionnee",
        "",
        f"- {result.selected_policy_name or 'None'}",
        "",
        "## Classement des politiques",
        "",
        "| Policy | Score | Confidence | Avg reward | Dangerous | Disabled |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
        *_candidate_lines(result.ranked_candidates),
        "",
        "## Raisons",
        "",
        *_reason_lines(result.reasons),
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(result.risk_notes),
        "",
        "## Fallback/Review",
        "",
        f"- Manual review required: {result.required_manual_review}",
        "",
        "## Recommandation AGIcore",
        "",
        f"- {result.recommendation}",
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _build_candidates(
    *,
    adaptive_policy_memory: AdaptivePolicyMemory | None,
    policy_results: tuple[PolicyEvaluationResult, ...],
    safe_rl_result: SafeRLExperimentResult | None,
    context_score: ContextScoringResult | None,
    market_regime: MarketRegimeAnalysis | None,
    behavior_result: BehaviorAnalysisResult | None,
    strategy_dna: StrategyDNA | None,
    trader_profile: TraderProfile | None,
) -> tuple[MetaStrategyCandidate, ...]:
    candidates: list[MetaStrategyCandidate] = []
    if adaptive_policy_memory is not None:
        candidates.extend(
            _candidate_from_memory(
                entry,
                disabled=entry.policy_name in adaptive_policy_memory.disabled_policies,
                safe_rl_result=safe_rl_result,
                context_score=context_score,
                market_regime=market_regime,
                behavior_result=behavior_result,
                strategy_dna=strategy_dna,
                trader_profile=trader_profile,
            )
            for entry in adaptive_policy_memory.entries.values()
        )
    seen = {candidate.policy_name for candidate in candidates}
    for result in policy_results:
        if result.policy.value in seen:
            continue
        candidates.append(
            _candidate_from_policy_result(
                result,
                safe_rl_result=safe_rl_result,
                context_score=context_score,
                market_regime=market_regime,
                behavior_result=behavior_result,
                strategy_dna=strategy_dna,
                trader_profile=trader_profile,
            )
        )
    return tuple(candidates)


def _candidate_from_memory(
    entry: PolicyMemoryEntry,
    *,
    disabled: bool,
    safe_rl_result: SafeRLExperimentResult | None,
    context_score: ContextScoringResult | None,
    market_regime: MarketRegimeAnalysis | None,
    behavior_result: BehaviorAnalysisResult | None,
    strategy_dna: StrategyDNA | None,
    trader_profile: TraderProfile | None,
) -> MetaStrategyCandidate:
    score = entry.confidence_score + int(entry.average_reward / 2)
    reasons = [MetaStrategyReason.MEMORY_MATCH]
    risks: list[str] = []
    if entry.average_reward > 10:
        score += 8
        reasons.append(MetaStrategyReason.HIGH_AVERAGE_REWARD)
    if entry.confidence_score >= 70:
        score += 8
        reasons.append(MetaStrategyReason.HIGH_CONFIDENCE)
    score, reasons, risks = _apply_common_penalties(
        policy_name=entry.policy_name,
        score=score,
        dangerous_rate=entry.dangerous_decision_rate,
        disabled=disabled or entry.recommendation == PolicyMemoryRecommendation.DISABLE_POLICY,
        safe_rl_result=safe_rl_result,
        context_score=context_score,
        market_regime=market_regime,
        behavior_result=behavior_result,
        strategy_dna=strategy_dna,
        trader_profile=trader_profile,
        reasons=reasons,
        risks=risks,
    )
    return MetaStrategyCandidate(
        policy_name=entry.policy_name,
        score=_clamp(score),
        confidence_score=entry.confidence_score,
        average_reward=entry.average_reward,
        dangerous_decision_rate=entry.dangerous_decision_rate,
        compatible_with_strategy=_strategy_compatible(entry.policy_name, strategy_dna, trader_profile),
        disabled=disabled or entry.recommendation == PolicyMemoryRecommendation.DISABLE_POLICY,
        reasons=tuple(dict.fromkeys(reasons)),
        risk_notes=tuple(dict.fromkeys(risks)),
    )


def _candidate_from_policy_result(
    result: PolicyEvaluationResult,
    *,
    safe_rl_result: SafeRLExperimentResult | None,
    context_score: ContextScoringResult | None,
    market_regime: MarketRegimeAnalysis | None,
    behavior_result: BehaviorAnalysisResult | None,
    strategy_dna: StrategyDNA | None,
    trader_profile: TraderProfile | None,
) -> MetaStrategyCandidate:
    count = max(1, result.scenario_count)
    dangerous_rate = result.dangerous_decisions / count
    score = result.normalized_reward + int(result.average_reward / 3)
    reasons = [MetaStrategyReason.HIGH_AVERAGE_REWARD] if result.average_reward > 10 else []
    risks: list[str] = []
    score, reasons, risks = _apply_common_penalties(
        policy_name=result.policy.value,
        score=score,
        dangerous_rate=dangerous_rate,
        disabled=False,
        safe_rl_result=safe_rl_result,
        context_score=context_score,
        market_regime=market_regime,
        behavior_result=behavior_result,
        strategy_dna=strategy_dna,
        trader_profile=trader_profile,
        reasons=reasons,
        risks=risks,
    )
    return MetaStrategyCandidate(
        policy_name=result.policy.value,
        score=_clamp(score),
        confidence_score=result.normalized_reward,
        average_reward=result.average_reward,
        dangerous_decision_rate=dangerous_rate,
        compatible_with_strategy=_strategy_compatible(result.policy.value, strategy_dna, trader_profile),
        disabled=False,
        reasons=tuple(dict.fromkeys(reasons)),
        risk_notes=tuple(dict.fromkeys(risks)),
    )


def _apply_common_penalties(
    *,
    policy_name: str,
    score: int,
    dangerous_rate: float,
    disabled: bool,
    safe_rl_result: SafeRLExperimentResult | None,
    context_score: ContextScoringResult | None,
    market_regime: MarketRegimeAnalysis | None,
    behavior_result: BehaviorAnalysisResult | None,
    strategy_dna: StrategyDNA | None,
    trader_profile: TraderProfile | None,
    reasons: list[MetaStrategyReason],
    risks: list[str],
) -> tuple[int, list[MetaStrategyReason], list[str]]:
    if disabled or dangerous_rate >= 0.25:
        score -= 45
        reasons.append(MetaStrategyReason.DANGEROUS_POLICY)
        risks.append(f"{policy_name}: dangerous policy memory or high dangerous rate.")
    if safe_rl_result is not None and safe_rl_result.status == SafeRLStatus.BLOCKED:
        score -= 50
        reasons.append(MetaStrategyReason.SAFE_RL_BLOCKED)
        risks.append("Safe RL status is BLOCKED.")
    elif safe_rl_result is not None and safe_rl_result.status == SafeRLStatus.REVIEW_REQUIRED:
        score -= 20
        risks.append("Safe RL requires review.")
    if context_score is not None and context_score.global_score < 60:
        score -= 15
        risks.append(f"Context score is low: {context_score.global_score}.")
    if market_regime is not None:
        regime = _value(market_regime.primary_regime)
        if market_regime.dangerous_market:
            score -= 60
            reasons.append(MetaStrategyReason.DANGEROUS_MARKET)
            risks.append("Market is dangerous.")
        if regime in {"CHOPPY", "NEWS_RISK", "DEAD_MARKET"} and "NO_TRADE" not in policy_name:
            score -= 15
            reasons.append(MetaStrategyReason.REGIME_INCOMPATIBLE)
            risks.append(f"{policy_name}: weak compatibility with {regime}.")
    if _behavior_high_risk(behavior_result):
        score -= 20
        reasons.append(MetaStrategyReason.BEHAVIOR_RISK_HIGH)
        risks.append("Behavior risk is high.")
    if _strategy_compatible(policy_name, strategy_dna, trader_profile):
        score += 8
        reasons.append(MetaStrategyReason.STRATEGY_DNA_COMPATIBLE)
    else:
        score -= 15
        reasons.append(MetaStrategyReason.REGIME_INCOMPATIBLE)
        risks.append(f"{policy_name}: incompatible with StrategyDNA or TraderProfile.")
    return score, reasons, risks


def _hard_block_reasons(
    context_score: ContextScoringResult | None,
    market_regime: MarketRegimeAnalysis | None,
    semi_auto_decision: SemiAutoDecisionResult | None,
) -> tuple[MetaStrategyReason, ...]:
    reasons: list[MetaStrategyReason] = []
    if context_score is not None and context_score.decision == TradeContextDecision.NO_TRADE:
        reasons.append(MetaStrategyReason.NO_TRADE_CONTEXT)
    if semi_auto_decision is not None and semi_auto_decision.decision == SemiAutoDecision.STOP_SESSION:
        reasons.append(MetaStrategyReason.STOP_SESSION)
    if market_regime is not None and market_regime.dangerous_market:
        reasons.append(MetaStrategyReason.DANGEROUS_MARKET)
    return tuple(reasons)


def _fallback_result(
    context_score: ContextScoringResult | None,
    safe_rl_result: SafeRLExperimentResult | None,
) -> MetaStrategySelectionResult:
    if safe_rl_result is not None and safe_rl_result.status == SafeRLStatus.BLOCKED:
        return MetaStrategySelectionResult(
            selected_policy_name=None,
            decision=MetaStrategyDecision.NO_STRATEGY,
            confidence_score=0,
            ranked_candidates=(),
            reasons=(MetaStrategyReason.SAFE_RL_BLOCKED,),
            risk_notes=tuple(safe_rl_result.risks_detected),
            required_manual_review=True,
            recommendation="No strategy selected because Safe RL is blocked.",
        )
    if context_score is None or context_score.global_score < 65:
        return MetaStrategySelectionResult(
            selected_policy_name="CONSERVATIVE",
            decision=MetaStrategyDecision.FALLBACK_TO_CONSERVATIVE,
            confidence_score=45,
            ranked_candidates=(),
            reasons=(MetaStrategyReason.FALLBACK_CONSERVATIVE,),
            risk_notes=("Insufficient or uncertain policy memory.",),
            required_manual_review=True,
            recommendation="Fallback to conservative offline review only.",
        )
    return MetaStrategySelectionResult(
        selected_policy_name=None,
        decision=MetaStrategyDecision.NO_STRATEGY,
        confidence_score=0,
        ranked_candidates=(),
        reasons=(),
        risk_notes=("No policy candidate available.",),
        required_manual_review=True,
        recommendation="Collect policy memory before selecting a strategy.",
    )


def _strategy_compatible(
    policy_name: str,
    strategy_dna: StrategyDNA | None,
    trader_profile: TraderProfile | None,
) -> bool:
    if trader_profile is not None and trader_profile.forbidden_conditions:
        return False
    if strategy_dna is None:
        return True
    name = policy_name.upper()
    if "LONG_ONLY" in name and strategy_dna.allowed_direction.value == "SHORT_ONLY":
        return False
    if "SHORT" in name and strategy_dna.allowed_direction.value == "LONG_ONLY":
        return False
    if strategy_dna.name and strategy_dna.name.upper() in name:
        return True
    return True


def _behavior_high_risk(behavior: BehaviorAnalysisResult | None) -> bool:
    if behavior is None:
        return False
    classes = {_value(item) for item in behavior.classifications}
    return bool(
        behavior.scores.emotional_risk_score >= 70
        or "HIGH_RISK" in classes
        or "OVERTRADING" in classes
        or "REVENGE_TRADING_PROBABLE" in classes
    )


def _risk_notes(candidates: tuple[MetaStrategyCandidate, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(note for candidate in candidates for note in candidate.risk_notes))


def _candidate_lines(candidates: tuple[MetaStrategyCandidate, ...]) -> list[str]:
    if not candidates:
        return ["| None | 0 | 0 | 0.00 | 0.00 | False |"]
    return [
        (
            f"| {candidate.policy_name} | {candidate.score} | {candidate.confidence_score} | "
            f"{candidate.average_reward:.2f} | {candidate.dangerous_decision_rate:.2f} | {candidate.disabled} |"
        )
        for candidate in candidates
    ]


def _reason_lines(reasons: tuple[MetaStrategyReason, ...]) -> list[str]:
    if not reasons:
        return ["- None"]
    return [f"- {reason.value}" for reason in reasons]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "rank_strategy_candidates",
    "render_meta_strategy_markdown",
    "select_meta_strategy",
]
