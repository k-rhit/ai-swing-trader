import streamlit as st
import pandas as pd

st.title("AI Swing Trader Dashboard")

df = pd.read_csv("https://raw.githubusercontent.com/YOUR_USERNAME/ai-swing-trader/main/data/signals/today_signals.csv")
st.dataframe(df)
