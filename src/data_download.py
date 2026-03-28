import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from utils import load_tickers

# STOCK_LIST = ["RELIANCE.NS","ICICIBANK.NS","HDFCBANK.NS","INFY.NS","TCS.NS"] 

def download_data():
    tickers = load_tickers()
    end = datetime.today()
    start = end - timedelta(days=900)

    for symbol in STOCK_LIST:
        df = yf.download(symbol, start=start, end=end)
        df.to_csv(f"data/raw/{symbol}.csv")
    print("Data downloaded successfully.")

if __name__ == "__main__":
    download_data()
