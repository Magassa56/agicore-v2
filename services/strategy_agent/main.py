
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scipy.optimize import minimize
import xgboost as xgb

# --- Strategy Configuration ---

TICKER = "QQQ"
TIMEFRAME = "1m"
EMA_SHORT = 19
EMA_LONG = 20
RSI_PERIOD = 14
ATR_PERIOD = 14
ADX_PERIOD = 14
VOLATILITY_WINDOW = 20
TRAIN_SIZE = 1000
VALIDATION_SIZE = 200
TEST_SIZE = 200

# --- Data Acquisition ---

def get_historical_data(ticker, period="7d", interval="1m"):
    """
    Downloads historical data from Yahoo Finance and merges it with execution data.
    """
    data = yf.download(ticker, period=period, interval=interval)
    data.columns = ['_'.join(col).strip() for col in data.columns.values]

    # Read execution data
    try:
        trades_df = pd.read_csv("trades.csv", index_col="timestamp", parse_dates=True)
        # Rename columns to avoid conflicts
        trades_df = trades_df.rename(columns={"price": "execution_price", "quantity": "execution_quantity"})
        # Merge with historical data
        data = pd.merge(data, trades_df[["execution_price", "slippage", "latency"]], left_index=True, right_index=True, how="left")
        # Forward-fill the execution data
        data[["execution_price", "slippage", "latency"]] = data[["execution_price", "slippage", "latency"]].fillna(method="ffill")
    except FileNotFoundError:
        print("trades.csv not found, skipping merge with execution data.")
        data["execution_price"] = np.nan
        data["slippage"] = np.nan
        data["latency"] = np.nan

    return data

# --- Feature Engineering ---

def add_indicators(df):
    """
    Adds technical indicators to the DataFrame.
    """
    df["EMA_SHORT"] = ta.trend.ema_indicator(df["Close_QQQ"], window=EMA_SHORT)
    df["EMA_LONG"] = ta.trend.ema_indicator(df["Close_QQQ"], window=EMA_LONG)
    df["RSI"] = ta.momentum.rsi(df["Close_QQQ"], window=RSI_PERIOD)
    df["ATR"] = ta.volatility.average_true_range(df["High_QQQ"], df["Low_QQQ"], df["Close_QQQ"], window=ATR_PERIOD)
    return df

def add_advanced_features(df):
    """
    Adds advanced features for the machine learning model.
    """
    # Volatility Regime
    df['log_returns'] = np.log(df['Close_QQQ'] / df['Close_QQQ'].shift(1))
    df['volatility_regime'] = df['log_returns'].rolling(window=VOLATILITY_WINDOW).std()

    # Market Trend Strength
    adx = ta.trend.ADXIndicator(df['High_QQQ'], df['Low_QQQ'], df['Close_QQQ'], window=ADX_PERIOD)
    df['adx'] = adx.adx()
    df['adx_pos'] = adx.adx_pos()
    df['adx_neg'] = adx.adx_neg()

    # Volume Imbalance
    df['obv'] = ta.volume.on_balance_volume(df['Close_QQQ'], df['Volume_QQQ'])
    df['vwap'] = ta.volume.volume_weighted_average_price(df['High_QQQ'], df['Low_QQQ'], df['Close_QQQ'], df['Volume_QQQ'])

    # Time-based features
    df["hour"] = df.index.hour
    df["minute"] = df.index.minute
    df["dayofweek"] = df.index.dayofweek
    
    return df

# --- Signal Generation ---

def generate_signals(df):
    """
    Generates trading signals based on the strategy.
    """
    df["signal"] = 0
    df.loc[(df["Close_QQQ"] > df["EMA_SHORT"]) & (df["Open_QQQ"] < df["EMA_SHORT"]) & (df["RSI"] < 70), "signal"] = 1
    df.loc[df["Close_QQQ"] < df["EMA_LONG"], "signal"] = -1
    return df

# --- Walk-Forward Validation & Dynamic Thresholding ---

