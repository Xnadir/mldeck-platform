"""
Experiments — tracking experiments with parameters, metrics, and metadata.
"""

import json
import os
import time
import random
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


EXPERIMENTS_FILE = "experiments_log.json"


def _load_experiments() -> list:
    if os.path.exists(EXPERIMENTS_FILE):
        with open(EXPERIMENTS_FILE, "r") as f:
            return json.load(f)
    return []


def _save_experiments(exps: list):
    with open(EXPERIMENTS_FILE, "w") as f:
        json.dump(exps, f, indent=2)


def run_experiment(df: pd.DataFrame, target_col: str, feature_cols: list, model_type: str = "random_forest", params: dict = None) -> dict:
    """Run a ML experiment: split data, train model, evaluate metrics."""
    params = params or {}
    start_time = time.time()

    X = df[feature_cols]
    y = df[target_col]

    # encode categoricals
    X = pd.get_dummies(X, drop_first=True)

    # split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # select model
    if model_type == "gradient_boosting":
        model = GradientBoostingClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", 3),
            learning_rate=params.get("learning_rate", 0.1),
            random_state=42
        )
    elif model_type == "logistic_regression":
        model = LogisticRegression(
            C=params.get("C", 1.0),
            max_iter=params.get("max_iter", 200),
            random_state=42
        )
    else:
        model = RandomForestClassifier(
            n_estimators=params.get("n_estimators", 100),
            max_depth=params.get("max_depth", None),
            min_samples_split=params.get("min_samples_split", 2),
            random_state=42
        )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    elapsed = round(time.time() - start_time, 3)

    # calculate metrics
    avg_method = 'weighted' if len(y.unique()) > 2 else 'binary'
    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
        "precision": round(precision_score(y_test, y_pred, average=avg_method, zero_division=0) * 100, 2),
        "recall": round(recall_score(y_test, y_pred, average=avg_method, zero_division=0) * 100, 2),
        "f1": round(f1_score(y_test, y_pred, average=avg_method, zero_division=0) * 100, 2),
    }

    # feature importances
    importances = {}
    if hasattr(model, 'feature_importances_'):
        for fname, imp in sorted(zip(X.columns, model.feature_importances_), key=lambda x: -x[1])[:10]:
            importances[fname] = round(float(imp) * 100, 2)

    experiment = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{random.randint(100,999)}",
        "timestamp": datetime.now().isoformat(),
        "model_type": model_type,
        "parameters": params,
        "dataset": {
            "rows": len(df),
            "features": feature_cols,
            "target": target_col,
            "train_size": len(X_train),
            "test_size": len(X_test),
        },
        "metrics": metrics,
        "feature_importances": importances,
        "elapsed_seconds": elapsed,
        "status": "completed",
    }

    exps = _load_experiments()
    exps.insert(0, experiment)
    if len(exps) > 50:
        exps = exps[:50]
    _save_experiments(exps)

    return experiment


def get_experiments() -> list:
    return _load_experiments()


def compare_experiments(ids: list) -> list:
    exps = _load_experiments()
    return [e for e in exps if e["id"] in ids]
