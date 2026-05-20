"""Unit tests for the offline autonomous trading simulation core."""
from __future__ import annotations

from agicore.trading.autonomous_simulation import (
    render_autonomous_simulation_markdown,
    run_autonomous_trading_simulation,
)
from agicore.trading.autonomous_simulation_models import (
    AutonomousSimulationConfig,
    AutonomousSimulationEventType,
    AutonomousSimulationStatus,
    AutonomousSimulationStep,
)
from agicore.trading.behavior_models import (
    BehaviorAnalysisResult,
    BehaviorRecommendation,
    BehaviorScores,
    BehaviorSummary,
    SessionBehaviorClass,
)
from agicore.trading.context_scoring_models import ContextScoreBreakdown, ContextScoringResult, TradeContextDecision
from agicore.trading.market_regime_models import (
    MarketRegime,
    MarketRegimeAnalysis,
    RegimeStrength,
    SessionCondition,
    VolatilityRegime,
)
from agicore.trading.paper_trading_adapter import MockPaperTradingAdapter
from agicore.trading.paper_trading_models import PaperOrderRequest, PaperOrderSide
from agicore.trading.safe_rl_models import SafeRLExperimentConfig
from agicore.trading.strategy_dna_models import StrategyDNA, TradeDirection


def _market(*, dangerous: bool = False) -> MarketRegimeAnalysis:
    return MarketRegimeAnalysis(
        primary_regime=MarketRegime.NEWS_RISK if dangerous else MarketRegime.TRENDING_UP,
        confidence=82,
        strength=RegimeStrength.STRONG,
        volatility=VolatilityRegime.EXTREME if dangerous else VolatilityRegime.NORMAL,
        session_condition=SessionCondition.DANGEROUS if dangerous else SessionCondition.FAVORABLE,
        context_quality_score=20 if dangerous else 86,
        favorable_for_pullback_strategy=not dangerous,
        dangerous_market=dangerous,
        detected_regimes=(MarketRegime.NEWS_RISK if dangerous else MarketRegime.TRENDING_UP,),
        warnings=(),
        recommendations=(),
    )


def _context(
    decision: TradeContextDecision = TradeContextDecision.STRONG_TRADE_ALLOWED,
    score: int = 88,
) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=score,
        decision=decision,
        breakdown=ContextScoreBreakdown(
            market_score=score,
            behavior_score=score,
            discipline_score=score,
            memory_score=score,
            emotional_score=score,
            volatility_score=score,
            strategy_regime_compatibility_score=score,
        ),
        favorable_factors=("clean context",),
        risk_factors=(),
        recommendations=(),
        strategy_regime_notes=(),
    )


def _behavior(*, high_risk: bool = False) -> BehaviorAnalysisResult:
    return BehaviorAnalysisResult(
        classifications=(SessionBehaviorClass.HIGH_RISK,) if high_risk else (SessionBehaviorClass.DISCIPLINED,),
        patterns=(),
        scores=BehaviorScores(
            discipline_score=80,
            emotional_risk_score=80 if high_risk else 65,
            consistency_score=80,
            risk_escalation_score=80 if high_risk else 20,
        ),
        recommendations=(BehaviorRecommendation.KEEP_CURRENT_RULES,),
        summary=BehaviorSummary(
            strengths=(),
            weaknesses=(),
            dangerous_hours=(),
            favorable_context="test",
            probable_trader_profile="test",
        ),
    )


def _strategy() -> StrategyDNA:
    return StrategyDNA(
        name="EMA20",
        description="offline",
        allowed_direction=TradeDirection.BOTH,
        ema_filter="EMA20 pullback",
    )


def _order(symbol: str = "MES") -> PaperOrderRequest:
    return PaperOrderRequest(
        symbol=symbol,
        side=PaperOrderSide.BUY,
        quantity=1,
        simulated_price=100.0,
    )


def test_run_autonomous_trading_simulation_executes_offline_step() -> None:
    result = run_autonomous_trading_simulation(
        (
            AutonomousSimulationStep(
                step_id="s1",
                order_request=_order(),
                market_regime=_market(),
                context_score=_context(),
                behavior_result=_behavior(),
                strategy_dna=_strategy(),
                hour_of_day=10,
            ),
        ),
        config=AutonomousSimulationConfig(max_steps=2, max_orders=2),
        adapter=MockPaperTradingAdapter(),
    )

    assert result.status == AutonomousSimulationStatus.COMPLETED
    assert result.total_steps == 1
    assert result.executed_orders == 1
    assert len(result.learning_dataset.transitions) == 1
    assert result.final_policy_memory.entries
    assert result.safe_rl_result is not None
    assert AutonomousSimulationEventType.PAPER_EXECUTION_COMPLETED in {event.event_type for event in result.event_log}


