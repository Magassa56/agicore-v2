
import os
import sys
import logging
import json
import asyncio # NEW: for async operations
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import alpaca_trade_api as tradeapi
from pythonjsonlogger import jsonlogger
from google.cloud import pubsub_v1

# Add the parent directory of 'tools' to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from tools.security import SecureAPICredentials, is_kill_switch_active
from shared.models import SignalEvent
from services.sor.main import SmartOrderRouter # NEW
from tools.market_analysis import get_market_data # NEW

app = FastAPI(title="Execution Agent", version="1.0.0")

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

# --- Configuration ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
TRADE_SIGNALS_TOPIC = os.getenv("TRADE_SIGNALS_TOPIC", "trade-signals")
ALPACA_KEY_ID_SECRET = "alpaca_api_key_id"
ALPACA_SECRET_KEY_SECRET = "alpaca_secret_key"

api = None
secure_creds = None
smart_order_router: SmartOrderRouter = None # NEW

def subscribe_to_signals():
    """Subscribes to a Pub/Sub topic to receive trade signals."""
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(GCP_PROJECT_ID, "execution-agent-sub")

    def callback(message):
        logger.info(f"Received message: {message.data}")
        try:
            signal_data = json.loads(message.data)
            signal = SignalEvent(**signal_data)
            asyncio.run(execute_trade(signal)) # NEW: Run async execute_trade
            message.ack()
        except Exception as e:
            logger.error(f"Failed to process message: {e}")

    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    logger.info(f"Listening for messages on {subscription_path}..\n")

    # Wrap the streaming pull future in a try block to catch exceptions.
    try:
        streaming_pull_future.result()
    except Exception as e:
        logger.error(f"Listening for messages on {subscription_path} threw an exception: {e}")
        streaming_pull_future.cancel()

import threading

...

def subscribe_to_signals_background():
    """Runs the Pub/Sub subscription in a background thread."""
    subscribe_thread = threading.Thread(target=subscribe_to_signals, daemon=True)
    subscribe_thread.start()

@app.on_event("startup")
async def startup_event(): # NEW: Make startup_event async
    global api, secure_creds, smart_order_router # NEW: Add smart_order_router to global
    if not GCP_PROJECT_ID:
        logger.critical("GCP_PROJECT_ID environment variable not set.")
        sys.exit(1)

    try:
        logger.info("Initializing secure credential loader...")
        secure_creds = SecureAPICredentials(
            project_id=GCP_PROJECT_ID,
            key_id_secret=ALPACA_KEY_ID_SECRET,
            secret_key_secret=ALPACA_SECRET_KEY_SECRET
        )
        with secure_creds as creds:
            api = tradeapi.REST(creds['api_key'], creds['secret_key'], api_version='v2')
            api.get_account()
        logger.info("Alpaca API connection successful.")
        smart_order_router = SmartOrderRouter(api=api) # NEW: Initialize SmartOrderRouter
    except Exception as e:
        logger.critical(f"Failed to connect to Alpaca API: {e}")
        sys.exit(1)

    subscribe_to_signals_background()


from prometheus_fastapi_instrumentator import Instrumentator, Counter, Gauge, Histogram
import time

...

# --- Metrics Configuration ---
PNL = Gauge("pnl", "Profit and Loss")
WIN_RATE = Gauge("win_rate", "Win rate of the trading strategy")
DRAWDOWN = Gauge("drawdown", "Drawdown of the trading strategy")
TRADE_FREQUENCY = Counter("trade_frequency", "Frequency of trades")
API_RESPONSE_TIME = Histogram("api_response_time", "API response time for placing orders")
SLIPPAGE = Gauge("slippage", "Slippage per trade")
LATENCY_ADJUSTED_PNL = Gauge("latency_adjusted_pnl", "Latency-adjusted PnL")
LOSING_STREAK = Counter("losing_streak", "Consecutive losing trades")

...

# Instrument the app with Prometheus metrics
Instrumentator().instrument(app).expose(app)

...

# --- In-memory data store for trades (for simplicity, use a proper DB in production) ---
trades = []

...

@app.post("/execute_trade")
async def execute_trade(signal: SignalEvent): # NEW: Make execute_trade async
    if is_kill_switch_active(GCP_PROJECT_ID):
        raise HTTPException(status_code=503, detail="Trading is halted due to kill switch.")

    logger.info(f"Received trade signal: {signal}")

    try:
        if smart_order_router is None:
            raise RuntimeError("SmartOrderRouter not initialized.")

        # NEW: Fetch market data
        market_data = await get_market_data(api, signal.ticker)
        bid_price = market_data['bid']
        ask_price = market_data['ask']
        atr = market_data['atr']
        logger.info(f"Market data for {signal.ticker}: Bid={bid_price}, Ask={ask_price}, ATR={atr}")

        start_time = time.time()
        # NEW: Use SmartOrderRouter to route the order
        order = await smart_order_router.route_order(
            symbol=signal.ticker,
            quantity=signal.quantity,
            side=signal.action,
            bid=bid_price,
            ask=ask_price,
            atr=atr
        )
        response_time = time.time() - start_time
        API_RESPONSE_TIME.observe(response_time)

        trades.append(order)
        TRADE_FREQUENCY.inc()

        # --- PnL Calculation (simplified) ---
        if order.status == 'filled':
            fill_price = float(order.filled_avg_price)
            if order.side == 'buy':
                pnl = (fill_price * 1.05 - fill_price) * float(order.qty)
            else:
                pnl = (fill_price - fill_price * 0.95) * float(order.qty)
            PNL.inc(pnl)

            # --- Slippage Calculation (updated) ---
            # Compare filled price to the price that was intended (signal.price or limit_price if applicable)
            intended_price = signal.price
            if order.order_type == 'limit' and order.limit_price: # Check if limit price was set by SOR
                intended_price = float(order.limit_price)

            slippage = intended_price - fill_price if intended_price else 0
            SLIPPAGE.set(slippage)

            # --- Latency-Adjusted PnL (simplified) ---
            latency_penalty = response_time * 0.1 # $0.10 per second of latency
            LATENCY_ADJUSTED_PNL.inc(pnl - latency_penalty)

            # --- Win Rate & Losing Streak ---
            if pnl > 0:
                LOSING_STREAK.clear()
            else:
                LOSING_STREAK.inc()

            # --- Win Rate Calculation (simplified) ---
            profitable_trades = [t for t in trades if t.status == 'filled' and float(t.filled_avg_price) > 0] # Simplified
            WIN_RATE.set(len(profitable_trades) / len(trades))

        # --- Drawdown Calculation (placeholder) ---
        DRAWDOWN.set(0.1)

        logger.info(f"Successfully executed trade for {signal.ticker}. Order ID: {order.id} with type {order.order_type}.")
        return {"status": "success", "signal": signal, "order": order.__dict__} # NEW: Return order details
    except Exception as e:
        logger.error(f"Failed to execute trade: {e}", exc_info=True) # NEW: log exc_info
        raise HTTPException(status_code=500, detail=f"Failed to execute trade: {e}")



@app.get("/health")
def health_check():
    return {"status": "healthy"}
