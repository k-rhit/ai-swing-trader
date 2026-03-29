import pandas as pd
import requests
import os
import ast

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


# -----------------------------------------------------
# Safe CSV loader
# -----------------------------------------------------
def safe_read_csv(path):
    if not os.path.exists(path):
        return None

    if os.path.getsize(path) == 0:
        return pd.DataFrame()

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()

    if content == "" or content.replace("\n", "") == "":
        return pd.DataFrame()

    if "," not in content:
        return pd.DataFrame()

    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


# -----------------------------------------------------
# Notify Logic
# -----------------------------------------------------
def notify():
    path = "data/signals/today_signals.csv"
    df = safe_read_csv(path)

    if df is None:
        send_message("⚠ Signal file missing.")
        return

    if df.empty:
        send_message("ℹ No swing signals today.")
        return

    for _, r in df.iterrows():

        # Convert string "[120, 130]" to list
        try:
            entry_range = ast.literal_eval(r["entry_range"])
        except:
            entry_range = r["entry_range"]

        # Determine trend-type (EMA based)
        trend_basis = "EMA trend filter (EMA20 > EMA50)"

        # Momentum components
        momentum_basis = "RSI + MACD + Volume Z-score (momentum confirmation)"

        # Target basis (ATR-based target)
        target_basis = "ATR-based targeting (TP1 = 2.2 ATR, TP2 = 3.8 ATR)"

        msg = (
f"📈 *Swing Signal Alert*\n"
f"Symbol: {r['symbol']}\n"
f"Final Score: {r['final_score']}\n\n"
f"Entry Range: {entry_range}\n"
f"Stop-Loss: {r['stop_loss']}\n"
f"Target 1: {r.get('target1', 'N/A')}\n"
f"Target 2: {r.get('target2', 'N/A')}\n\n"
f"📊 Basis:\n"
f"- Trend: {trend_basis}\n"
f"- Momentum: {momentum_basis}\n"
f"- Targeting: {target_basis}\n"
        )

        send_message(msg)


if __name__ == "__main__":
    notify()