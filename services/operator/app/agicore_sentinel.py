import os
import json
import time
import logging
import sys
import signal
import requests
from datetime import datetime

try:
    import alpaca_trade_api as tradeapi
except ImportError:
    logging.error("Alpaca Trade API not installed. Please install it using 'pip install alpaca-trade-api'")
    sys.exit(1)

# Ensure dotenv is installed and loaded
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logging.warning("python-dotenv not installed. Environment variables must be set manually.")

# --- Configuration ---
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_SECRET_KEY = os.getenv("APCA_API_SECRET_KEY")
APCA_API_BASE_URL = os.getenv("APCA_API_BASE_URL")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

STATE_FILE = "sentinel_state.json"
LOG_FILE = "agicore_log.txt"
MONITOR_INTERVAL_SECONDS = 60
PNL_ALERT_THRESHOLD = 0.02 # 2% loss

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(LOG_FILE),
                        logging.StreamHandler(sys.stdout)
                    ])

def log_event(message, level=logging.INFO):
    """Logs an event to both file and console."""
    if level == logging.ERROR:
        logging.error(message)
    elif level == logging.WARNING:
        logging.warning(message)
    else:
        logging.info(message)

# --- Telegram Sender ---
def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log_event("Telegram credentials not set. Skipping Telegram notification.", level=logging.WARNING)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        log_event(f"Telegram message sent: {message}")
    except requests.exceptions.RequestException as e:
        log_event(f"Failed to send Telegram message: {e}", level=logging.ERROR)

# --- State Management ---
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "last_account_status": None,
        "last_equity": 0.0,
        "last_cash": 0.0,
        "active_positions": {}, # symbol: {qty, avg_entry_price}
        "pending_orders": {}, # id: {symbol, side, qty}
        "last_checked_time": None
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=4)

# --- Alpaca API Client ---
api = None
def initialize_alpaca_api():
    global api
    if not APCA_API_KEY_ID or not APCA_API_SECRET_KEY or not APCA_API_BASE_URL:
        log_event("Alpaca API credentials (APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL) are not set in environment variables.", level=logging.ERROR)
        send_telegram_message("AGICORE SENTINEL: ERROR - Alpaca API credentials missing. Exiting.")
        sys.exit(1)
    try:
        api = tradeapi.REST(APCA_API_KEY_ID, APCA_API_SECRET_KEY, APCA_API_BASE_URL, api_version='v2')
        api.get_account() # Test connection
        log_event("Alpaca API connection: OK")
        return True
    except Exception as e:
        log_event(f"Alpaca API connection failed: {e}", level=logging.ERROR)
        send_telegram_message(f"AGICORE SENTINEL: ERROR - Alpaca API connection failed: {e}")
        return False

# --- Monitoring Functions ---
def check_account(current_state):
    global api
    if api is None:
        if not initialize_alpaca_api():
            return "Connection failed." # Indicate connection failure
    
    try:
        account = api.get_account()
        
        status = account.status
        equity = float(account.equity)
        cash = float(account.cash)

        if current_state["last_account_status"] != status:
            message = f"Account status changed from {current_state['last_account_status']} to {status}."
            log_event(message)
            send_telegram_message(f"AGICORE SENTINEL: Account Status Change - {status}")
            current_state["last_account_status"] = status
        
        if equity != current_state["last_equity"]:
            log_event(f"Account equity changed: ${current_state['last_equity']:.2f} -> ${equity:.2f}")
            current_state["last_equity"] = equity
        
        if cash != current_state["last_cash"]:
            log_event(f"Account cash changed: ${current_state['last_cash']:.2f} -> ${cash:.2f}")
            current_state["last_cash"] = cash

        # Check for significant loss
        if current_state["last_equity"] > 0 and equity < current_state["last_equity"] * (1 - PNL_ALERT_THRESHOLD):
            loss_percentage = ((current_state["last_equity"] - equity) / current_state["last_equity"]) * 100
            message = f"Significant account loss detected: Equity dropped by {loss_percentage:.2f}% to ${equity:.2f}"
            log_event(message, level=logging.WARNING)
            send_telegram_message(f"AGICORE SENTINEL: ALERT - Significant account loss: {loss_percentage:.2f}%")

        if status != 'ACTIVE':
            message = f"Account is not ACTIVE: Current status is {status}."
            log_event(message, level=logging.WARNING)
            send_telegram_message(f"AGICORE SENTINEL: Account is not ACTIVE ({status}). Trading may be restricted.")

        return f"Connexion : OK\nCompte actif : {'OUI' if status == 'ACTIVE' else 'NON'} (Status: {status})\nEquity: ${equity:.2f}, Cash: ${cash:.2f}"

    except Exception as e:
        log_event(f"Error checking account: {e}", level=logging.ERROR)
        send_telegram_message(f"AGICORE SENTINEL: ERROR - Account check failed: {e}")
        return "Connexion : FAILED\nCompte actif : UNKNOWN"

