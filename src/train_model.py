import pandas as pd
import xgboost as xgb
import glob, numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def prepare_training_data():
    dfs = []
    for file in glob.glob("data/processed/*.csv"):
        df = pd.read_csv(file)
        df["target"] = (df["Close"].shift(-5) / df["Close"] > 1.02).astype(int)
        df.dropna(inplace=True)
        dfs.append(df)
    return pd.concat(dfs)

def train_model():
    df = prepare_training_data()
    X = df[["rsi","macd","atr","ema20","ema50","vol_z"]]
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = xgb.XGBClassifier(n_estimators=200, max_depth=4, learning_rate=0.1)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    print("Accuracy:", accuracy_score(y_test, preds))

    model.save_model("data/models/model.json")

if __name__ == "__main__":
    train_model()