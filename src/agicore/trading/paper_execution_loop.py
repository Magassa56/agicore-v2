"""Controlled offline paper execution loop for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime

from .context_scoring_models import ContextScoringResult, TradeContextDecision
from .paper_execution_models import (
    PaperExecutionDecision,
    PaperExecutionEvent,
    PaperExecutionEventType,
    PaperExecutionLoopConfig,
    PaperExecutionRequest,
    PaperExecutionResult,
)
from .paper_trading_adapter import PaperTradingAdapter
from .paper_trading_models import PaperOrderRequest, PaperOrderResult, PaperOrderStatus, PaperOrderType
from .playbook_models import TraderProfile
from .semi_auto_decision_models import SemiAutoDecision, SemiAutoDecisionResult
from .strategy_dna_models import StrategyDNA, TradeDirection

_SAFETY_MESSAGE = (
    "Offline paper execution only. No broker, API, NinjaTrader, Alpaca, Binance, "
    "Rithmic or Tradovate connection is used. No real order is sent."
)


def run_paper_execution_loop(
    request: PaperExecutionRequest,
    *,
    adapter: PaperTradingAdapter,
) -> PaperExecutionResult:
    """Run the controlled offline paper execution loop."""
    events: list[PaperExecutionEvent] = []
    _event(events, PaperExecutionEventType.LOOP_STARTED, "Paper execution loop started.")

    failures = _precheck_failures(
        semi_auto_decision=request.semi_auto_decision,
        context_score=request.context_score,
        order_request=request.order_request,
        strategy_dna=request.strategy_dna,
        trader_profile=request.trader_profile,
        config=request.config,
    )
    if failures:
        for failure in failures:
            _event(events, PaperExecutionEventType.PRECHECK_FAILED, failure)
        _event(events, PaperExecutionEventType.LOOP_COMPLETED, "Loop completed with precheck rejection.")
        return PaperExecutionResult(
            decision=PaperExecutionDecision.PRECHECK_REJECTED,
            accepted=False,
            precheck_passed=False,
            precheck_reasons=tuple(failures),
            order_result=None,
            events=tuple(events),
            safety_message=_SAFETY_MESSAGE,
        )

    _event(events, PaperExecutionEventType.PRECHECK_PASSED, "All offline paper prechecks passed.")
    _event(events, PaperExecutionEventType.PAPER_ORDER_SUBMITTED, "Submitting simulated paper order.")
    order_result = adapter.submit_order(
        request.order_request,
        semi_auto_decision=request.semi_auto_decision,
        strategy_dna=request.strategy_dna,
        trader_profile=request.trader_profile,
        context_score=request.context_score,
    )

    if order_result.status == PaperOrderStatus.FILLED:
        _event(events, PaperExecutionEventType.PAPER_ORDER_FILLED, order_result.reason)
        decision = PaperExecutionDecision.PAPER_ORDER_FILLED
        accepted = True
    else:
        _event(events, PaperExecutionEventType.PAPER_ORDER_REJECTED, order_result.reason)
        decision = PaperExecutionDecision.PAPER_ORDER_REJECTED
        accepted = False

    _event(events, PaperExecutionEventType.LOOP_COMPLETED, "Paper execution loop completed.")
    return PaperExecutionResult(
        decision=decision,
        accepted=accepted,
        precheck_passed=True,
        precheck_reasons=("All prechecks passed",),
        order_result=order_result,
        events=tuple(events),
        safety_message=_SAFETY_MESSAGE,
    )


def render_paper_execution_result_markdown(result: PaperExecutionResult) -> str:
    """Render a controlled paper execution loop result as Markdown."""
    order = result.order_result
    lines = [
        "# Controlled Paper Execution Loop",
        "",
        "## Decision boucle",
        "",
        f"- Decision: {result.decision.value}",
        f"- Accepted: {result.accepted}",
        "",
        "## Prechecks",
        "",
        *_bullet_lines(result.precheck_reasons),
        "",
        "## Ordre paper",
        "",
        *_order_lines(order),
        "",
        "## Resultat simulated fill/rejection",
        "",
        *_result_lines(order),
        "",
        "## Position/account simules",
        "",
        *_position_account_lines(order),
        "",
        "## Avertissement securite",
        "",
        f"- {result.safety_message}",
        "",
    ]
    return "\n".join(lines)


def _precheck_failures(
    *,
    semi_auto_decision: SemiAutoDecisionResult,
    context_score: ContextScoringResult,
    order_request: PaperOrderRequest,
    strategy_dna: StrategyDNA | None,
    trader_profile: TraderProfile | None,
    config: PaperExecutionLoopConfig,
) -> list[str]:
    failures: list[str] = []
    if semi_auto_decision.decision in {
        SemiAutoDecision.BLOCK_TRADE,
        SemiAutoDecision.STOP_SESSION,
        SemiAutoDecision.REVIEW_ONLY,
    }:
        failures.append(f"Semi-auto decision blocks execution: {semi_auto_decision.decision.value}.")
    if context_score.decision == TradeContextDecision.NO_TRADE:
        failures.append("Context decision is NO_TRADE.")
    if (
        context_score.decision == TradeContextDecision.HIGH_RISK_CONTEXT
        and not config.allow_high_risk_override
    ):
        failures.append("Context decision is HIGH_RISK_CONTEXT and override is disabled.")
    if not config.trading_enabled or not order_request.trading_enabled:
        failures.append("Trading is disabled for the paper execution loop.")
    if not config.risk_allowed or not order_request.risk_allowed:
        failures.append("Risk is not allowed for the paper execution loop.")
    if config.submitted_orders_count >= config.max_orders_per_session:
        failures.append("Maximum paper orders per session reached.")
    if order_request.order_type != PaperOrderType.MARKET:
        failures.append("Only MARKET paper orders are supported by the controlled loop.")
    if order_request.quantity <= 0:
        failures.append("Paper order quantity must be positive.")
    if order_request.simulated_price <= 0:
        failures.append("Paper order simulated price must be positive.")
    if strategy_dna is not None:
        if strategy_dna.allowed_direction == TradeDirection.LONG_ONLY and order_request.side.value == "SELL":
            failures.append("StrategyDNA direction is incompatible with SELL order.")
        if strategy_dna.allowed_direction == TradeDirection.SHORT_ONLY and order_request.side.value == "BUY":
            failures.append("StrategyDNA direction is incompatible with BUY order.")
    if trader_profile is not None and trader_profile.forbidden_conditions:
        failures.append("TraderProfile has forbidden conditions requiring review.")
    return failures


def _event(
    events: list[PaperExecutionEvent],
    event_type: PaperExecutionEventType,
    message: str,
) -> None:
    events.append(PaperExecutionEvent(event_type=event_type, message=message, timestamp=datetime.now(UTC)))


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _order_lines(order: PaperOrderResult | None) -> list[str]:
    if order is None:
        return ["- None submitted"]
    request = order.request
    return [
        f"- Order ID: {order.order_id}",
        f"- Symbol: {request.symbol}",
        f"- Side: {request.side.value}",
        f"- Quantity: {request.quantity}",
        f"- Type: {request.order_type.value}",
        f"- Simulated price: {request.simulated_price:.2f}",
    ]


def _result_lines(order: PaperOrderResult | None) -> list[str]:
    if order is None:
        return ["- No simulated order result"]
    return [
        f"- Status: {order.status.value}",
        f"- Accepted: {order.accepted}",
        f"- Reason: {order.reason}",
        f"- Filled quantity: {order.filled_quantity}",
        f"- Fill price: {order.fill_price if order.fill_price is not None else 'None'}",
    ]


def _position_account_lines(order: PaperOrderResult | None) -> list[str]:
    if order is None:
        return ["- None"]
    lines: list[str] = []
    if order.position is None:
        lines.append("- Position: None")
    else:
        lines.extend(
            [
                f"- Position symbol: {order.position.symbol}",
                f"- Position quantity: {order.position.quantity}",
                f"- Position average price: {order.position.average_price:.2f}",
                f"- Position realized PnL: {order.position.realized_pnl:.2f}",
            ]
        )
    if order.account_state is None:
        lines.append("- Account: None")
    else:
        lines.extend(
            [
                f"- Account cash: {order.account_state.cash:.2f}",
                f"- Account equity: {order.account_state.equity:.2f}",
                f"- Account realized PnL: {order.account_state.realized_pnl:.2f}",
                f"- Account open positions: {order.account_state.open_positions}",
            ]
        )
    return lines


__all__ = [
    "render_paper_execution_result_markdown",
    "run_paper_execution_loop",
]
