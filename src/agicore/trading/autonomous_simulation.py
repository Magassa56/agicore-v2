"""Offline autonomous trading simulation core for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime

from .adaptive_policy_memory import update_policy_memory
from .adaptive_policy_memory_models import AdaptivePolicyMemory
from .autonomous_simulation_models import (
    AutonomousSimulationConfig,
    AutonomousSimulationEvent,
    AutonomousSimulationEventType,
    AutonomousSimulationResult,
    AutonomousSimulationStatus,
    AutonomousSimulationStep,
)
from .context_scoring import compute_trade_context_score
from .context_scoring_models import ContextScoringResult
from .market_regime import detect_market_regime
from .market_regime_models import MarketRegimeAnalysis
from .meta_strategy_models import MetaStrategyDecision
from .meta_strategy_selector import select_meta_strategy
from .offline_dataset import build_learning_transition, build_offline_learning_dataset
from .paper_execution_loop import run_paper_execution_loop
from .paper_execution_models import PaperExecutionLoopConfig, PaperExecutionRequest, PaperExecutionResult
from .paper_trading_adapter import MockPaperTradingAdapter, PaperTradingAdapter
from .paper_trading_models import PaperOrderRequest
from .policy_evaluation_models import PolicyEvaluationResult, PolicyRule, TradingPolicy
from .reward_function import evaluate_trading_reward
from .safe_rl_layer import validate_rl_experiment
from .safe_rl_models import SafeRLExperimentResult, SafeRLStatus
from .semi_auto_decision import build_semi_auto_decision
from .semi_auto_decision_models import SemiAutoDecision


def run_autonomous_trading_simulation(
    steps: tuple[AutonomousSimulationStep, ...] | list[AutonomousSimulationStep],
    *,
    config: AutonomousSimulationConfig | None = None,
    adapter: PaperTradingAdapter | None = None,
    initial_policy_memory: AdaptivePolicyMemory | None = None,
) -> AutonomousSimulationResult:
    """Run an end-to-end autonomous trading simulation offline only."""
    resolved_config = config or AutonomousSimulationConfig()
    resolved_adapter = adapter or MockPaperTradingAdapter(trading_enabled=resolved_config.trading_enabled)
    policy_memory = initial_policy_memory or AdaptivePolicyMemory()
    events: list[AutonomousSimulationEvent] = []
    processed_steps: list[AutonomousSimulationStep] = []
    transitions = []
    total_reward = 0
    executed_orders = 0
    blocked_orders = 0
    safe_rl_result: SafeRLExperimentResult | None = None
    status = AutonomousSimulationStatus.COMPLETED

    _event(events, AutonomousSimulationEventType.SIMULATION_STARTED, "Offline simulation started.", None)
    if not steps:
        status = AutonomousSimulationStatus.NO_STEPS
        _event(events, AutonomousSimulationEventType.SIMULATION_COMPLETED, "No simulation steps provided.", None)
        return _result(
            status=status,
            processed_steps=processed_steps,
            transitions=transitions,
            policy_memory=policy_memory,
            events=events,
            total_reward=total_reward,
            executed_orders=executed_orders,
            blocked_orders=blocked_orders,
            safe_rl_result=safe_rl_result,
        )

    for index, step in enumerate(tuple(steps)[: resolved_config.max_steps]):
        _event(events, AutonomousSimulationEventType.STEP_STARTED, f"Step {step.step_id} started.", step.step_id)
        session_trade_count = executed_orders
        market = _resolve_market(step)
        _event(events, AutonomousSimulationEventType.MARKET_REGIME_DETECTED, f"Market regime: {market.primary_regime.value}.", step.step_id)

        context = _resolve_context(step, market)
        _event(events, AutonomousSimulationEventType.CONTEXT_SCORED, f"Context score: {context.global_score}/100.", step.step_id)

        meta = select_meta_strategy(
            adaptive_policy_memory=policy_memory,
            safe_rl_result=safe_rl_result,
            context_score=context,
            market_regime=market,
            behavior_result=step.behavior_result,
            strategy_dna=step.strategy_dna,
        )
        _event(events, AutonomousSimulationEventType.META_STRATEGY_SELECTED, f"Meta decision: {meta.decision.value}.", step.step_id)

        semi = build_semi_auto_decision(
            context_score=context,
            market_regime=market,
            behavior_result=step.behavior_result,
            strategy_dna=step.strategy_dna,
        )
        _event(events, AutonomousSimulationEventType.SEMI_AUTO_DECISION_BUILT, f"Semi-auto decision: {semi.decision.value}.", step.step_id)

        paper = _maybe_execute_paper_order(
            step=step,
            context=context,
            semi=semi,
            config=resolved_config,
            adapter=resolved_adapter,
            submitted_orders_count=executed_orders,
            events=events,
        )
        if paper is None:
            blocked_orders += 1
            _event(events, AutonomousSimulationEventType.PAPER_EXECUTION_SKIPPED, "Paper execution skipped by guardrails.", step.step_id)
        else:
            if paper.accepted:
                executed_orders += 1
            else:
                blocked_orders += 1
            _event(events, AutonomousSimulationEventType.PAPER_EXECUTION_COMPLETED, f"Paper execution: {paper.decision.value}.", step.step_id)

        reward = evaluate_trading_reward(
            paper_execution_result=paper,
            semi_auto_decision=semi,
            context_score=context,
            behavior_result=step.behavior_result,
            market_regime=market,
            strategy_dna=step.strategy_dna,
        )
        total_reward += reward.total_reward
        _event(events, AutonomousSimulationEventType.REWARD_EVALUATED, f"Reward: {reward.total_reward}.", step.step_id)

        effective_policy_name = _effective_policy_name(meta.decision, meta.selected_policy_name)
        transition = build_learning_transition(
            context_score=context,
            market_regime=market,
            behavior_result=step.behavior_result,
            strategy_dna=step.strategy_dna,
            hour_of_day=step.hour_of_day,
            session_trade_count=session_trade_count,
            policy_name=effective_policy_name,
            semi_auto_decision=semi,
            paper_execution_result=paper,
            reward_result=reward,
            next_context_score=context,
            next_market_regime=market,
            next_behavior_result=step.behavior_result,
            next_strategy_dna=step.strategy_dna,
            next_hour_of_day=step.hour_of_day,
            next_session_trade_count=executed_orders,
            source_id=step.step_id,
        )
        transitions.append(transition)
        _event(events, AutonomousSimulationEventType.LEARNING_TRANSITION_BUILT, "Learning transition built.", step.step_id)

        policy_memory = _update_memory(
            policy_memory,
            policy_name=effective_policy_name,
            context=context,
            paper=paper,
            reward=reward,
            market=market,
            behavior=step.behavior_result,
            strategy_name=step.strategy_dna.name if step.strategy_dna is not None else None,
        )
        _event(events, AutonomousSimulationEventType.POLICY_MEMORY_UPDATED, "Policy memory updated.", step.step_id)

        dataset = build_offline_learning_dataset(transitions)
        safe_rl_result = validate_rl_experiment(
            dataset=dataset,
            context_score=context,
            market_regime=market,
            behavior_result=step.behavior_result,
            semi_auto_decision=semi,
            reward_result=reward,
            config=resolved_config.safe_rl_config,
        )
        _event(events, AutonomousSimulationEventType.SAFE_RL_VALIDATED, f"Safe RL status: {safe_rl_result.status.value}.", step.step_id)

        processed_steps.append(
            AutonomousSimulationStep(
                step_id=step.step_id,
                prices=step.prices,
                ema_fast=step.ema_fast,
                ema_slow=step.ema_slow,
                atr=step.atr,
                ranges=step.ranges,
                volume=step.volume,
                timestamps=step.timestamps,
                order_request=step.order_request,
                market_regime=market,
                context_score=context,
                behavior_result=step.behavior_result,
                strategy_dna=step.strategy_dna,
                hour_of_day=step.hour_of_day,
                session_trade_count=session_trade_count,
                meta_strategy_result=meta,
                semi_auto_decision=semi,
                paper_execution_result=paper,
                reward_result=reward,
                learning_transition=transition,
                safe_rl_result=safe_rl_result,
            )
        )

        status = _stop_status(
            safe_rl_result=safe_rl_result,
            executed_orders=executed_orders,
            total_reward=total_reward,
            semi_decision=semi.decision,
            config=resolved_config,
        )
        if status != AutonomousSimulationStatus.COMPLETED:
            _event(events, AutonomousSimulationEventType.GUARDRAIL_STOP, f"Simulation stopped: {status.value}.", step.step_id)
            break
        if index + 1 >= resolved_config.max_steps:
            status = AutonomousSimulationStatus.STOPPED_MAX_STEPS
            _event(events, AutonomousSimulationEventType.GUARDRAIL_STOP, "Maximum steps reached.", step.step_id)
            break

    _event(events, AutonomousSimulationEventType.SIMULATION_COMPLETED, f"Simulation completed with status {status.value}.", None)
    return _result(
        status=status,
        processed_steps=processed_steps,
        transitions=transitions,
        policy_memory=policy_memory,
        events=events,
        total_reward=total_reward,
        executed_orders=executed_orders,
        blocked_orders=blocked_orders,
        safe_rl_result=safe_rl_result,
    )


def render_autonomous_simulation_markdown(result: AutonomousSimulationResult) -> str:
    """Render an offline autonomous simulation result as Markdown."""
    lines = [
        "# Autonomous Trading Simulation Core",
        "",
        "## Resume simulation",
        "",
        f"- Steps: {result.total_steps}",
        f"- Average reward: {result.average_reward:.2f}",
        "",
        "## Statut final",
        "",
        f"- {result.status.value}",
        "",
        "## Ordres paper simules",
        "",
        f"- Executed orders: {result.executed_orders}",
        "",
        "## Decisions bloquees",
        "",
        f"- Blocked orders: {result.blocked_orders}",
        "",
        "## Reward total",
        "",
        f"- Total reward: {result.total_reward}",
        "",
        "## Memoire politique finale",
        "",
        f"- Policies tracked: {len(result.final_policy_memory.entries)}",
        f"- Disabled policies: {len(result.final_policy_memory.disabled_policies)}",
        "",
        "## Dataset learning",
        "",
        f"- Transitions: {len(result.learning_dataset.transitions)}",
        f"- Name: {result.learning_dataset.name}",
        "",
        "## Safe RL status",
        "",
        f"- {result.safe_rl_result.status.value if result.safe_rl_result is not None else 'None'}",
        "",
        "## Limites / securite",
        "",
        f"- {result.safety_message}",
        "",
    ]
    return "\n".join(lines)


def _resolve_market(step: AutonomousSimulationStep) -> MarketRegimeAnalysis:
    if step.market_regime is not None:
        return step.market_regime
    return detect_market_regime(
        prices=step.prices,
        ema_fast=step.ema_fast,
        ema_slow=step.ema_slow,
        atr=step.atr,
        ranges=step.ranges,
        volume=step.volume,
        timestamps=step.timestamps,
        strategy_dna=step.strategy_dna,
        behavior_result=step.behavior_result,
    )


def _resolve_context(step: AutonomousSimulationStep, market: MarketRegimeAnalysis) -> ContextScoringResult:
    if step.context_score is not None:
        return step.context_score
    return compute_trade_context_score(
        market_regime=market,
        behavior_result=step.behavior_result,
        strategy_dna=step.strategy_dna,
    )


def _maybe_execute_paper_order(
    *,
    step: AutonomousSimulationStep,
    context: ContextScoringResult,
    semi,
    config: AutonomousSimulationConfig,
    adapter: PaperTradingAdapter,
    submitted_orders_count: int,
    events: list[AutonomousSimulationEvent],
) -> PaperExecutionResult | None:
    if step.order_request is None:
        return None
    if semi.decision in {SemiAutoDecision.BLOCK_TRADE, SemiAutoDecision.STOP_SESSION, SemiAutoDecision.REVIEW_ONLY}:
        return None
    request = _normalized_order(step.order_request, config)
    return run_paper_execution_loop(
        PaperExecutionRequest(
            semi_auto_decision=semi,
            context_score=context,
            order_request=request,
            strategy_dna=step.strategy_dna,
            config=PaperExecutionLoopConfig(
                trading_enabled=config.trading_enabled,
                risk_allowed=config.risk_allowed,
                allow_high_risk_override=config.allow_high_risk_override,
                max_orders_per_session=config.max_orders,
                submitted_orders_count=submitted_orders_count,
            ),
        ),
        adapter=adapter,
    )


def _normalized_order(request: PaperOrderRequest, config: AutonomousSimulationConfig) -> PaperOrderRequest:
    quantity = request.quantity if request.quantity > 0 else config.default_order_quantity
    return PaperOrderRequest(
        symbol=request.symbol,
        side=request.side,
        quantity=quantity,
        order_type=request.order_type,
        simulated_price=request.simulated_price,
        risk_allowed=request.risk_allowed and config.risk_allowed,
        trading_enabled=request.trading_enabled and config.trading_enabled,
        client_order_id=request.client_order_id,
    )


def _update_memory(
    memory: AdaptivePolicyMemory,
    *,
    policy_name: str | None,
    context: ContextScoringResult,
    paper: PaperExecutionResult | None,
    reward,
    market: MarketRegimeAnalysis,
    behavior,
    strategy_name: str | None,
) -> AdaptivePolicyMemory:
    if policy_name is None:
        return memory
    policy = _policy(policy_name)
    result = PolicyEvaluationResult(
        policy=policy,
        rule=PolicyRule(
            policy=policy,
            min_context_score=60,
            reduce_risk_below_score=70,
            block_high_risk_context=True,
            allow_high_risk_override=False,
            reduce_size_on_caution=True,
            block_revenge_trading=True,
            block_overtrading=True,
            long_only="LONG_ONLY" in policy.value,
        ),
        total_reward=reward.total_reward,
        normalized_reward=reward.normalized_reward,
        accepted_trades=1 if paper is not None and paper.accepted else 0,
        blocked_trades=0 if paper is not None and paper.accepted else 1,
        reduced_risk_trades=1 if reward.breakdown.risk_adjusted_reward.value > 10 else 0,
        dangerous_decisions=1 if reward.normalized_reward < 30 else 0,
        average_context_score=float(context.global_score),
        average_reward=float(reward.total_reward),
        best_policy=False,
        best_policy_reason="autonomous_simulation_snapshot",
        scenario_count=1,
        semi_auto_decisions=(),
        paper_execution_results=(),
        reward_results=(),
        risk_notes=reward.improvement_actions,
    )
    return update_policy_memory(
        memory,
        policy_results=(result,),
        market_regime=market,
        behavior_result=behavior,
        strategy_name=strategy_name,
    )


def _policy(name: str) -> TradingPolicy:
    try:
        return TradingPolicy(name)
    except ValueError:
        return TradingPolicy.CONSERVATIVE


def _effective_policy_name(decision: MetaStrategyDecision, selected_policy_name: str | None) -> str | None:
    if selected_policy_name is not None:
        return selected_policy_name
    if decision in {MetaStrategyDecision.NO_STRATEGY, MetaStrategyDecision.FALLBACK_TO_CONSERVATIVE}:
        return TradingPolicy.CONSERVATIVE.value
    return None


def _stop_status(
    *,
    safe_rl_result: SafeRLExperimentResult,
    executed_orders: int,
    total_reward: int,
    semi_decision: SemiAutoDecision,
    config: AutonomousSimulationConfig,
) -> AutonomousSimulationStatus:
    if safe_rl_result.status == SafeRLStatus.BLOCKED:
        return AutonomousSimulationStatus.STOPPED_SAFE_RL_BLOCKED
    if executed_orders >= config.max_orders:
        return AutonomousSimulationStatus.STOPPED_MAX_ORDERS
    if total_reward <= -abs(config.daily_loss_limit):
        return AutonomousSimulationStatus.STOPPED_DAILY_LOSS_LIMIT
    if semi_decision == SemiAutoDecision.STOP_SESSION:
        return AutonomousSimulationStatus.STOPPED_SESSION
    return AutonomousSimulationStatus.COMPLETED


def _result(
    *,
    status: AutonomousSimulationStatus,
    processed_steps: list[AutonomousSimulationStep],
    transitions,
    policy_memory: AdaptivePolicyMemory,
    events: list[AutonomousSimulationEvent],
    total_reward: int,
    executed_orders: int,
    blocked_orders: int,
    safe_rl_result: SafeRLExperimentResult | None,
) -> AutonomousSimulationResult:
    dataset = build_offline_learning_dataset(transitions)
    average_reward = round(total_reward / len(processed_steps), 2) if processed_steps else 0.0
    return AutonomousSimulationResult(
        total_steps=len(processed_steps),
        executed_orders=executed_orders,
        blocked_orders=blocked_orders,
        total_reward=total_reward,
        average_reward=average_reward,
        final_policy_memory=policy_memory,
        learning_dataset=dataset,
        event_log=tuple(events),
        status=status,
        safe_rl_result=safe_rl_result,
        steps=tuple(processed_steps),
    )


def _event(
    events: list[AutonomousSimulationEvent],
    event_type: AutonomousSimulationEventType,
    message: str,
    step_id: str | None,
) -> None:
    events.append(
        AutonomousSimulationEvent(
            event_type=event_type,
            message=message,
            step_id=step_id,
            timestamp=datetime.now(UTC),
        )
    )


__all__ = [
    "render_autonomous_simulation_markdown",
    "run_autonomous_trading_simulation",
]
