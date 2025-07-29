#!/usr/bin/env python
"""
ML Optimize: 
 - Loads trade_history.json
 - Featurizes each CLOSED trade at entry (RSI, ADX, ATR, vol, pop)
 - Trains a RandomForestClassifier to predict win (1) vs loss (0)
 - Serializes the best model + threshold into model.pkl
"""

import sys, pathlib

# ── Ensure repo root is on the import path ─────────────────────────────────
# so that "import utils" and other top‑level modules resolve
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import json
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score

import utils

# 1) Load full history
hist_file = ROOT / "trade_history.json"
hist      = json.loads(hist_file.read_text()) if hist_file.exists() else []
records   = []

# 2) Extract only CLOSED trades with exit_date & pnl
for run in hist:
    for t in run.get("open_trades", []):
        if t.get("status") in ("Target Hit", "SL Hit") and t.get("exit_date"):
            records.append(t)

df = pd.DataFrame(records)
if df.empty:
    print("❌ No closed trades to train on – aborting.")
    exit(0)

# 3) Build feature matrix at ENTRY
X, y = [], []
for _, row in df.iterrows():
    sym   = row["symbol"]
    entry = row["entry"]
    tgt   = row["target"]
    sl    = row["sl"]

    # compute indicators
    rsi = utils.fetch_rsi(sym, period=14)
    adx = utils.fetch_adx(sym, period=14)
    atr = utils.fetch_atr(sym, period=14)
    vol = int(utils.fetch_ohlc(sym, 30)["volume"].iloc[-1])
    pop = utils.hist_pop(sym,
                        (tgt - entry) / entry * 100,
                        (entry - sl)  / entry * 100)

    X.append([rsi, adx, atr, vol, pop])
    y.append(1 if row["status"] == "Target Hit" else 0)

X = np.array(X)
y = np.array(y)

# 4) Train/test split & grid‐search
Xtr, Xte, ytr, yte = train_test_split(X, y, stratify=y, random_state=42)
param_grid = {
    "n_estimators":     [50, 100],
    "max_depth":        [3, 5, None],
    "min_samples_leaf": [1, 3, 5]
}
grid = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid, cv=3, scoring="accuracy", n_jobs=-1
)
grid.fit(Xtr, ytr)

best = grid.best_estimator_
print("✅ Best params:", grid.best_params_)

# 5) Evaluate
y_pred = best.predict(Xte)
print("✅ Test accuracy:", accuracy_score(yte, y_pred))

# 6) Serialize
artifact = {"model": best, "threshold": 0.5}
joblib.dump(artifact, ROOT / "model.pkl")
print("☑️  Wrote model.pkl")
