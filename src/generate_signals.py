import pandas as pd
import numpy as np
import xgboost as xgb
from utils import load_tickers

# Load model
model = xgb.XGBClassifier()
model.load_model("data/models/model.json")

SIGNALS = []

# CONFIG
PROB_THRESHOLD = 0.65
FINAL_SCORE_THRESHOLD = 0.72
MIN_ATR_PCT = 0.008     # 0.8% intraday ATR minimum (avoid low volatility stocks)
MAX_GAP_PCT = 0.015     # avoid high opening gaps


def generate_signal_for_stock(df, symbol):
    if len(df) < 60:
        return

    row = df.iloc[-1]

    # Required features — if missing, skip
    required = ["rsi","macd","atr","ema20","ema50","vol_z"]
    if any(f not in df.columns for f in required):
        return

    # Volatility filter — skip illiquid low ATR stocks
    atr_pct = row["atr"] / row["Close"]
    if atr_pct < MIN_ATR_PCT:
        return

    # Trend direction filter
    ema20 = row["ema20"]
    ema50 = row["ema50"]
    uptrend = 1 if ema20 > ema50 else 0

    # Volume confirmation
    volume_ok = 1 if row["vol_z"] > 0 else 0

    # Predict probability
    X = row[required].values.reshape(1, -1)
    prob = float(model.predict_proba(X)[0][1])

    if prob < PROB_THRESHOLD:
        return

    # Optional: ADX trend-strength (fallback if not present)
    if "adx" in df.columns:
        adx = row["adx"]
        trend_strength = min(adx / 25, 1.0)  # normalize 0-1
    else:
        # fallback based on EMA gradient
        trend_strength = min(abs((ema20 - ema50) / ema50) * 50, 1.0)

    # Final score (weighted)
    final_score = (
        0.55 * prob +
        0.25 * trend_strength +
        0.15 * uptrend +
        0.05 * volume_ok
    )

    if final_score < FINAL_SCORE_THRESHOLD:
        return

    # Opening gap check (avoid choppy days)
    if len(df) >= 2:
        prev_close = df.iloc[-2]["Close"]
        gap_pct = abs(row["Close"] - prev_close) / prev_close
        if gap_pct > MAX_GAP_PCT:
            return

    # Entry range
    close_price = row["Close"]
    entry_low = close_price * 0.996
    entry_high = close_price * 1.004

    # SL & target
    sl = close_price - 1.6 * row["atr"]
    target1 = close_price + 2.2 * row["atr"]
    target2 = close_price + 3.8 * row["atr"]

    SIGNALS.append({
        "symbol": symbol,
        "prob": round(prob, 4),
        "trend_strength": round(trend_strength, 3),
        "final_score": round(final_score, 4),
        "entry_range": [round(entry_low, 2), round(entry_high, 2)],
        "stop_loss": round(sl, 2),
        "target1": round(target1, 2),
        "target2": round(target2, 2),
    })


def generate_all_signals():
    SIGNALS.clear()
    tickers = load_tickers()

    for symbol in tickers:
        file = f"data/processed/{symbol}.csv"
        df = pd.read_csv(file)
        generate_signal_for_stock(df, symbol)

    out = pd.DataFrame(SIGNALS)
    out.to_csv("data/signals/today_signals.csv", index=False)

    print(f"Signals generated: {len(SIGNALS)} stocks.")


if __name__ == "__main__":
    generate_all_signals()