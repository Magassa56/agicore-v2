"""Offline paper trading adapter interface and in-memory mock implementation."""
from __future__ import annotations

from typing import Protocol
from uuid import uuid4

from .context_scoring_models import ContextScoringResult, TradeContextDecision
from .paper_trading_models import (
    PaperAccountState,
    PaperOrderRequest,
    PaperOrderResult,
    PaperOrderSide,
    PaperOrderStatus,
    PaperOrderType,
    PaperPosition,
)
from .playbook_models import TraderProfile
from .semi_auto_decision_models import SemiAutoDecision, SemiAutoDecisionResult
from .strategy_dna_models import StrategyDNA, TradeDirection


class PaperTradingAdapter(Protocol):
    """Abstract interface for offline/paper trading adapters."""

    def submit_order(
        self,
        request: PaperOrderRequest,
        *,
        semi_auto_decision: SemiAutoDecisionResult | None = None,
        strategy_dna: StrategyDNA | None = None,
        trader_profile: TraderProfile | None = None,
        context_score: ContextScoringResult | None = None,
    ) -> PaperOrderResult:
        """Submit a simulated order request."""

    def cancel_order(self, order_id: str) -> PaperOrderResult:
        """Cancel a simulated order if it is cancelable."""

    def get_order(self, order_id: str) -> PaperOrderResult | None:
        """Return a simulated order result by id."""

    def get_positions(self) -> tuple[PaperPosition, ...]:
        """Return current simulated positions."""

    def get_account_state(self) -> PaperAccountState:
        """Return current simulated account state."""


class MockPaperTradingAdapter:
    """In-memory offline paper adapter. It never connects to a broker."""

    def __init__(self, *, starting_cash: float = 100_000.0, trading_enabled: bool = True) -> None:
        self._starting_cash = float(starting_cash)
        self._cash = float(starting_cash)
        self._trading_enabled = trading_enabled
        self._orders: dict[str, PaperOrderResult] = {}
        self._positions: dict[str, PaperPosition] = {}

    def submit_order(
        self,
        request: PaperOrderRequest,
        *,
        semi_auto_decision: SemiAutoDecisionResult | None = None,
        strategy_dna: StrategyDNA | None = None,
        trader_profile: TraderProfile | None = None,
        context_score: ContextScoringResult | None = None,
    ) -> PaperOrderResult:
        """Submit and immediately fill a supported market order in memory."""
        order_id = request.client_order_id or f"paper-{uuid4().hex[:12]}"
        rejection = self._rejection_reason(
            request,
            semi_auto_decision=semi_auto_decision,
            strategy_dna=strategy_dna,
            trader_profile=trader_profile,
            context_score=context_score,
        )
        if rejection:
            return self._store(
                PaperOrderResult(
                    order_id=order_id,
                    request=request,
                    status=PaperOrderStatus.REJECTED,
                    accepted=False,
                    reason=rejection,
                    account_state=self.get_account_state(),
                )
            )

        position = self._fill_market_order(request)
        return self._store(
            PaperOrderResult(
                order_id=order_id,
                request=request,
                status=PaperOrderStatus.FILLED,
                accepted=True,
                reason="Simulated market order filled offline.",
                filled_quantity=request.quantity,
                fill_price=request.simulated_price,
                position=position,
                account_state=self.get_account_state(),
            )
        )

    def cancel_order(self, order_id: str) -> PaperOrderResult:
        """Cancel an accepted simulated order; filled/rejected orders stay final."""
        order = self._orders.get(order_id)
        if order is None:
            request = PaperOrderRequest(
                symbol="UNKNOWN",
                side=PaperOrderSide.BUY,
                quantity=0.0,
            )
            return PaperOrderResult(
                order_id=order_id,
                request=request,
                status=PaperOrderStatus.REJECTED,
                accepted=False,
                reason="Order not found.",
                account_state=self.get_account_state(),
            )
        if order.status in (PaperOrderStatus.FILLED, PaperOrderStatus.REJECTED, PaperOrderStatus.CANCELED):
            return order
        canceled = PaperOrderResult(
            order_id=order.order_id,
            request=order.request,
            status=PaperOrderStatus.CANCELED,
            accepted=False,
            reason="Simulated order canceled offline.",
            account_state=self.get_account_state(),
        )
        return self._store(canceled)

    def get_order(self, order_id: str) -> PaperOrderResult | None:
        """Return a stored simulated order."""
        return self._orders.get(order_id)

    def get_positions(self) -> tuple[PaperPosition, ...]:
        """Return non-flat simulated positions."""
        return tuple(position for position in self._positions.values() if position.quantity != 0)

    def get_account_state(self) -> PaperAccountState:
        """Return current simulated account state."""
        realized = sum(position.realized_pnl for position in self._positions.values())
        return PaperAccountState(
            cash=round(self._cash, 2),
            equity=round(self._cash, 2),
            realized_pnl=round(realized, 2),
            open_positions=len(self.get_positions()),
            trading_enabled=self._trading_enabled,
        )

    def _rejection_reason(
        self,
        request: PaperOrderRequest,
        *,
        semi_auto_decision: SemiAutoDecisionResult | None,
        strategy_dna: StrategyDNA | None,
        trader_profile: TraderProfile | None,
        context_score: ContextScoringResult | None,
    ) -> str | None:
        if not self._trading_enabled or not request.trading_enabled:
            return "Paper trading is disabled."
        if not request.risk_allowed:
            return "Risk gate rejected the simulated order."
        if request.order_type != PaperOrderType.MARKET:
            return "Only MARKET orders are supported by the mock paper adapter."
        if request.quantity <= 0:
            return "Quantity must be positive."
        if request.simulated_price <= 0:
            return "Simulated market price must be positive."
        if semi_auto_decision is not None and semi_auto_decision.decision in {
            SemiAutoDecision.BLOCK_TRADE,
            SemiAutoDecision.STOP_SESSION,
            SemiAutoDecision.REVIEW_ONLY,
        }:
            return f"Semi-auto decision blocks paper order: {semi_auto_decision.decision.value}."
        if context_score is not None and context_score.decision == TradeContextDecision.NO_TRADE:
            return "Context scoring decision is NO_TRADE."
        if strategy_dna is not None:
            direction = strategy_dna.allowed_direction
            if direction == TradeDirection.LONG_ONLY and request.side == PaperOrderSide.SELL:
                return "Strategy DNA allows long-only paper orders."
            if direction == TradeDirection.SHORT_ONLY and request.side == PaperOrderSide.BUY:
                return "Strategy DNA allows short-only paper orders."
        if trader_profile is not None and trader_profile.forbidden_conditions:
            return "Trader profile has forbidden conditions requiring manual review."
        return None

    def _fill_market_order(self, request: PaperOrderRequest) -> PaperPosition:
        existing = self._positions.get(
            request.symbol,
            PaperPosition(symbol=request.symbol, quantity=0.0, average_price=0.0),
        )
        signed_qty = request.quantity if request.side == PaperOrderSide.BUY else -request.quantity
        old_qty = existing.quantity
        new_qty = old_qty + signed_qty
        realized = existing.realized_pnl
        average_price = existing.average_price

        if old_qty == 0 or old_qty * signed_qty > 0:
            total_cost = abs(old_qty) * average_price + abs(signed_qty) * request.simulated_price
            total_qty = abs(old_qty) + abs(signed_qty)
            average_price = total_cost / total_qty if total_qty else 0.0
        else:
            closing_qty = min(abs(old_qty), abs(signed_qty))
            if old_qty > 0:
                realized += (request.simulated_price - average_price) * closing_qty
            else:
                realized += (average_price - request.simulated_price) * closing_qty
            if new_qty == 0:
                average_price = 0.0
            elif old_qty * new_qty < 0:
                average_price = request.simulated_price

        self._cash -= signed_qty * request.simulated_price
        position = PaperPosition(
            symbol=request.symbol,
            quantity=round(new_qty, 8),
            average_price=round(average_price, 8),
            realized_pnl=round(realized, 2),
        )
        self._positions[request.symbol] = position
        return position

    def _store(self, result: PaperOrderResult) -> PaperOrderResult:
        self._orders[result.order_id] = result
        return result


