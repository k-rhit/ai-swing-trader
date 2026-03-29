import pandas as pd

def check_sma_v40_conditions(df):
    """
    df: processed dataframe with OHLC data
    Returns: dictionary with buy/sell signals OR None
    """

    row = df.iloc[-1]

    sma20 = row["sma20"]
    sma50 = row["sma50"]
    sma200 = row["sma200"]

    # ---------------- BUY CONDITIONS ----------------
    buy_cond_1 = sma200 > sma50 > sma20
    buy_cond_2 = row["Close"] == row["Low"]         # closing at lowest point
    buy_cond_3 = (
        (sma200 > sma50 > sma20) and
        buy_cond_2
    )

    # ---------------- SELL CONDITIONS ----------------
    sell_cond_1 = sma200 < sma50 < sma20
    sell_cond_2 = row["Close"] == row["High"]

    sell_cond_3 = (
        (sma200 < sma50 < sma20) and
        sell_cond_2
    )

    # Output format
    if buy_cond_3:
        return {
            "type": "BUY",
            "entry_low": round(row["Close"] * 0.995, 2),
            "entry_high": round(row["Close"] * 1.005, 2),
            "stop_loss": None,
            "target": None
        }

    if sell_cond_3:
        return {
            "type": "SELL",
            "entry_low": None,
            "entry_high": None,
            "stop_loss": None,
            "target": None
        }

    return None