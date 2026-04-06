
import pytest
from unittest.mock import AsyncMock, MagicMock
from services.sor.main import SmartOrderRouter
from alpaca_trade_api.rest import REST

@pytest.fixture
def mock_alpaca_api():
    """Mocks the Alpaca API for testing purposes."""
    mock_api = MagicMock(spec=REST)
    mock_api.submit_order = MagicMock()
    mock_api.cancel_order = MagicMock()
    mock_api.get_order = MagicMock()
    return mock_api

@pytest.mark.asyncio
async def test_sor_limit_order_filled(mock_alpaca_api):
    """
    Test that a limit order is placed and filled when conditions are favorable.
    """
    sor = SmartOrderRouter(api=mock_alpaca_api, execution_timeout=1)
    
    # Simulate a tight spread and low volatility
    bid, ask, atr = 100.0, 100.01, 0.05
    symbol, quantity, side = "AAPL", 1, "buy"

    # Mock order response for submit_order to return an unfiiled order
    mock_alpaca_api.submit_order.return_value = MagicMock(id="order_123", status="new", order_type="limit", limit_price=round(bid + (ask - bid) * 0.5, 2), qty=1)
    
    # Mock order response for get_order: first call returns 'new', subsequent calls return 'filled'
    mock_alpaca_api.get_order.side_effect = [
        MagicMock(id="order_123", status="new", order_type="limit", limit_price=round(bid + (ask - bid) * 0.5, 2), qty=1),
        MagicMock(id="order_123", status="filled", order_type="limit", limit_price=round(bid + (ask - bid) * 0.5, 2), qty=1, filled_avg_price=round(bid + (ask - bid) * 0.5, 2))
    ]

    result_order = await sor.route_order(symbol, quantity, side, bid, ask, atr)

    mock_alpaca_api.submit_order.assert_called_once()
    assert result_order.status == "filled"
    assert result_order.order_type == "limit"
    assert result_order.limit_price == round(bid + (ask - bid) * 0.5, 2) # Should be aggressive but within spread

@pytest.mark.asyncio
async def test_sor_limit_order_fallback_to_market(mock_alpaca_api):
    """
    Test that a limit order falls back to a market order if not filled within timeout.
    """
    sor = SmartOrderRouter(api=mock_alpaca_api, execution_timeout=1)
    
    # Simulate a tight spread and low volatility
    bid, ask, atr = 100.0, 100.01, 0.05
    symbol, quantity, side = "AAPL", 1, "buy"

    # Mock order response for submit_order
    mock_alpaca_api.submit_order.return_value = MagicMock(id="order_456", status="new", order_type="limit", limit_price=100.00, qty=1)
    
    # Mock order response for get_order to simulate no fill (staying "new" for a few calls)
    # until timeout, then simulate cancellation, then market order submission.
    mock_alpaca_api.get_order.side_effect = [
        MagicMock(id="order_456", status="new", order_type="limit", limit_price=100.00, qty=1),
        MagicMock(id="order_456", status="new", order_type="limit", limit_price=100.00, qty=1),
        MagicMock(id="order_456", status="new", order_type="limit", limit_price=100.00, qty=1),
        MagicMock(id="order_456", status="canceled", order_type="limit", limit_price=100.00, qty=1), # After timeout, simulate cancellation
        MagicMock(id="market_order_789", status="filled", order_type="market", qty=1, filled_avg_price=100.05) # Market order filled
    ]

    # Mock market order submission
    mock_alpaca_api.submit_order.side_effect = [
        MagicMock(id="order_456", status="new", order_type="limit", limit_price=100.00, qty=1), # Limit order attempt
        MagicMock(id="market_order_789", status="filled", order_type="market", qty=1, filled_avg_price=100.05) # Market order after fallback
    ]

    result_order = await sor.route_order(symbol, quantity, side, bid, ask, atr)

    assert mock_alpaca_api.cancel_order.called
    assert result_order.order_type == "market"
    assert result_order.status == "filled"

@pytest.mark.asyncio
async def test_sor_market_order_direct(mock_alpaca_api):
    """
    Test that a market order is placed directly when conditions are unfavorable for limit.
    """
    sor = SmartOrderRouter(api=mock_alpaca_api, execution_timeout=1)
    
    # Simulate a wide spread and high volatility
    bid, ask, atr = 100.0, 101.0, 5.0 # Spread = 1.0, ATR = 5.0 -> spread < (atr * 0.1) is false
    symbol, quantity, side = "GOOG", 1, "sell"

    # Mock market order submission
    mock_alpaca_api.submit_order.return_value = MagicMock(id="order_abc", status="filled", order_type="market", qty=1, filled_avg_price=100.50)

    result_order = await sor.route_order(symbol, quantity, side, bid, ask, atr)

    mock_alpaca_api.submit_order.assert_called_once()
    assert result_order.order_type == "market"
    assert result_order.status == "filled"

@pytest.mark.asyncio
async def test_sor_aggressive_limit_buy(mock_alpaca_api):
    """
    Test aggressive limit price for buy in volatile market.
    """
    sor = SmartOrderRouter(api=mock_alpaca_api, execution_timeout=1)
    
    # Volatile market, use_limit_order is true (spread < atr * 0.1)
    bid, ask, atr = 100.0, 100.05, 1.0 # spread = 0.05, atr*0.1 = 0.1. spread < 0.1 is true. atr > spread*2 is true (1.0 > 0.1)
    symbol, quantity, side = "MSFT", 1, "buy"

    mock_alpaca_api.submit_order.return_value = MagicMock(id="order_buy_aggr", status="new", order_type="limit", limit_price=bid, qty=1)
    mock_alpaca_api.get_order.return_value = MagicMock(id="order_buy_aggr", status="filled", order_type="limit", limit_price=bid, qty=1, filled_avg_price=bid)

    result_order = await sor.route_order(symbol, quantity, side, bid, ask, atr)

    mock_alpaca_api.submit_order.assert_called_once()
    assert result_order.order_type == "limit"
    assert result_order.limit_price == bid

@pytest.mark.asyncio
async def test_sor_aggressive_limit_sell(mock_alpaca_api):
    """
    Test aggressive limit price for sell in volatile market.
    """
    sor = SmartOrderRouter(api=mock_alpaca_api, execution_timeout=1)
    
    # Volatile market, use_limit_order is true (spread < atr * 0.1)
    bid, ask, atr = 100.0, 100.05, 1.0 # spread = 0.05, atr*0.1 = 0.1. spread < 0.1 is true. atr > spread*2 is true (1.0 > 0.1)
    symbol, quantity, side = "MSFT", 1, "sell"

    mock_alpaca_api.submit_order.return_value = MagicMock(id="order_sell_aggr", status="new", order_type="limit", limit_price=ask, qty=1)
    mock_alpaca_api.get_order.return_value = MagicMock(id="order_sell_aggr", status="filled", order_type="limit", limit_price=ask, qty=1, filled_avg_price=ask)

    result_order = await sor.route_order(symbol, quantity, side, bid, ask, atr)

    mock_alpaca_api.submit_order.assert_called_once()
    assert result_order.order_type == "limit"
    assert result_order.limit_price == ask