import pandas as pd
import ta
import glob
import os
from utils import load_tickers

def add_features(df):
    df["rsi"] = ta.momentum.rsi(df["Close"], window=14)
    df["macd"] = ta.trend.macd_diff(df["Close"])
    df["atr"] = ta.volatility.average_true_range(df["High"], df["Low"], df["Close"])
    df["ema20"] = ta.trend.ema_indicator(df["Close"], window=20)
    df["ema50"] = ta.trend.ema_indicator(df["Close"], window=50)

    df["vol_z"] = (df["Volume"] - df["Volume"].rolling(20).mean()) / df["Volume"].rolling(20).std()

    df.dropna(inplace=True)
    return df


def process_all():
    os.makedirs("data/processed", exist_ok=True)
    tickers = load_tickers()

    for symbol in tickers:
        file = f"data/raw/{symbol}.csv"
        if not os.path.exists(file):
            print("Missing raw file for:", symbol)
            continue

        df = pd.read_csv(file)

        numeric_cols = ["Open", "High", "Low", "Close", "Volume"]
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors="coerce")
        df.dropna(subset=numeric_cols, inplace=True)

        df = add_features(df)

        out_path = f"data/processed/{symbol}.csv"
        df.to_csv(out_path, index=False)
        print("Processed:", out_path)


if __name__ == "__main__":
    process_all()