def render_paper_order_result_markdown(result: PaperOrderResult) -> str:
    """Render a simulated paper order result as Markdown."""
    position = result.position
    account = result.account_state
    lines = [
        "# Paper Trading Order Result",
        "",
        "## Ordre simule",
        "",
        f"- Order ID: {result.order_id}",
        f"- Symbol: {result.request.symbol}",
        f"- Side: {result.request.side.value}",
        f"- Quantity: {result.request.quantity}",
        f"- Type: {result.request.order_type.value}",
        f"- Simulated price: {result.request.simulated_price:.2f}",
        "",
        "## Statut",
        "",
        f"- Status: {result.status.value}",
        f"- Accepted: {result.accepted}",
        "",
        "## Raison acceptation/refus",
        "",
        f"- {result.reason}",
        "",
        "## Position simulee",
        "",
        *_position_lines(position),
        "",
        "## Compte simule",
        "",
        *_account_lines(account),
        "",
        "## Avertissement paper/offline only",
        "",
        "- Offline paper simulation only. No broker, API, NinjaTrader, Alpaca, Binance, Rithmic or Tradovate connection is used.",
        "- No real order is sent.",
        "",
    ]
    return "\n".join(lines)


def _position_lines(position: PaperPosition | None) -> list[str]:
    if position is None:
        return ["- None"]
    return [
        f"- Symbol: {position.symbol}",
        f"- Quantity: {position.quantity}",
        f"- Average price: {position.average_price:.2f}",
        f"- Realized PnL: {position.realized_pnl:.2f}",
    ]


def _account_lines(account: PaperAccountState | None) -> list[str]:
    if account is None:
        return ["- None"]
    return [
        f"- Cash: {account.cash:.2f}",
        f"- Equity: {account.equity:.2f}",
        f"- Realized PnL: {account.realized_pnl:.2f}",
        f"- Open positions: {account.open_positions}",
        f"- Trading enabled: {account.trading_enabled}",
    ]


__all__ = [
    "MockPaperTradingAdapter",
    "PaperTradingAdapter",
    "render_paper_order_result_markdown",
]
