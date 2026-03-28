import pandas as pd
import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def safe_read_csv(path):
    # 1. File does not exist
    if not os.path.exists(path):
        return None

    # 2. File is empty in bytes
    if os.path.getsize(path) == 0:
        return pd.DataFrame()

    # 3. Read raw text first
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read().strip()

    # 4. Only whitespace/newlines → treat as empty
    if content == "" or content.replace("\n", "") == "":
        return pd.DataFrame()

    # 5. CSV must contain at least one comma or header-like structure
    if "," not in content:
        return pd.DataFrame()

    # 6. Now safely load CSV
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame()


def notify():
    path = "data/signals/today_signals.csv"

    df = safe_read_csv(path)

    # df is None → file missing
    if df is None:
        send_message("Signal file missing.")
        return

    # df exists but empty or corrupted
    if df.empty:
        send_message("No swing signals today.")
        return

    # Otherwise process signals
    for _, r in df.iterrows():
        msg = f"""
Swing Signal:
{r['symbol']}
Score: {r['final_score']}
Entry Range: {r['entry_range']}
SL: {r['stop_loss']}
Target: {r['target']}
"""
        send_message(msg)


if __name__ == "__main__":
    notify()
