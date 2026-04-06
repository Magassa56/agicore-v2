
import logging
import time
import asyncio
from alpaca_trade_api.rest import REST

logger = logging.getLogger(__name__)

class SmartOrderRouter:
    """
    A Smart Order Router that dynamically adjusts order types and prices.
    """

    def __init__(self, api: REST, execution_timeout: int = 60):
        self.api = api
        self.execution_timeout = execution_timeout

    async def route_order(self, symbol: str, quantity: float, side: str, bid: float, ask: float, atr: float):
        """
        Routes an order with smart logic.

        Args:
            symbol (str): The ticker symbol.
            quantity (float): The quantity to trade.
            side (str): 'buy' or 'sell'.
            bid (float): The current best bid price.
            ask (float): The current best ask price.
            atr (float): The Average True Range.

        Returns:
            dict: The order parameters.
        """
        spread = ask - bid
        
        # Dynamic order type selection
        # If spread is tight and volatility is low, use a LIMIT order
        use_limit_order = spread < (atr * 0.1)  # Example threshold: 10% of ATR

        order_params = {
            "symbol": symbol,
            "qty": quantity,
            "side": side,
            "time_in_force": 'day',
        }

        if use_limit_order:
            # Adjust limit price based on spread and volatility
            if side == 'buy':
                limit_price = bid + (spread * 0.5)
                if atr > (spread * 2): # Volatile market
                    limit_price = bid # More aggressive
            else: # sell
                limit_price = ask - (spread * 0.5)
                if atr > (spread * 2): # Volatile market
                    limit_price = ask # More aggressive
            
            order_params.update({
                "type": "limit",
                "limit_price": round(limit_price, 2)
            })

            logger.info(f"Using LIMIT order for {symbol} at {limit_price}")
            
            try:
                # Submit limit order and wait for it to be filled
                order = self.api.submit_order(**order_params)
                logger.info(f"Submitted LIMIT order for {symbol}. Order ID: {order.id}")

                filled = await self._wait_for_fill(order.id)

                if not filled:
                    logger.warning(f"LIMIT order for {symbol} not filled within timeout. Switching to MARKET order.")
                    # Cancel the limit order
                    self.api.cancel_order(order.id)
                    order_params.update({"type": "market"})
                else:
                    logger.info(f"LIMIT order for {symbol} filled. Order ID: {order.id}")
                    # The order is filled, so we can just return the filled order
                    return self.api.get_order(order.id)


            except Exception as e:
                logger.error(f"Error in LIMIT order placement for {symbol}: {e}. Falling back to MARKET order.")
                order_params.update({"type": "market"})

        else:
            order_params.update({"type": "market"})
            logger.info(f"Spread too wide or market too volatile. Using MARKET order for {symbol}.")

        # If we reach here, it means we need to submit a market order
        if order_params.get("type") == "market":
            market_order = self.api.submit_order(**order_params)
            logger.info(f"Submitted MARKET order for {symbol}. Order ID: {market_order.id}")
            return market_order

    async def _wait_for_fill(self, order_id: str) -> bool:
        """
        Waits for an order to be filled.
        """
        start_time = time.time()
        while time.time() - start_time < self.execution_timeout:
            order = self.api.get_order(order_id)
            if order.status == 'filled':
                return True
            if order.status in ['canceled', 'rejected', 'expired']:
                return False
            await asyncio.sleep(1)
        return False
