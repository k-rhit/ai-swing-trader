import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from utils import load_tickers
import os

def download_data():
    tickers = load_tickers()  # now reading from tickers.json
    end = datetime.today()
    start = end - timedelta(days=900)

    os.makedirs("data/raw", exist_ok=True)

    for symbol in tickers:
        print(f"Downloading → {symbol}")
        df = yf.download(symbol, start=start, end=end)

        if df.empty:
            print(f"Warning: No data for {symbol}")
            continue

        df.to_csv(f"data/raw/{symbol}.csv")

    print("All data downloaded successfully.")

if __name__ == "__main__":
    download_data()