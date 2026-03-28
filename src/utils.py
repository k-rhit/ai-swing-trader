import json

def load_tickers():
    with open("config/tickers.json", "r") as f:
        data = json.load(f)
    return data.get("tickers", [])