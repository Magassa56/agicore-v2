"""Unit tests for controlled offline paper execution loop."""
from __future__ import annotations

from agicore.trading.context_scoring_models import (
    ContextScoreBreakdown,
    ContextScoringResult,
    TradeContextDecision,
)
from agicore.trading.paper_execution_loop import (
    render_paper_execution_result_markdown,
    run_paper_execution_loop,
)
from agicore.trading.paper_execution_models import (
    PaperExecutionDecision,
    PaperExecutionEventType,
    PaperExecutionLoopConfig,
    PaperExecutionRequest,
)
from agicore.trading.paper_trading_adapter import MockPaperTradingAdapter
from agicore.trading.paper_trading_models import (
    PaperOrderRequest,
    PaperOrderSide,
    PaperOrderStatus,
    PaperOrderType,
)
from agicore.trading.semi_auto_decision_models import (
    SemiAutoAction,
    SemiAutoDecision,
    SemiAutoDecisionResult,
)
from agicore.trading.strategy_dna_models import StrategyDNA, TradeDirection


def _context(decision: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED) -> ContextScoringResult:
    return ContextScoringResult(
        global_score=75,
        decision=decision,
        breakdown=ContextScoreBreakdown(
            market_score=75,
            behavior_score=75,
            discipline_score=75,
            memory_score=75,
            emotional_score=75,
            volatility_score=75,
            strategy_regime_compatibility_score=75,
        ),
        favorable_factors=("clean context",),
        risk_factors=(),
        recommendations=("paper only",),
        strategy_regime_notes=("compatible",),
    )


def _semi(decision: SemiAutoDecision = SemiAutoDecision.APPROVE_TRADE) -> SemiAutoDecisionResult:
    return SemiAutoDecisionResult(
        decision=decision,
        action=SemiAutoAction.PREPARE_ORDER_PREVIEW,
        context_score=80,
        approval_reasons=("approved",),
        blocking_reasons=(),
        detected_risks=(),
        manual_confirmation_conditions=(),
        trader_message="offline preview",
    )


def _order(
    *,
    side: PaperOrderSide = PaperOrderSide.BUY,
    order_type: PaperOrderType = PaperOrderType.MARKET,
    risk_allowed: bool = True,
    trading_enabled: bool = True,
) -> PaperOrderRequest:
    return PaperOrderRequest(
        symbol="NQ",
        side=side,
        quantity=1.0,
        order_type=order_type,
        simulated_price=100.0,
        risk_allowed=risk_allowed,
        trading_enabled=trading_enabled,
    )


def _request(
    *,
    semi: SemiAutoDecision = SemiAutoDecision.APPROVE_TRADE,
    context: TradeContextDecision = TradeContextDecision.TRADE_ALLOWED,
    order: PaperOrderRequest | None = None,
    config: PaperExecutionLoopConfig | None = None,
    strategy: StrategyDNA | None = None,
) -> PaperExecutionRequest:
    return PaperExecutionRequest(
        semi_auto_decision=_semi(semi),
        context_score=_context(context),
        order_request=order or _order(),
        strategy_dna=strategy,
        config=config or PaperExecutionLoopConfig(),
    )


def test_run_paper_execution_loop_fills_after_prechecks() -> None:
    adapter = MockPaperTradingAdapter(starting_cash=10_000.0)

    result = run_paper_execution_loop(_request(), adapter=adapter)

    assert result.decision == PaperExecutionDecision.PAPER_ORDER_FILLED
    assert result.accepted is True
    assert result.precheck_passed is True
    assert result.order_result is not None
    assert result.order_result.status == PaperOrderStatus.FILLED
    assert adapter.get_account_state().cash == 9900.0
    assert [event.event_type for event in result.events] == [
        PaperExecutionEventType.LOOP_STARTED,
        PaperExecutionEventType.PRECHECK_PASSED,
        PaperExecutionEventType.PAPER_ORDER_SUBMITTED,
        PaperExecutionEventType.PAPER_ORDER_FILLED,
        PaperExecutionEventType.LOOP_COMPLETED,
    ]


def test_run_paper_execution_loop_rejects_blocking_semi_auto_decisions() -> None:
    result = run_paper_execution_loop(
        _request(semi=SemiAutoDecision.BLOCK_TRADE),
        adapter=MockPaperTradingAdapter(),
    )

    assert result.decision == PaperExecutionDecision.PRECHECK_REJECTED
    assert result.order_result is None
    assert any("BLOCK_TRADE" in reason for reason in result.precheck_reasons)
    assert PaperExecutionEventType.PRECHECK_FAILED in [event.event_type for event in result.events]


