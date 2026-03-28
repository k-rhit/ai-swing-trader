import pandas as pd
import xgboost as xgb
import glob
import numpy as np
import json

model = xgb.XGBClassifier()
model.load_model("data/models/model.json")

SIGNALS = []

def generate_signal_for_stock(df, symbol):
    row = df.iloc[-1]  

    X = row[["rsi","macd","atr","ema20","ema50","vol_z"]].values.reshape(1, -1)
    prob = model.predict_proba(X)[0][1]

    uptrend = row["ema20"] > row["ema50"]
    volume_ok = row["vol_z"] > 0

    final_score = 0.6*prob + 0.3*uptrend + 0.1*volume_ok

    if final_score > 0.70:
        entry_low = row["Close"] * 0.995
        entry_high = row["Close"] * 1.005
        sl = row["Close"] - 1.5 * row["atr"]
        target = row["Close"] + 3 * row["atr"]

        SIGNALS.append({
            "symbol": symbol,
            "final_score": float(final_score),
            "entry_range": [round(entry_low,2), round(entry_high,2)],
            "stop_loss": round(sl,2),
            "target": round(target,2)
        })

def generate_all_signals():
    for file in glob.glob("data/processed/*.csv"):
        df = pd.read_csv(file)
        generate_signal_for_stock(df, file.split("/")[-1].replace(".csv",""))
    pd.DataFrame(SIGNALS).to_csv("data/signals/today_signals.csv", index=False)

if __name__ == "__main__":
    generate_all_signals()