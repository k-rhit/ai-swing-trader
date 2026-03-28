import pandas as pd
import ta
import glob

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
    for file in glob.glob("data/raw/*.csv"):
        df = pd.read_csv(file)
        df = add_features(df)
        df.to_csv("data/processed/" + file.split("/")[-1])

if __name__ == "__main__":
    process_all()