def monitor_positions(current_state):
    global api
    if api is None:
        if not initialize_alpaca_api():
            return # Skip if no connection
            
    try:
        current_positions = {p.symbol: {"qty": float(p.qty), "avg_entry_price": float(p.avg_entry_price), "unrealized_pnl": float(p.unrealized_pl)} for p in api.list_positions()}
        
        # Detect new and updated positions
        for symbol, data in current_positions.items():
            if symbol not in current_state["active_positions"]:
                message = f"New position opened: {data['qty']} shares of {symbol} at ${data['avg_entry_price']:.2f}"
                log_event(message)
                send_telegram_message(f"AGICORE SENTINEL: New Position - {data['qty']} {symbol} @ ${data['avg_entry_price']:.2f}")
            elif (current_state["active_positions"][symbol]["qty"] != data["qty"] or
                  current_state["active_positions"][symbol]["avg_entry_price"] != data["avg_entry_price"]):
                message = f"Position updated for {symbol}: Qty {current_state['active_positions'][symbol]['qty']}->{data['qty']}, Avg Price {current_state['active_positions'][symbol]['avg_entry_price']:.2f}->{data['avg_entry_price']:.2f}"
                log_event(message)
                send_telegram_message(f"AGICORE SENTINEL: Position Update - {symbol} Qty: {data['qty']}")
            
            # PnL monitoring for active positions
            if abs(data["unrealized_pnl"] / (data["qty"] * data["avg_entry_price"])) > PNL_ALERT_THRESHOLD and data["unrealized_pnl"] < 0:
                loss_percentage = (abs(data["unrealized_pnl"]) / (data["qty"] * data["avg_entry_price"])) * 100
                message = f"Position {symbol} unrealized loss exceeded {PNL_ALERT_THRESHOLD*100:.0f}%: {loss_percentage:.2f}%"
                log_event(message, level=logging.WARNING)
                send_telegram_message(f"AGICORE SENTINEL: ALERT - {symbol} unrealized loss: {loss_percentage:.2f}%")
                
        # Detect closed positions
        for symbol in current_state["active_positions"]:
            if symbol not in current_positions:
                message = f"Position closed for {symbol}."
                log_event(message)
                send_telegram_message(f"AGICORE SENTINEL: Position Closed - {symbol}")
        
        current_state["active_positions"] = current_positions

    except Exception as e:
        log_event(f"Error monitoring positions: {e}", level=logging.ERROR)
        send_telegram_message(f"AGICORE SENTINEL: ERROR - Position monitoring failed: {e}")

