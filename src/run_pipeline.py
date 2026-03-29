import os

print("\n===== STEP 1: Processing Raw Data =====")
os.system("python src/utils.py")
os.system("python src/data_download.py")
os.system("python src/sma_strategy.py")
os.system("python src/features.py")

print("\n===== STEP 2: Training Model =====")
os.system("python src/train_model.py")

print("\n===== STEP 3: Generating Signals =====")
os.system("python src/generate_signals.py")

print("\n===== STEP 4: Running Backtest =====")
os.system("python backtest/backtest_engine.py")

os.system("python src/notify.py")

print("\n===== PIPELINE FINISHED =====")