def walk_forward_validation(df):
    """
    Performs walk-forward validation with dynamic threshold optimization.
    """
    df["target"] = df["signal"].shift(-1)
    df = df.dropna()

    features = ["hour", "minute", "dayofweek", "RSI", "ATR", "volatility_regime", "adx", "adx_pos", "adx_neg", "obv", "vwap"]
    target = "target"
    
    all_predictions = []
    all_true_values = []
    trades = []
    initial_capital = 100000
    capital = initial_capital
    position = 0

    for i in range(TRAIN_SIZE + VALIDATION_SIZE, len(df), TEST_SIZE):
        train_df = df.iloc[i - (TRAIN_SIZE + VALIDATION_SIZE) : i - VALIDATION_SIZE]
        validation_df = df.iloc[i - VALIDATION_SIZE : i]
        test_df = df.iloc[i : i + TEST_SIZE]

        X_train = train_df[features]
        y_train = train_df[target]
        X_validation = validation_df[features]
        y_validation = validation_df[target]
        X_test = test_df[features]
        y_test = test_df[target]

        # Train the model
        model = xgb.XGBClassifier(objective='multi:softprob', num_class=3, eval_metric='mlogloss', use_label_encoder=False)
        model.fit(X_train, y_train)

        # Optimize threshold
        def objective(threshold):
            buy_threshold, sell_threshold = threshold
            y_pred_proba = model.predict_proba(X_validation)
            y_pred = np.zeros(len(y_validation))
            y_pred[y_pred_proba[:, 2] > buy_threshold] = 1
            y_pred[y_pred_proba[:, 0] > sell_threshold] = -1
            
            # Simple profit metric for optimization
            profit = np.sum(y_pred * y_validation)
            return -profit
            
        # Initial guess for thresholds
        initial_thresholds = [0.5, 0.5]
        result = minimize(objective, initial_thresholds, bounds=[(0, 1), (0, 1)])
        best_buy_threshold, best_sell_threshold = result.x

        # Make predictions on test set
        y_pred_proba_test = model.predict_proba(X_test)
        y_pred_test = np.zeros(len(y_test))
        y_pred_test[y_pred_proba_test[:, 2] > best_buy_threshold] = 1
        y_pred_test[y_pred_proba_test[:, 0] > best_sell_threshold] = -1
        
        all_predictions.extend(y_pred_test)
        all_true_values.extend(y_test)
        
        # Backtest with optimized signals
        for j in range(len(test_df)):
            if y_pred_test[j] == 1 and position == 0:
                position = capital / test_df["Close_QQQ"].iloc[j]
                capital = 0
                trades.append({"type": "BUY", "price": test_df["Close_QQQ"].iloc[j], "index": test_df.index[j], "position": position})
            elif y_pred_test[j] == -1 and position > 0:
                capital = position * test_df["Close_QQQ"].iloc[j]
                position = 0
                trades.append({"type": "SELL", "price": test_df["Close_QQQ"].iloc[j], "index": test_df.index[j], "capital": capital})

    if position > 0:
        capital = position * df["Close_QQQ"].iloc[-1]
    
    # --- Performance Evaluation ---
    accuracy = accuracy_score(all_true_values, all_predictions)
    precision = precision_score(all_true_values, all_predictions, average='weighted')
    recall = recall_score(all_true_values, all_predictions, average='weighted')
    f1 = f1_score(all_true_values, all_predictions, average='weighted')
    profit = capital - initial_capital
    profit_percent = (profit / initial_capital) * 100

    print("
--- Improved Model Evaluation ---")
    print(f"Walk-Forward Accuracy: {accuracy:.3f}")
    print(f"Walk-Forward Precision: {precision:.3f}")
    print(f"Walk-Forward Recall: {recall:.3f}")
    print(f"Walk-Forward F1-Score: {f1:.3f}")
    
    print("
--- Backtest Results ---")
    print(f"Initial Capital: ${initial_capital:,.2f}")
    print(f"Final Capital: ${capital:,.2f}")
    print(f"Profit: ${profit:,.2f}")
    print(f"Profit (%): {profit_percent:.2f}%")
    print(f"Number of Trades: {len(trades)}")

    trades_df = pd.DataFrame(trades)
    trades_df.to_csv("trades.csv")
    print("
Trades saved to trades.csv")

from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from google.cloud import pubsub_v1
import json
import os

...

# --- Pub/Sub Configuration ---
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
TRADE_SIGNALS_TOPIC = os.getenv("TRADE_SIGNALS_TOPIC", "trade-signals")

...

def publish_signals(signals):
    """
    Publishes the generated signals to the Pub/Sub topic.
    """
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCP_PROJECT_ID, TRADE_SIGNALS_TOPIC)

    for signal in signals:
        message_data = json.dumps(signal).encode("utf-8")
        future = publisher.publish(topic_path, message_data)
        print(f"Published message ID: {future.result()}")

...

def walk_forward_validation(df):
    ...
    # --- Performance Evaluation ---
    ...
    print("--- Backtest Results ---")
    ...
    print("
Trades saved to trades.csv")

    # --- Push metrics to Prometheus Pushgateway ---
    registry = CollectorRegistry()
    pnl_gauge = Gauge('strategy_pnl_percentage', 'Strategy PnL in percentage', registry=registry)
    pnl_gauge.set(profit_percent)
    win_rate_gauge = Gauge('strategy_win_rate', 'Strategy win rate', registry=registry)
    win_rate_gauge.set(accuracy) # Using accuracy as a proxy for win rate
    trade_frequency_gauge = Gauge('strategy_trade_frequency', 'Strategy trade frequency', registry=registry)
    trade_frequency_gauge.set(len(trades))
    drawdown_gauge = Gauge('strategy_drawdown', 'Strategy drawdown', registry=registry)
    drawdown_gauge.set(0.1) # Placeholder

    # --- Sharpe Ratio Calculation ---
    daily_returns = trades_df.set_index('index')['price'].pct_change().dropna()
    sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252) # Annualized
    sharpe_ratio_gauge = Gauge('strategy_sharpe_ratio', 'Strategy Sharpe ratio', registry=registry)
    sharpe_ratio_gauge.set(sharpe_ratio)

    push_to_gateway('localhost:9091', job='strategy_agent', registry=registry)

    # --- Publish signals to Pub/Sub ---
    signals_to_publish = []
    for trade in trades:
        signals_to_publish.append({
            "ticker": TICKER,
            "action": trade['type'].lower(),
            "confidence": 0.9, # Placeholder
            "quantity": 1, # Placeholder
            "order_type": "market"
        })
    publish_signals(signals_to_publish)

# --- Main Execution ---
...