def monitor_orders(current_state):
    global api
    if api is None:
        if not initialize_alpaca_api():
            return # Skip if no connection
            
    try:
        # Get recent orders (last day, for simplicity)
        # Alpaca API provides limited historical order data for free tier, so focusing on recent status
        orders = api.list_orders(status='all', after=datetime.now().strftime('%Y-%m-%d'))
        
        current_pending_orders = {}
        for order in orders:
            if order.status in ['new', 'partially_filled', 'filled']:
                current_pending_orders[order.id] = {
                    "symbol": order.symbol,
                    "side": order.side,
                    "qty": float(order.qty),
                    "status": order.status,
                    "filled_qty": float(order.filled_qty) if order.filled_qty else 0,
                    "filled_avg_price": float(order.filled_avg_price) if order.filled_avg_price else 0
                }
        
        # Check for executed orders or status changes
        for order_id, order_data in current_pending_orders.items():
            if order_id not in current_state["pending_orders"]:
                message = f"New order detected: {order_data['side']} {order_data['qty']} {order_data['symbol']} (ID: {order_id})"
                log_event(message)
                send_telegram_message(f"AGICORE SENTINEL: New Order - {order_data['side']} {order_data['qty']} {order_data['symbol']}")
            elif current_state["pending_orders"][order_id]["status"] != order_data["status"]:
                message = f"Order {order_id} status changed from {current_state['pending_orders'][order_id]['status']} to {order_data['status']} for {order_data['symbol']}."
                log_event(message)
                send_telegram_message(f"AGICORE SENTINEL: Order Update - {order_data['symbol']} changed to {order_data['status']}")
                
                if order_data["status"] == 'filled':
                    message = f"Order filled: {order_data['filled_qty']} shares of {order_data['symbol']} at avg ${order_data['filled_avg_price']:.2f} (ID: {order_id})"
                    log_event(message)
                    send_telegram_message(f"AGICORE SENTINEL: Order Filled - {order_data['filled_qty']} {order_data['symbol']} @ ${order_data['filled_avg_price']:.2f}")

        # Check for rejected/canceled orders
        for order_id, order_data in current_state["pending_orders"].items():
            if order_id not in current_pending_orders and order_data["status"] not in ['filled', 'canceled', 'rejected']:
                 # Need to re-fetch the specific order to get its final status if not in current_pending_orders
                try:
                    final_order_status = api.get_order(order_id).status
                    if final_order_status in ['rejected', 'canceled']:
                        message = f"Order {order_id} for {order_data['symbol']} was {final_order_status}."
                        log_event(message, level=logging.WARNING)
                        send_telegram_message(f"AGICORE SENTINEL: ALERT - Order {order_data['symbol']} {final_order_status.upper()}")
                except Exception as e:
                    log_event(f"Could not retrieve final status for order {order_id}: {e}", level=logging.ERROR)

        current_state["pending_orders"] = current_pending_orders

    except Exception as e:
        log_event(f"Error monitoring orders: {e}", level=logging.ERROR)
        send_telegram_message(f"AGICORE SENTINEL: ERROR - Order monitoring failed: {e}")

# --- Graceful Shutdown ---
running = True
def signal_handler(signum, frame):
    global running
    log_event("CTRL+C detected. Shutting down gracefully...")
    send_telegram_message("AGICORE SENTINEL: Shutting down.")
    running = False

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# --- Main Loop ---
def main_loop():
    global api
    last_event_message = "None"

    print("==============================")
    print("AGICORE SENTINEL ACTIVE")
    print("==============================")

    current_state = load_state()
    if not initialize_alpaca_api():
        last_event_message = "Initial Alpaca API connection failed."
        print(f"Connexion : FAILED\nCompte actif : UNKNOWN\nSurveillance : INACTIVE\nDernier événement :\nHeure : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{last_event_message}")
        # Keep trying to initialize inside the loop
    
    while running:
        try:
            account_status_str = check_account(current_state)
            monitor_positions(current_state)
            monitor_orders(current_state)
            
            current_state["last_checked_time"] = datetime.now().isoformat()
            save_state(current_state)

            last_event_message = f"Monitoring successful at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Console output
            os.system('cls' if os.name == 'nt' else 'clear') # Clear console for updated output
            print("==============================")
            print("AGICORE SENTINEL ACTIVE")
            print("==============================")
            print(account_status_str)
            print("Surveillance : ACTIVE")
            print("Dernier événement :")
            print(f"Heure : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(last_event_message)

        except Exception as e:
            last_event_message = f"An unexpected error occurred: {e}"
            log_event(last_event_message, level=logging.ERROR)
            send_telegram_message(f"AGICORE SENTINEL: CRITICAL ERROR - {e}")
            # Console output for error state
            os.system('cls' if os.name == 'nt' else 'clear')
            print("==============================")
            print("AGICORE SENTINEL ACTIVE (ERROR)")
            print("==============================")
            print(f"Connexion : FAILED\nCompte actif : UNKNOWN\nSurveillance : ACTIVE WITH ERRORS\nDernier événement :\nHeure : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n{last_event_message}")

        log_event(f"Sleeping for {MONITOR_INTERVAL_SECONDS} seconds...")
        time.sleep(MONITOR_INTERVAL_SECONDS)

    log_event("AGICORE SENTINEL has stopped.")

if __name__ == "__main__":
    main_loop()