def test_run_autonomous_trading_simulation_blocks_dangerous_market_with_safe_rl_stop() -> None:
    result = run_autonomous_trading_simulation(
        (
            AutonomousSimulationStep(
                step_id="danger",
                order_request=_order(),
                market_regime=_market(dangerous=True),
                context_score=_context(TradeContextDecision.NO_TRADE, 20),
                behavior_result=_behavior(),
                strategy_dna=_strategy(),
            ),
        ),
        config=AutonomousSimulationConfig(max_steps=3, max_orders=3),
    )

    assert result.status == AutonomousSimulationStatus.STOPPED_SAFE_RL_BLOCKED
    assert result.executed_orders == 0
    assert result.blocked_orders == 1
    assert result.safe_rl_result is not None


def test_run_autonomous_trading_simulation_stops_on_max_orders() -> None:
    steps = tuple(
        AutonomousSimulationStep(
            step_id=f"s{index}",
            order_request=_order(f"MES{index}"),
            market_regime=_market(),
            context_score=_context(),
            behavior_result=_behavior(),
            strategy_dna=_strategy(),
        )
        for index in range(3)
    )

    result = run_autonomous_trading_simulation(
        steps,
        config=AutonomousSimulationConfig(max_steps=5, max_orders=1),
    )

    assert result.status == AutonomousSimulationStatus.STOPPED_MAX_ORDERS
    assert result.executed_orders == 1
    assert result.total_steps == 1


def test_run_autonomous_trading_simulation_can_detect_market_from_prices() -> None:
    result = run_autonomous_trading_simulation(
        (
            AutonomousSimulationStep(
                step_id="prices",
                prices=(100, 101, 102, 103, 104),
                ema_fast=(100, 101, 102, 103, 104),
                ema_slow=(99, 100, 101, 102, 103),
                atr=(1, 1, 1, 1, 1.1),
                ranges=(1, 1, 1, 1, 1.1),
                order_request=None,
                behavior_result=_behavior(),
                strategy_dna=_strategy(),
            ),
        ),
        config=AutonomousSimulationConfig(max_steps=1),
    )

    assert result.total_steps == 1
    assert result.steps[0].market_regime is not None
    assert result.learning_dataset.transitions[0].state.market_regime is not None


def test_run_autonomous_trading_simulation_honors_strict_safe_rl_config() -> None:
    result = run_autonomous_trading_simulation(
        (
            AutonomousSimulationStep(
                step_id="strict",
                order_request=_order(),
                market_regime=_market(),
                context_score=_context(),
                behavior_result=_behavior(),
                strategy_dna=_strategy(),
            ),
        ),
        config=AutonomousSimulationConfig(
            safe_rl_config=SafeRLExperimentConfig(min_dataset_quality_score=100, min_transitions_count=10),
        ),
    )

    assert result.status == AutonomousSimulationStatus.STOPPED_SAFE_RL_BLOCKED


def test_run_autonomous_trading_simulation_empty_steps() -> None:
    result = run_autonomous_trading_simulation(())

    assert result.status == AutonomousSimulationStatus.NO_STEPS
    assert result.total_steps == 0
    assert len(result.learning_dataset.transitions) == 0


def test_render_autonomous_simulation_markdown_contains_required_sections() -> None:
    result = run_autonomous_trading_simulation(
        (
            AutonomousSimulationStep(
                step_id="s1",
                order_request=_order(),
                market_regime=_market(),
                context_score=_context(),
                behavior_result=_behavior(),
                strategy_dna=_strategy(),
            ),
        ),
        config=AutonomousSimulationConfig(max_orders=2),
    )

    markdown = render_autonomous_simulation_markdown(result)

    assert "# Autonomous Trading Simulation Core" in markdown
    assert "## Resume simulation" in markdown
    assert "## Statut final" in markdown
    assert "## Ordres paper simules" in markdown
    assert "## Decisions bloquees" in markdown
    assert "## Reward total" in markdown
    assert "## Memoire politique finale" in markdown
    assert "## Dataset learning" in markdown
    assert "## Safe RL status" in markdown
    assert "## Limites / securite" in markdown
    assert "No broker" in markdown
