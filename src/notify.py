import pandas as pd
import requests
import os

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def notify():
    df = pd.read_csv("data/signals/today_signals.csv")
    if df.empty:
        send_message("No swing signals today.")
    else:
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