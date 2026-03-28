import vectorbt as vbt
import pandas as pd

def run_backtest(symbol):
    df = pd.read_csv(f"data/processed/{symbol}.csv")
    entries = df["Close"] < df["ema20"]
    exits = df["Close"] > df["ema50"]

    pf = vbt.Portfolio.from_signals(df["Close"], entries, exits)
    print(pf.stats())

if __name__ == "__main__":
    run_backtest("RELIANCE.NS")