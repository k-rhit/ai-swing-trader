import pandas as pd
import numpy as np
import glob
import os

RESULTS = []

def simulate_trade(df, entry_low, entry_high, sl, target, lookahead=20):
    """
    Candle-by-candle simulation:
    - Looks ahead X candles to see if entry gets filled.
    - After entry: checks which hits first → SL or Target.
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
        return None  # No fill → no trade

    # 2) After entry, check SL/Target
    for j in range(entry_index + 1, min(entry_index + 1 + lookahead, len(df))):
        low = df.iloc[j]["Low"]
        high = df.iloc[j]["High"]

        if low <= sl:
            return entry_price, sl, -1
        if high >= target:
            return entry_price, target, 1

    # 3) If neither hit, exit at last candle close
    exit_price = df.iloc[min(entry_index + lookahead, len(df)-1)]["Close"]
    pnl = 1 if exit_price > entry_price else -1
    return entry_price, exit_price, pnl


def backtest_stock(df, symbol):
    df.reset_index(drop=True, inplace=True)

    equity = 1_00_000
    risk_per_trade = 0.02
    trades = []

    for i in range(60, len(df)):
        row = df.iloc[i]

        # Replicate same feature logic
        up = row["ema20"] > row["ema50"]
        vol = row["vol_z"] > 0

        # Model-based probability (same as signal generator)
        # Placeholder: rule-based simulation, OR plug prediction.
        prob = 0.5
        score = 0.6*prob + 0.3*up + 0.1*vol

        if score < 0.70:
            continue

        entry_low  = row["Close"] * 0.995
        entry_high = row["Close"] * 1.005
        sl = row["Close"] - 1.5 * row["atr"]
        tgt = row["Close"] + 3 * row["atr"]

        trade_result = simulate_trade(df.iloc[i:i+30], entry_low, entry_high, sl, tgt)

        if trade_result is None:
            continue

        entry_price, exit_price, pnl_flag = trade_result

        capital_risk = equity * risk_per_trade
        qty = max(int(capital_risk / abs(entry_price - sl)), 1)

        pnl = (exit_price - entry_price) * qty
        equity += pnl

        trades.append({
            "symbol": symbol,
            "entry_idx": i,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "qty": qty,
            "pnl": pnl,
            "equity_after": equity,
            "result": "WIN" if pnl_flag > 0 else "LOSS"
        })

    return trades, equity


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
    print("Win Rate:", round((df_trades['result'] == 'WIN').mean()*100, 2), "%")
    print("Total Trades:", len(df_trades))

    return df_trades


if __name__ == "__main__":
    backtest_all()