import json

def load_tickers():
    with open("tickers.json") as f:
        data = json.load(f)
    return data["stocks"]