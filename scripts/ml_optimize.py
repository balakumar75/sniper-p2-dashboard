#!/usr/bin/env python
"""
ML Optimize: 
 - Loads trade_history.json
 - Featurizes each trade at entry (RSI, ADX, ATR, vol, pop)
 - Trains a RandomForestClassifier to predict win (1) vs loss (0)
 - Serializes the trained model and threshold into model.pkl
"""

import json, pathlib, joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score

import utils

# 1. Load history
hist = json.loads(pathlib.Path("trade_history.json").read_text())
records = []
for run in hist:
    for t in run["open_trades"] if "open_trades" in run else run.get("trades", []):
        # only closed trades have exit_date & pnl
        if t.get("status") in ("Target Hit","SL Hit") and t.get("exit_date"):
            records.append(t)

df = pd.DataFrame(records)
if df.empty:
    print("No closed trades to train on.")
    exit(0)

# 2. Feature engineering at entry: re-fetch indicators
features = []
labels   = []
for _, row in df.iterrows():
    sym    = row["symbol"]
    entry  = row["entry"]
    target = row["target"]
    sl     = row["sl"]
    # compute features at entry
    rsi = utils.fetch_rsi(sym,14)
    adx = utils.fetch_adx(sym,14)
    atr = utils.fetch_atr(sym,14)
    vol = utils.fetch_ohlc(sym,30)["volume"].iloc[-1] if utils.fetch_ohlc(sym,30) is not None else 0
    pop = utils.hist_pop(sym, (target-entry)/entry*100, (entry-sl)/entry*100)
    features.append([rsi, adx, atr, vol, pop])
    # label = 1 if profit, 0 if SL
    labels.append(1 if row["status"]=="Target Hit" else 0)

X = np.array(features)
y = np.array(labels)

# 3. Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, random_state=42)

# 4. Grid search for best RF hyperparams
param_grid = {
    "n_estimators": [50,100],
    "max_depth":    [3,5,None],
    "min_samples_leaf": [1,3,5]
}
grid = GridSearchCV(RandomForestClassifier(random_state=42), param_grid,
                    cv=3, scoring="accuracy", n_jobs=-1)
grid.fit(X_train, y_train)

best = grid.best_estimator_
print("Best params:", grid.best_params_)

# 5. Evaluate
y_pred = best.predict(X_test)
print("Test accuracy:", accuracy_score(y_test, y_pred))

# 6. Serialize model + decision threshold (default 0.5)
model_artifact = {
    "model": best,
    "threshold": 0.5
}
joblib.dump(model_artifact, "model.pkl")
print("☑️  model.pkl written")
