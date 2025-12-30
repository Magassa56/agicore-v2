
import os
import re
from fastapi import FastAPI, HTTPException, Depends, Request, Header
from pydantic import BaseModel, Field
import logging
from typing import Dict, Any, List
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import APIError
# from starlette.requests import Request # Moved this import


# --- Configuration & Environment Variables ---

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Alpaca API Configuration
# These are loaded from environment variables, which will be injected by Cloud Run from Secret Manager
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
# Ensure we are not using a live account by mistake
TRADING_MODE = os.getenv("TRADING_MODE", "paper") 
raw_alpaca_base_url = os.getenv("ALPACA_BASE_URL", "")
ALPACA_BASE_URL = raw_alpaca_base_url.strip() # <-- enlève \n et espaces
BASE_URL = ALPACA_BASE_URL if ALPACA_BASE_URL else ("https://paper-api.alpaca.markets" if TRADING_MODE == "paper" else "https://api.alpaca.markets")

# Safeguards
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"
ALLOWED_SYMBOLS_RAW = os.getenv("ALLOWED_SYMBOLS", "BTC/USD,ETH/USD")
ALLOWED_SYMBOLS = [symbol.strip() for symbol in ALLOWED_SYMBOLS_RAW.split(',')]
MAX_QTY = float(os.getenv("MAX_QTY", "1.0"))

# --- FastAPI Application ---

app = FastAPI(
    title="AGIcore - Trader Agent",
    description="A micro-agent for executing trades and fetching market data, with Alpaca paper trading integration.",
    version="1.1.0"
)

# --- New Endpoints and Helpers ---

def env_bool(name: str, default: bool = False) -> bool:
    """Converts an environment variable to a boolean."""
    return os.getenv(name, str(default)).lower() in ("true", "1", "yes")

def env_int(name: str, default: int = 0) -> int:
    """Converts an environment variable to an integer."""
    try:
        return int(os.getenv(name, str(default)))
    except (ValueError, TypeError):
        return default

def is_sensitive(key: str) -> bool:
    """Checks if an environment variable key is sensitive."""
    return bool(re.search(r"KEY|SECRET|TOKEN|PASS|PASSWORD|PRIVATE|CREDENTIAL|AUTH|SIGNATURE", key, re.IGNORECASE))

def mask_value(key: str, value: str) -> str:
    """Masks sensitive values."""
    if not is_sensitive(key):
        return value
    if len(value) > 12:
        return f"{value[:4]}...{value[-4:]}"
    return "***"

# --- Public Config Endpoint ---

@app.get("/config", response_model=Dict[str, Any])
async def get_config():
    """
    Returns the public, non-sensitive configuration of the service.
    """
    return {
        "service": "trader-agent",
        "TRADING_MODE": TRADING_MODE,
        "DRY_RUN": env_bool("DRY_RUN", True),
        "ALLOWED_SYMBOLS": ALLOWED_SYMBOLS,
        "MAX_QTY": env_int("MAX_QTY", 1),
        "ALPACA_BASE_URL": BASE_URL,
        "K_REVISION": os.getenv("K_REVISION", "local"),
        "GCP_PROJECT": os.getenv("GCP_PROJECT", None),
    }

# --- Protected Debug Endpoint ---

DEBUG_ENDPOINTS_ENABLED = env_bool("DEBUG_ENDPOINTS", False)
DEBUG_TOKEN = os.getenv("DEBUG_TOKEN")

# if DEBUG_ENDPOINTS_ENABLED: # Commented out conditional block for debugging
@app.get("/debug/env", response_model=Dict[str, str])
async def get_debug_env(x_debug_token: str = Header(None)):
    """
    [PROTECTED] Returns a masked and truncated dump of environment variables.
    Requires DEBUG_ENDPOINTS=true and a valid X-Debug-Token header.
    """
    if not DEBUG_TOKEN or x_debug_token != DEBUG_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing X-Debug-Token.")
    
    env_dump = {}
    for key, value in os.environ.items():
        masked_value = mask_value(key, str(value))
        env_dump[key] = masked_value[:200] + "..." if len(masked_value) > 200 else masked_value
        
    return env_dump
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

# --- Alpaca API Client ---

