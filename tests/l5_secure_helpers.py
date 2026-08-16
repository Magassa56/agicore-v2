from __future__ import annotations

from datetime import datetime, timezone

from agicore.core.events import EventBus
from agicore.l5_action.broker_mock import MockBroker
from agicore.l5_action.execution_service import ExecutionService
from agicore.l5_action.execution_transaction import L5ExecutionTransactionStore
from agicore.risk.exposure_models import RiskLimits, empty_snapshot
from agicore.risk.risk_execution_context import InMemoryRiskContextProvider, RiskExecutionContext
from agicore.risk.risk_manager import RiskManager


TEST_TIME = datetime(2026, 8, 15, 10, 0, tzinfo=timezone.utc)


def make_execution_service(
    *,
    max_position_size: float = 100.0,
    max_exposure_value: float = 10_000_000.0,
    execution_enabled: bool = True,
    event_bus: EventBus | None = None,
) -> ExecutionService:
    limits = RiskLimits(
        max_position_size=max_position_size,
        max_exposure_value=max_exposure_value,
        max_drawdown_pct=0.5,
        daily_loss_limit=100_000.0,
    )
    snapshot = empty_snapshot(initial_equity=1_000_000.0)
    context = RiskExecutionContext(
        provider_id="test-canonical-l5",
        state_version=0,
        trading_day="2026-08-15",
        risk_limits=limits,
        exposure_snapshot=snapshot,
        signed_positions={"ES": 0.0, "NQ": 0.0},
        daily_realized_pnl=0.0,
        current_equity=1_000_000.0,
        peak_equity=1_000_000.0,
        execution_enabled=execution_enabled,
        kill_switch_active=False,
        legacy_hard_deny=False,
    )
    seed = InMemoryRiskContextProvider(context)
    price_provider = MockBroker(provider_id="test-l5-price")
    price_provider.set_market_price("ES", 100.0, observed_at=TEST_TIME)
    price_provider.set_market_price("NQ", 200.0, observed_at=TEST_TIME)
    store = L5ExecutionTransactionStore(
        initial_context=context,
        initial_risk_journal=seed.journal,
        price_provider=price_provider,
    )
    return ExecutionService(store, RiskManager(limits, event_bus=event_bus), price_provider)


def market_payload(
    suffix: str,
    *,
    symbol: str = "ES",
    side: str = "BUY",
    quantity: float = 1.0,
    price: float = 100.0,
) -> dict[str, object]:
    stamp = TEST_TIME.isoformat()
    return {
        "intent_id": f"intent-{suffix}",
        "symbol": symbol,
        "side": side,
        "quantity": quantity,
        "estimated_price": price,
        "timestamp": stamp,
        "order_type": "MARKET",
        "operation_id": f"operation-{suffix}",
        "order_id": f"order-{suffix}",
        "fill_id": f"fill-{suffix}",
        "report_id": f"report-{suffix}",
        "submitted_at": stamp,
        "filled_at": stamp,
    }