def test_run_paper_execution_loop_rejects_no_trade_and_high_risk_without_override() -> None:
    no_trade = run_paper_execution_loop(
        _request(context=TradeContextDecision.NO_TRADE),
        adapter=MockPaperTradingAdapter(),
    )
    high_risk = run_paper_execution_loop(
        _request(context=TradeContextDecision.HIGH_RISK_CONTEXT),
        adapter=MockPaperTradingAdapter(),
    )

    assert no_trade.decision == PaperExecutionDecision.PRECHECK_REJECTED
    assert any("NO_TRADE" in reason for reason in no_trade.precheck_reasons)
    assert high_risk.decision == PaperExecutionDecision.PRECHECK_REJECTED
    assert any("HIGH_RISK_CONTEXT" in reason for reason in high_risk.precheck_reasons)


def test_run_paper_execution_loop_allows_high_risk_with_explicit_override() -> None:
    result = run_paper_execution_loop(
        _request(
            context=TradeContextDecision.HIGH_RISK_CONTEXT,
            config=PaperExecutionLoopConfig(allow_high_risk_override=True),
        ),
        adapter=MockPaperTradingAdapter(),
    )

    assert result.decision == PaperExecutionDecision.PAPER_ORDER_FILLED
    assert result.accepted is True


def test_run_paper_execution_loop_rejects_risk_trading_max_orders_and_non_market() -> None:
    disabled = run_paper_execution_loop(
        _request(config=PaperExecutionLoopConfig(trading_enabled=False)),
        adapter=MockPaperTradingAdapter(),
    )
    risk_blocked = run_paper_execution_loop(
        _request(config=PaperExecutionLoopConfig(risk_allowed=False)),
        adapter=MockPaperTradingAdapter(),
    )
    max_orders = run_paper_execution_loop(
        _request(config=PaperExecutionLoopConfig(max_orders_per_session=1, submitted_orders_count=1)),
        adapter=MockPaperTradingAdapter(),
    )
    non_market = run_paper_execution_loop(
        _request(order=_order(order_type=PaperOrderType.LIMIT)),
        adapter=MockPaperTradingAdapter(),
    )

    assert any("Trading is disabled" in reason for reason in disabled.precheck_reasons)
    assert any("Risk is not allowed" in reason for reason in risk_blocked.precheck_reasons)
    assert any("Maximum paper orders" in reason for reason in max_orders.precheck_reasons)
    assert any("Only MARKET" in reason for reason in non_market.precheck_reasons)


def test_run_paper_execution_loop_rejects_strategy_direction_incompatibility() -> None:
    result = run_paper_execution_loop(
        _request(
            order=_order(side=PaperOrderSide.SELL),
            strategy=StrategyDNA(
                name="LongOnly",
                description="offline",
                allowed_direction=TradeDirection.LONG_ONLY,
            ),
        ),
        adapter=MockPaperTradingAdapter(),
    )

    assert result.decision == PaperExecutionDecision.PRECHECK_REJECTED
    assert any("StrategyDNA direction" in reason for reason in result.precheck_reasons)


def test_run_paper_execution_loop_reports_adapter_rejection_after_precheck() -> None:
    adapter = MockPaperTradingAdapter(trading_enabled=False)

    result = run_paper_execution_loop(_request(), adapter=adapter)

    assert result.precheck_passed is True
    assert result.decision == PaperExecutionDecision.PAPER_ORDER_REJECTED
    assert result.order_result is not None
    assert result.order_result.status == PaperOrderStatus.REJECTED
    assert PaperExecutionEventType.PAPER_ORDER_REJECTED in [event.event_type for event in result.events]


def test_render_paper_execution_result_markdown_contains_required_sections() -> None:
    result = run_paper_execution_loop(_request(), adapter=MockPaperTradingAdapter())

    markdown = render_paper_execution_result_markdown(result)

    assert "# Controlled Paper Execution Loop" in markdown
    assert "## Decision boucle" in markdown
    assert "## Prechecks" in markdown
    assert "## Ordre paper" in markdown
    assert "## Resultat simulated fill/rejection" in markdown
    assert "## Position/account simules" in markdown
    assert "## Avertissement securite" in markdown
    assert "No real order is sent" in markdown
