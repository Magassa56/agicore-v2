"""Offline reward function engine for AGIcore Trading."""
from __future__ import annotations

from .adaptive_memory_models import TraderMemoryProfile
from .behavior_models import BehaviorAnalysisResult
from .context_scoring_models import ContextScoringResult, TradeContextDecision
from .market_regime_models import MarketRegimeAnalysis
from .paper_execution_models import PaperExecutionDecision, PaperExecutionResult
from .reward_models import (
    RewardBreakdown,
    RewardComponent,
    RewardEvaluationInput,
    RewardEvaluationResult,
    RewardLabel,
)
from .semi_auto_decision_models import SemiAutoDecision, SemiAutoDecisionResult
from .session_replay_models import SessionReplayResult
from .strategy_dna_models import StrategyDNA
from .trade_journal_models import JournalAnalysisResult, TradeJournalEntry


def evaluate_trading_reward(
    evaluation_input: RewardEvaluationInput | None = None,
    *,
    paper_execution_result: PaperExecutionResult | None = None,
    semi_auto_decision: SemiAutoDecisionResult | None = None,
    context_score: ContextScoringResult | None = None,
    session_replay_result: SessionReplayResult | None = None,
    behavior_result: BehaviorAnalysisResult | None = None,
    memory_profile: TraderMemoryProfile | None = None,
    market_regime: MarketRegimeAnalysis | None = None,
    strategy_dna: StrategyDNA | None = None,
    journal_entries: tuple[TradeJournalEntry, ...] = (),
    journal_result: JournalAnalysisResult | None = None,
) -> RewardEvaluationResult:
    """Evaluate a deterministic offline reward for a trading decision."""
    if evaluation_input is not None:
        paper_execution_result = evaluation_input.paper_execution_result
        semi_auto_decision = evaluation_input.semi_auto_decision
        context_score = evaluation_input.context_score
        session_replay_result = evaluation_input.session_replay_result
        behavior_result = evaluation_input.behavior_result
        memory_profile = evaluation_input.memory_profile
        market_regime = evaluation_input.market_regime
        strategy_dna = evaluation_input.strategy_dna
        journal_entries = evaluation_input.journal_entries
        journal_result = evaluation_input.journal_result

    notes: list[str] = []
    actions: list[str] = []
    breakdown = RewardBreakdown(
        pnl_reward=_pnl_reward(paper_execution_result, context_score, notes, actions),
        risk_adjusted_reward=_risk_adjusted_reward(
            paper_execution_result,
            semi_auto_decision,
            context_score,
            market_regime,
            notes,
            actions,
        ),
        discipline_reward=_discipline_reward(session_replay_result, journal_result, journal_entries, notes, actions),
        context_alignment_reward=_context_alignment_reward(
            paper_execution_result,
            semi_auto_decision,
            context_score,
            market_regime,
            notes,
            actions,
        ),
        behavior_reward=_behavior_reward(behavior_result, notes, actions),
        drawdown_penalty=_drawdown_penalty(session_replay_result, notes, actions),
        rule_violation_penalty=_rule_violation_penalty(session_replay_result, journal_result, journal_entries, notes, actions),
        overtrading_penalty=_class_penalty(
            behavior_result,
            class_name="OVERTRADING",
            component_name="overtrading_penalty",
            penalty=-35,
            reason="Overtrading detected.",
            action="Set a hard trade-count stop before the next session.",
            notes=notes,
            actions=actions,
        ),
        revenge_trading_penalty=_class_penalty(
            behavior_result,
            class_name="REVENGE_TRADING_PROBABLE",
            component_name="revenge_trading_penalty",
            penalty=-45,
            reason="Revenge trading probable.",
            action="Require a cooldown after losses before evaluating another trade.",
            notes=notes,
            actions=actions,
        ),
        strategy_compliance_reward=_strategy_compliance_reward(
            paper_execution_result,
            context_score,
            market_regime,
            strategy_dna,
            notes,
            actions,
        ),
        memory_improvement_reward=_memory_improvement_reward(memory_profile, behavior_result, notes, actions),
    )
    components = _components(breakdown)
    total_reward = sum(component.value for component in components)
    normalized_reward = _clamp(50 + round(total_reward / 5))
    label = _label(normalized_reward)

    return RewardEvaluationResult(
        total_reward=total_reward,
        normalized_reward=normalized_reward,
        reward_label=label,
        breakdown=breakdown,
        learning_notes=tuple(dict.fromkeys(notes or ["Insufficient context; reward is mostly neutral."])),
        improvement_actions=tuple(dict.fromkeys(actions or ["Continue collecting offline evaluation data."])),
    )


