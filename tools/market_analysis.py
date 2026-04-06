
import asyncio
import logging
from typing import Dict, Any
from alpaca_trade_api.rest import API
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

async def get_market_data(api: API, symbol: str) -> Dict[str, Any]:
    """
    Retrieves real-time market data (bid, ask, ATR) for a given symbol using Alpaca API.
    """
    try:
        # Get latest quote for bid/ask
        quote = api.get_latest_quote(symbol)
        bid_price = quote.bid_price
        ask_price = quote.ask_price

        # Calculate ATR for the last 14 days (common period for ATR)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=15) # Fetch one extra day for ATR calculation
        
        barset = api.get_bars(symbol, '1D', start=start_date.isoformat(), end=end_date.isoformat()).df
        
        if barset.empty:
            logger.warning(f"No historical data found for {symbol} to calculate ATR. Returning default ATR.")
            atr = 1.0 # Default ATR
        else:
            # Simplified ATR calculation (requires more robust implementation for production)
            # For a proper ATR, you need True Range for each period, and then average.
            # Here, we'll just use a simple volatility measure for demonstration.
            high_low_diff = barset['high'] - barset['low']
            close_prev_diff = abs(barset['close'].diff()) # Close vs previous close
            
            # True Range: max of (high-low, abs(high-prev_close), abs(low-prev_close))
            # This is a simplification; a full ATR calculation is more involved.
            true_ranges = [max(hl, cp) for hl, cp in zip(high_low_diff[1:], close_prev_diff[1:])]
            atr = sum(true_ranges) / len(true_ranges) if true_ranges else 1.0
            
            logger.info(f"Calculated ATR for {symbol}: {atr}")

        return {
            "bid": bid_price,
            "ask": ask_price,
            "atr": atr,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get market data for {symbol} from Alpaca API: {e}")
        # Fallback to mock data if API call fails
        return {
            "bid": 100.0,
            "ask": 100.1,
            "atr": 1.0,
            "timestamp": datetime.now().isoformat(),
            "mocked": True
        }

async def get_market_analysis_old(topic: str) -> Dict[str, Any]:
    """
    Placeholder for a tool that performs market analysis.
    
    In a real implementation, this would call the agicore-analytics service
    or another third-party API.
    """
    logger.info(f"Getting market analysis for topic: {topic}")
    # Simulate an async operation
    await asyncio.sleep(2)
    return {
        "topic": topic,
        "sentiment": "bullish",
        "forecast": "10% increase over the next quarter",
    }