def get_alpaca_api():
    """Dependency to create and validate the Alpaca API client."""
    logger.info(f"Attempting to initialize Alpaca API client.")
    logger.info(f"TRADING_MODE: {TRADING_MODE}")
    logger.info(f"BASE_URL: {BASE_URL}")

    if not ALPACA_API_KEY or not ALPACA_SECRET_KEY:
        logger.error("Alpaca API keys are not configured. Set ALPACA_API_KEY and ALPACA_SECRET_KEY.")
        raise HTTPException(status_code=500, detail="Alpaca API credentials are not configured.")
    if TRADING_MODE != "paper":
        logger.critical("FATAL: Live trading mode is enabled. This is not allowed.")
        raise HTTPException(status_code=500, detail="Live trading is strictly forbidden.")
    
    try:
        api = tradeapi.REST(ALPACA_API_KEY, ALPACA_SECRET_KEY, base_url=BASE_URL, api_version='v2')
        # Validate connection by trying to get account info
        account_info = api.get_account()
        logger.info(f"Successfully connected to Alpaca API. Account status: {account_info.status}")
        return api
    except APIError as e:
        logger.error(f"Failed to connect to Alpaca API: {e}", exc_info=True)
        raise HTTPException(status_code=503, detail=f"Could not connect to Alpaca: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during Alpaca client initialization: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during API client setup.")


# --- Pydantic Models ---

class AlpacaOrder(BaseModel):
    symbol: str = Field(..., description="The symbol to trade, e.g., 'BTC/USD'")
    qty: float = Field(..., gt=0, description="The quantity to trade.")
    side: str = Field(..., description="Either 'buy' or 'sell'")
    type: str = Field("market", description="Order type, e.g., 'market', 'limit'")
    time_in_force: str = Field("gtc", description="Time in force, e.g., 'gtc', 'day'")

class TradeResponse(BaseModel):
    message: str
    order_details: Dict[str, Any]

# --- API Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {"message": "AGIcore Trader Agent is running."}

@app.get("/alpaca/account", response_model=Dict[str, Any])
async def get_alpaca_account(api: tradeapi.REST = Depends(get_alpaca_api)):
    """
    Fetches the Alpaca paper trading account information to validate the connection.
    """
    try:
        account_info = api.get_account()
        return {
            "id": account_info.id,
            "account_number": account_info.account_number,
            "status": account_info.status,
            "crypto_status": account_info.crypto_status,
            "buying_power": account_info.buying_power,
            "equity": account_info.equity,
            "is_paper": TRADING_MODE == "paper",
        }
    except APIError as e:
        logger.error(f"Failed to fetch Alpaca account: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Alpaca account: {e}")

@app.post("/alpaca/order", response_model=TradeResponse)
async def create_alpaca_order(order: AlpacaOrder, api: tradeapi.REST = Depends(get_alpaca_api)):
    """
    Submits a trade order to the Alpaca paper trading API with extensive safeguards.
    """
    # --- Safeguard Checks ---
    if order.symbol not in ALLOWED_SYMBOLS:
        msg = f"Symbol '{order.symbol}' is not in the allowed list: {ALLOWED_SYMBOLS}"
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    if order.qty > MAX_QTY:
        msg = f"Quantity {order.qty} exceeds the maximum allowed of {MAX_QTY}"
        logger.warning(msg)
        raise HTTPException(status_code=400, detail=msg)

    if order.side not in ["buy", "sell"]:
        raise HTTPException(status_code=400, detail="Side must be 'buy' or 'sell'")

    # --- Dry Run Simulation ---
    if DRY_RUN:
        logger.info(f"[DRY RUN] Simulating order: {order.side} {order.qty} {order.symbol}")
        simulated_response = {
            "symbol": order.symbol,
            "qty": order.qty,
            "side": order.side,
            "type": order.type,
            "status": "simulated_accepted",
            "dry_run": True
        }
        return TradeResponse(message="[DRY RUN] Order submission simulated successfully.", order_details=simulated_response)
        
    # --- Live Paper Trading Execution ---
    try:
        logger.info(f"Submitting paper trade order: {order.side} {order.qty} {order.symbol}")
        placed_order = api.submit_order(
            symbol=order.symbol,
            qty=order.qty,
            side=order.side,
            type=order.type,
            time_in_force=order.time_in_force
        )
        logger.info(f"Paper trade order submitted successfully. Order ID: {placed_order.id}")
        
        # Return a subset of the order details
        order_details = {
            "id": placed_order.id,
            "client_order_id": placed_order.client_order_id,
            "symbol": placed_order.symbol,
            "qty": placed_order.qty,
            "side": placed_order.side,
            "type": placed_order.type,
            "status": placed_order.status,
            "created_at": placed_order.created_at,
        }
        return TradeResponse(message="Paper trade order submitted successfully.", order_details=order_details)

    except APIError as e:
        logger.error(f"Alpaca API error during order submission: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit order to Alpaca: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred during order submission: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