def render_reward_evaluation_markdown(result: RewardEvaluationResult) -> str:
    """Render a reward evaluation as Markdown."""
    penalties = tuple(component for component in _components(result.breakdown) if component.value < 0)
    positives = tuple(component for component in _components(result.breakdown) if component.value > 0)
    lines = [
        "# Trading Reward Evaluation",
        "",
        "## Reward total",
        "",
        f"- Total reward: {result.total_reward}",
        f"- Normalized reward: {result.normalized_reward}/100",
        "",
        "## Label",
        "",
        f"- {result.reward_label.value}",
        "",
        "## Detail composants",
        "",
        *_component_lines(_components(result.breakdown)),
        "",
        "## Penalites",
        "",
        *_component_lines(penalties),
        "",
        "## Ce qui a ete bien fait",
        "",
        *_component_lines(positives),
        "",
        "## Ce qui doit etre ameliore",
        "",
        *_bullet_lines(result.improvement_actions),
        "",
        "## Utilisation future pour RL offline",
        "",
        "- This deterministic reward can be logged as an offline policy-evaluation target.",
        "- It uses no external ML, broker, market API, or real execution.",
        "",
    ]
    return "\n".join(lines)


def _pnl_reward(
    paper: PaperExecutionResult | None,
    context: ContextScoringResult | None,
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    pnl = _realized_pnl(paper)
    if pnl > 0:
        notes.append("Positive simulated PnL was achieved.")
        return RewardComponent("pnl_reward", _clamp_signed(20 + min(40, int(pnl))), "Positive simulated PnL.")
    if pnl < 0:
        actions.append("Review why the decision produced negative simulated PnL.")
        penalty = max(-70, int(pnl))
        if context is not None and context.decision == TradeContextDecision.NO_TRADE:
            penalty -= 25
            actions.append("Never execute a losing decision in a NO_TRADE context.")
        return RewardComponent("pnl_reward", _clamp_signed(penalty), "Negative simulated PnL.")
    if paper is not None and paper.decision == PaperExecutionDecision.PAPER_ORDER_FILLED:
        return RewardComponent("pnl_reward", 5, "Paper order filled with flat realized PnL.")
    return RewardComponent("pnl_reward", 0, "No realized PnL available.")


def _risk_adjusted_reward(
    paper: PaperExecutionResult | None,
    semi: SemiAutoDecisionResult | None,
    context: ContextScoringResult | None,
    market: MarketRegimeAnalysis | None,
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    value = 10
    reasons: list[str] = ["Risk stayed within offline evaluation defaults."]
    filled = paper is not None and paper.decision == PaperExecutionDecision.PAPER_ORDER_FILLED
    qty = _order_quantity(paper)
    if filled and qty > 1 and context is not None and context.global_score < 65:
        value -= 35
        reasons.append("Size was high relative to context score.")
        actions.append("Reduce size when context score is below 65.")
    if filled and market is not None and market.dangerous_market:
        value -= 45
        reasons.append("Execution occurred in dangerous market conditions.")
        actions.append("Block or reduce risk when market regime is dangerous.")
    if semi is not None and semi.decision == SemiAutoDecision.APPROVE_REDUCED_RISK:
        value += 15
        notes.append("Reduced-risk approval was respected.")
    if paper is not None and not paper.accepted and market is not None and market.dangerous_market:
        value += 25
        notes.append("The system avoided execution in a dangerous market.")
    return RewardComponent("risk_adjusted_reward", _clamp_signed(value), " ".join(reasons))


def _discipline_reward(
    replay: SessionReplayResult | None,
    journal: JournalAnalysisResult | None,
    journal_entries: tuple[TradeJournalEntry, ...],
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    values: list[int] = []
    if replay is not None:
        values.append(int(replay.discipline_score) - 50)
    if journal is not None:
        compliance = (journal.playbook_compliance_rate + journal.risk_rules_compliance_rate) / 2
        values.append(round(compliance * 100) - 50)
    if journal_entries:
        compliance = sum(1 for entry in journal_entries if entry.followed_playbook and entry.followed_risk_rules)
        values.append(round((compliance / len(journal_entries)) * 100) - 50)
    if not values:
        return RewardComponent("discipline_reward", 0, "No discipline evidence provided.")
    value = _clamp_signed(round(sum(values) / len(values)))
    if value > 20:
        notes.append("Discipline and rule-following were strong.")
    if value < 0:
        actions.append("Improve playbook and risk-rule compliance before next evaluation.")
    return RewardComponent("discipline_reward", value, "Discipline derived from replay/journal evidence.")


def _context_alignment_reward(
    paper: PaperExecutionResult | None,
    semi: SemiAutoDecisionResult | None,
    context: ContextScoringResult | None,
    market: MarketRegimeAnalysis | None,
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    value = 0
    if context is not None:
        value += round((context.global_score - 50) / 2)
        if context.decision == TradeContextDecision.NO_TRADE and _paper_filled(paper):
            value -= 55
            actions.append("Do not approve paper execution when context decision is NO_TRADE.")
        if context.decision in (TradeContextDecision.STRONG_TRADE_ALLOWED, TradeContextDecision.TRADE_ALLOWED):
            value += 15
    if market is not None:
        if market.favorable_for_pullback_strategy:
            value += 20
            notes.append("Market regime aligned with the pullback strategy.")
        if market.dangerous_market:
            value -= 25
    if semi is not None:
        if semi.decision == SemiAutoDecision.APPROVE_TRADE and market is not None and market.dangerous_market:
            value -= 35
            actions.append("Avoid APPROVE_TRADE when market regime is dangerous.")
        if semi.decision in (SemiAutoDecision.BLOCK_TRADE, SemiAutoDecision.STOP_SESSION) and market is not None and market.dangerous_market:
            value += 35
            notes.append("Blocking the trade was correct in dangerous context.")
    return RewardComponent("context_alignment_reward", _clamp_signed(value), "Decision alignment with context and market regime.")


def _behavior_reward(
    behavior: BehaviorAnalysisResult | None,
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    if behavior is None:
        return RewardComponent("behavior_reward", 0, "No behavior analysis provided.")
    value = round((behavior.scores.discipline_score + behavior.scores.emotional_risk_score + behavior.scores.consistency_score) / 3) - 50
    classes = {_value(item) for item in behavior.classifications}
    if "DISCIPLINED" in classes:
        value += 10
    if "HIGH_RISK" in classes:
        value -= 20
        actions.append("Reduce risk when behavior intelligence marks HIGH_RISK.")
    if value > 20:
        notes.append("Behavior state supported the decision.")
    return RewardComponent("behavior_reward", _clamp_signed(value), "Behavior reward from discipline/emotional/consistency scores.")


def _drawdown_penalty(
    replay: SessionReplayResult | None,
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    if replay is None or not replay.sessions:
        return RewardComponent("drawdown_penalty", 0, "No drawdown evidence provided.")
    largest_loss = min((session.largest_loss for session in replay.sessions), default=0.0)
    if largest_loss >= 0:
        return RewardComponent("drawdown_penalty", 0, "No negative replay drawdown detected.")
    penalty = -min(60, int(abs(largest_loss) / 10))
    if penalty < -20:
        actions.append("Review drawdown controls and max-loss handling.")
    return RewardComponent("drawdown_penalty", penalty, "Penalty from largest replay loss.")


def _rule_violation_penalty(
    replay: SessionReplayResult | None,
    journal: JournalAnalysisResult | None,
    journal_entries: tuple[TradeJournalEntry, ...],
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    violations = 0
    if replay is not None:
        violations += sum(len(session.violations) for session in replay.sessions)
    if journal is not None:
        if journal.playbook_compliance_rate < 1.0:
            violations += 1
        if journal.risk_rules_compliance_rate < 1.0:
            violations += 1
    violations += sum(1 for entry in journal_entries if not entry.followed_playbook or not entry.followed_risk_rules)
    if violations == 0:
        notes.append("No playbook or risk-rule violation was detected.")
        return RewardComponent("rule_violation_penalty", 0, "No rule violation detected.")
    actions.append("Review every playbook/risk violation before the next session.")
    return RewardComponent("rule_violation_penalty", -min(80, violations * 15), f"{violations} rule violation signal(s).")


def _class_penalty(
    behavior: BehaviorAnalysisResult | None,
    *,
    class_name: str,
    component_name: str,
    penalty: int,
    reason: str,
    action: str,
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    classes = {_value(item) for item in behavior.classifications} if behavior is not None else set()
    if class_name in classes:
        actions.append(action)
        return RewardComponent(component_name, penalty, reason)
    return RewardComponent(component_name, 0, f"{class_name} not detected.")


def _strategy_compliance_reward(
    paper: PaperExecutionResult | None,
    context: ContextScoringResult | None,
    market: MarketRegimeAnalysis | None,
    strategy: StrategyDNA | None,
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    value = 0
    if strategy is not None:
        value += 10
    if context is not None and context.breakdown.strategy_regime_compatibility_score >= 75:
        value += 20
        notes.append("Strategy/regime compatibility was strong.")
    if market is not None and market.favorable_for_pullback_strategy:
        value += 15
    if _paper_filled(paper) and market is not None and not market.favorable_for_pullback_strategy:
        value -= 35
        actions.append("Avoid executing strategy when regime compatibility is weak.")
    return RewardComponent("strategy_compliance_reward", _clamp_signed(value), "Strategy compliance and regime compatibility.")


def _memory_improvement_reward(
    memory: TraderMemoryProfile | None,
    behavior: BehaviorAnalysisResult | None,
    notes: list[str],
    actions: list[str],
) -> RewardComponent:
    if memory is None or memory.sessions_count == 0:
        return RewardComponent("memory_improvement_reward", 0, "No adaptive memory baseline available.")
    current_discipline = behavior.scores.discipline_score if behavior is not None else memory.average_discipline_score
    current_emotional = behavior.scores.emotional_risk_score if behavior is not None else memory.average_emotional_risk_score
    discipline_delta = current_discipline - memory.average_discipline_score
    emotional_delta = current_emotional - memory.average_emotional_risk_score
    value = round((discipline_delta + emotional_delta) / 2)
    if memory.favorable_contexts:
        value += 10
    if memory.recurring_patterns:
        value -= 15
        actions.append("Address recurring patterns stored in adaptive memory.")
    if value > 0:
        notes.append("Current behavior improved versus adaptive memory baseline.")
    return RewardComponent("memory_improvement_reward", _clamp_signed(value), "Adaptive memory comparison reward.")


def _components(breakdown: RewardBreakdown) -> tuple[RewardComponent, ...]:
    return (
        breakdown.pnl_reward,
        breakdown.risk_adjusted_reward,
        breakdown.discipline_reward,
        breakdown.context_alignment_reward,
        breakdown.behavior_reward,
        breakdown.drawdown_penalty,
        breakdown.rule_violation_penalty,
        breakdown.overtrading_penalty,
        breakdown.revenge_trading_penalty,
        breakdown.strategy_compliance_reward,
        breakdown.memory_improvement_reward,
    )


def _realized_pnl(paper: PaperExecutionResult | None) -> float:
    if paper is None or paper.order_result is None or paper.order_result.position is None:
        return 0.0
    return paper.order_result.position.realized_pnl


def _order_quantity(paper: PaperExecutionResult | None) -> float:
    if paper is None or paper.order_result is None:
        return 0.0
    return paper.order_result.request.quantity


def _paper_filled(paper: PaperExecutionResult | None) -> bool:
    return bool(paper is not None and paper.decision == PaperExecutionDecision.PAPER_ORDER_FILLED)


def _component_lines(components: tuple[RewardComponent, ...]) -> list[str]:
    if not components:
        return ["- None"]
    return [f"- {component.name}: {component.value} ({component.reason})" for component in components]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _label(normalized_reward: int) -> RewardLabel:
    if normalized_reward >= 85:
        return RewardLabel.EXCELLENT_DECISION
    if normalized_reward >= 70:
        return RewardLabel.GOOD_DECISION
    if normalized_reward >= 50:
        return RewardLabel.ACCEPTABLE
    if normalized_reward >= 30:
        return RewardLabel.BAD_DECISION
    return RewardLabel.DANGEROUS_DECISION


def _value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


def _clamp_signed(value: int | float) -> int:
    return max(-100, min(100, int(round(value))))


__all__ = [
    "evaluate_trading_reward",
    "render_reward_evaluation_markdown",
]
