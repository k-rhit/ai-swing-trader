import os

print("\n===== STEP 1: Processing Raw Data =====")
os.system("data_download.py")
os.system("python features.py")

print("\n===== STEP 2: Training Model =====")
os.system("python train_model.py")

print("\n===== STEP 3: Generating Signals =====")
os.system("python generated_signals.py")

print("\n===== STEP 4: Running Backtest =====")
os.system("python backtest_engine.py")

print("\n===== PIPELINE FINISHED =====")