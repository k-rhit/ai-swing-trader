import pandas as pd
import numpy as np
import glob
import os


RESULTS = []


# ---------------------------------------------------------------------------------
# TRADE SIMULATOR (Shared for Both Strategies)
# ---------------------------------------------------------------------------------
def simulate_trade(df, entry_low, entry_high, sl, target, lookahead=20):
    """
    Candle-by-candle simulation for 20 candles:
    - checks if entry gets filled
    - after entry: checks which hits first (SL or Target)
    """

    # 1) Find entry candle
    for i in range(len(df)):
        low = df.iloc[i]["Low"]
        high = df.iloc[i]["High"]

        if low <= entry_high and high >= entry_low:
            entry_price = np.clip(df.iloc[i]["Open"], entry_low, entry_high)
            entry_index = i
            break
    else:
        return None

    # 2) After entry → check SL and target
    for j in range(entry_index + 1, min(entry_index + 1 + lookahead, len(df))):
        low = df.iloc[j]["Low"]
        high = df.iloc[j]["High"]

        if low <= sl:
            return entry_price, sl, -1

        if high >= target:
            return entry_price, target, 1

    # 3) Neither hit → exit on final close
    exit_price = df.iloc[min(entry_index + lookahead, len(df)-1)]["Close"]
    pnl_flag = 1 if exit_price > entry_price else -1

    return entry_price, exit_price, pnl_flag



# ---------------------------------------------------------------------------------
# STRATEGY B: SMA V40 Swing Strategy (Pure Rule-Based)
# ---------------------------------------------------------------------------------
def check_sma_buy(row):
    return (
        row["sma200"] > row["sma50"] > row["sma20"] and
        row["Close"] == row["Low"] and
        row["Close"] < row["Open"]   # red candle
    )

def check_sma_sell_condition(row):
    return (
        row["sma200"] < row["sma50"] < row["sma20"] and
        row["Close"] == row["High"] and
        row["Close"] > row["Open"]   # green candle
    )



# ---------------------------------------------------------------------------------
# STRATEGY A: ML + EMA Trend System
# ---------------------------------------------------------------------------------
def ml_strategy_signal(row, prob=0.5):
    up = row["ema20"] > row["ema50"]
    vol = row["vol_z"] > 0
    score = 0.6*prob + 0.3*up + 0.1*vol
    return score > 0.70



# ---------------------------------------------------------------------------------
# BACKTEST for ONE STOCK integrating both strategies
# ---------------------------------------------------------------------------------
def backtest_stock(df, symbol):
    df.reset_index(drop=True, inplace=True)

    equity = 100_000
    risk_per_trade = 0.02
    trades = []

    # Ensure SMA columns exist
    if "sma20" not in df.columns:
        df["sma20"] = df["Close"].rolling(20).mean()
        df["sma50"] = df["Close"].rolling(50).mean()
        df["sma200"] = df["Close"].rolling(200).mean()

    for i in range(200, len(df)):

        row = df.iloc[i]

        # -------------------------------------------------------
        # STRATEGY A: ML Trend Strategy Trigger
        # -------------------------------------------------------
        if ml_strategy_signal(row):
            entry_low = row["Close"] * 0.995
            entry_high = row["Close"] * 1.005
            sl = row["Close"] - 1.5 * row["atr"]
            tgt = row["Close"] + 3 * row["atr"]

            trade_result = simulate_trade(df.iloc[i:i+30], entry_low, entry_high, sl, tgt)

            if trade_result:
                entry, exit, flag = trade_result
                capital_risk = equity * risk_per_trade
                qty = max(int(capital_risk / abs(entry - sl)), 1)
                pnl = (exit - entry) * qty
                equity += pnl

                trades.append({
                    "symbol": symbol,
                    "strategy": "ML_EMA",
                    "entry_idx": i,
                    "entry_price": entry,
                    "exit_price": exit,
                    "qty": qty,
                    "pnl": pnl,
                    "equity_after": equity,
                    "result": "WIN" if flag > 0 else "LOSS"
                })

        # -------------------------------------------------------
        # STRATEGY B: SMA V40 System Trigger
        # -------------------------------------------------------
        if check_sma_buy(row):
            entry_low = entry_high = row["Close"]
            sl = row["Low"] * 0.995
            tgt = row["High"] * 1.02

            trade_result = simulate_trade(df.iloc[i:i+25], entry_low, entry_high, sl, tgt)

            if trade_result:
                entry, exit, flag = trade_result
                capital_risk = equity * risk_per_trade
                qty = max(int(capital_risk / abs(entry - sl)), 1)
                pnl = (exit - entry) * qty
                equity += pnl

                trades.append({
                    "symbol": symbol,
                    "strategy": "SMA_V40",
                    "entry_idx": i,
                    "entry_price": entry,
                    "exit_price": exit,
                    "qty": qty,
                    "pnl": pnl,
                    "equity_after": equity,
                    "result": "WIN" if flag > 0 else "LOSS"
                })

    return trades, equity



# ---------------------------------------------------------------------------------
# BACKTEST ALL STOCKS
# ---------------------------------------------------------------------------------
def backtest_all():
    os.makedirs("data/backtest", exist_ok=True)

    all_trades = []
    final_equity = 0
    symbols = 0

    for file in glob.glob("data/processed/*.csv"):
        df = pd.read_csv(file)
        symbol = file.split("/")[-1].replace(".csv","")

        trades, eq = backtest_stock(df, symbol)
        all_trades.extend(trades)
        final_equity += eq
        symbols += 1

        print(f"Backtested {symbol}: Final Equity = {eq}")

    df_trades = pd.DataFrame(all_trades)
    df_trades.to_csv("data/backtest/all_trades.csv", index=False)

    print("\n===== BACKTEST SUMMARY =====")
    print("Total Stocks Tested:", symbols)
    print("Portfolio Final Equity:", final_equity)

    # Prevent crash if no trades
    if df_trades.empty:
        print("No trades generated across all stocks.")
        return df_trades

    # Safe result check
    if "result" in df_trades.columns:
        win_rate = round((df_trades["result"] == "WIN").mean() * 100, 2)
        print("Win Rate:", win_rate, "%")
    else:
        print("Win Rate: N/A (no result column)")

    print("Total Trades:", len(df_trades))

    if "strategy" in df_trades.columns:
        print("ML Strategy Trades:", sum(df_trades["strategy"] == "ML_EMA"))
        print("SMA Strategy Trades:", sum(df_trades["strategy"] == "SMA_V40"))
    else:
        print("Strategy Breakdown Not Available")

    return df_trades



if __name__ == "__main__":
    backtest_all()