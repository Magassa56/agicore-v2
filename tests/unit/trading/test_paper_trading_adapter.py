"""Unit tests for offline paper trading adapter."""
from __future__ import annotations

from agicore.trading.context_scoring_models import (
    ContextScoreBreakdown,
    ContextScoringResult,
    TradeContextDecision,
)
from agicore.trading.paper_trading_adapter import (
    MockPaperTradingAdapter,
    render_paper_order_result_markdown,
)
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
        recommendations=("paper preview only",),
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


def test_mock_paper_adapter_fills_market_order_and_updates_position_account() -> None:
    adapter = MockPaperTradingAdapter(starting_cash=10_000.0)
    request = PaperOrderRequest(
        symbol="NQ",
        side=PaperOrderSide.BUY,
        quantity=2.0,
        simulated_price=100.0,
    )

    result = adapter.submit_order(request, semi_auto_decision=_semi(), context_score=_context())

    assert result.status == PaperOrderStatus.FILLED
    assert result.accepted is True
    assert result.filled_quantity == 2.0
    assert result.fill_price == 100.0
    assert result.position is not None
    assert result.position.quantity == 2.0
    assert result.position.average_price == 100.0
    assert adapter.get_order(result.order_id) == result
    assert adapter.get_account_state().cash == 9800.0
    assert adapter.get_account_state().open_positions == 1


def test_mock_paper_adapter_tracks_realized_pnl_on_position_reduction() -> None:
    adapter = MockPaperTradingAdapter(starting_cash=10_000.0)
    adapter.submit_order(
        PaperOrderRequest(
            symbol="NQ",
            side=PaperOrderSide.BUY,
            quantity=2.0,
            simulated_price=100.0,
        )
    )

    result = adapter.submit_order(
        PaperOrderRequest(
            symbol="NQ",
            side=PaperOrderSide.SELL,
            quantity=1.0,
            simulated_price=110.0,
        )
    )

    assert result.status == PaperOrderStatus.FILLED
    assert result.position is not None
    assert result.position.quantity == 1.0
    assert result.position.realized_pnl == 10.0
    assert adapter.get_account_state().realized_pnl == 10.0


def test_mock_paper_adapter_rejects_disabled_or_risk_blocked_orders() -> None:
    disabled = MockPaperTradingAdapter(trading_enabled=False)

    disabled_result = disabled.submit_order(
        PaperOrderRequest(
            symbol="NQ",
            side=PaperOrderSide.BUY,
            quantity=1.0,
            simulated_price=100.0,
        )
    )
    risk_result = MockPaperTradingAdapter().submit_order(
        PaperOrderRequest(
            symbol="NQ",
            side=PaperOrderSide.BUY,
            quantity=1.0,
            simulated_price=100.0,
            risk_allowed=False,
        )
    )

    assert disabled_result.status == PaperOrderStatus.REJECTED
    assert "disabled" in disabled_result.reason
    assert risk_result.status == PaperOrderStatus.REJECTED
    assert "Risk gate" in risk_result.reason


def test_mock_paper_adapter_supports_market_only_and_strategy_direction() -> None:
    adapter = MockPaperTradingAdapter()
    limit_result = adapter.submit_order(
        PaperOrderRequest(
            symbol="NQ",
            side=PaperOrderSide.BUY,
            quantity=1.0,
            order_type=PaperOrderType.LIMIT,
            simulated_price=100.0,
        )
    )
    strategy_result = adapter.submit_order(
        PaperOrderRequest(
            symbol="NQ",
            side=PaperOrderSide.SELL,
            quantity=1.0,
            simulated_price=100.0,
        ),
        strategy_dna=StrategyDNA(
            name="LongOnly",
            description="offline",
            allowed_direction=TradeDirection.LONG_ONLY,
        ),
    )

    assert limit_result.status == PaperOrderStatus.REJECTED
    assert "Only MARKET" in limit_result.reason
    assert strategy_result.status == PaperOrderStatus.REJECTED
    assert "long-only" in strategy_result.reason


def test_mock_paper_adapter_rejects_blocking_semi_auto_and_no_trade_context() -> None:
    adapter = MockPaperTradingAdapter()
    request = PaperOrderRequest(
        symbol="NQ",
        side=PaperOrderSide.BUY,
        quantity=1.0,
        simulated_price=100.0,
    )

    blocked = adapter.submit_order(request, semi_auto_decision=_semi(SemiAutoDecision.BLOCK_TRADE))
    no_trade = adapter.submit_order(request, context_score=_context(TradeContextDecision.NO_TRADE))

    assert blocked.status == PaperOrderStatus.REJECTED
    assert "Semi-auto decision blocks" in blocked.reason
    assert no_trade.status == PaperOrderStatus.REJECTED
    assert "NO_TRADE" in no_trade.reason


def test_render_paper_order_result_markdown_contains_required_sections() -> None:
    adapter = MockPaperTradingAdapter()
    result = adapter.submit_order(
        PaperOrderRequest(
            symbol="NQ",
            side=PaperOrderSide.BUY,
            quantity=1.0,
            simulated_price=100.0,
        )
    )

    markdown = render_paper_order_result_markdown(result)

    assert "# Paper Trading Order Result" in markdown
    assert "## Ordre simule" in markdown
    assert "## Statut" in markdown
    assert "## Raison acceptation/refus" in markdown
    assert "## Position simulee" in markdown
    assert "## Compte simule" in markdown
    assert "## Avertissement paper/offline only" in markdown
    assert "No real order is sent" in markdown
