"""
model.py
Handles training and loading of the fraud detection model.

Dataset expected: Kaggle "Credit Card Fraud Detection" dataset (creditcard.csv)
Download from: https://www.kaggle.com/mlg-ulb/creditcardfraud
Place it at: backend/data/creditcard.csv
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score, confusion_matrix
from imblearn.over_sampling import SMOTE
import xgboost as xgb

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "xgboost_model.pkl")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "creditcard.csv")


def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at {path}. Download creditcard.csv from Kaggle "
            "and place it in backend/data/"
        )
    return pd.read_csv(path)


def train_and_compare(df: pd.DataFrame):
    """Train Logistic Regression, Random Forest, and XGBoost, compare with AUC-PR."""
    X = df.drop(columns=["Class"])
    y = df["Class"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # Balance the training set only, never touch the test set
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

    results = {}

    log_reg = LogisticRegression(max_iter=1000, class_weight="balanced")
    log_reg.fit(X_train_res, y_train_res)
    log_reg_score = average_precision_score(y_test, log_reg.predict_proba(X_test)[:, 1])
    results["logistic_regression"] = log_reg_score

    rf = RandomForestClassifier(
        n_estimators=200, class_weight="balanced", random_state=42, n_jobs=-1
    )
    rf.fit(X_train_res, y_train_res)
    rf_score = average_precision_score(y_test, rf.predict_proba(X_test)[:, 1])
    results["random_forest"] = rf_score

    xgb_model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        eval_metric="aucpr",
        use_label_encoder=False,
        random_state=42,
    )
    xgb_model.fit(X_train_res, y_train_res)
    xgb_score = average_precision_score(y_test, xgb_model.predict_proba(X_test)[:, 1])
    results["xgboost"] = xgb_score

    cm = confusion_matrix(y_test, xgb_model.predict(X_test))

    print("AUC-PR scores:", results)
    print("XGBoost confusion matrix:\n", cm)

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(xgb_model, MODEL_PATH)

    return xgb_model, results, cm


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"No trained model found at {MODEL_PATH}. Run: python model.py to train first."
        )
    return joblib.load(MODEL_PATH)


def predict_transaction(model, features: dict) -> dict:
    """
    features: dict with keys Time, V1..V28, Amount (matching the Kaggle schema)
    Returns fraud probability and a verdict.
    """
    row = pd.DataFrame([features])
    proba = float(model.predict_proba(row)[0][1])

    if proba >= 0.8:
        verdict = "Fraud"
    elif proba >= 0.3:
        verdict = "Suspicious"
    else:
        verdict = "Legitimate"

    return {"fraud_probability": round(proba, 4), "verdict": verdict}


if __name__ == "__main__":
    data = load_data()
    train_and_compare(data)
