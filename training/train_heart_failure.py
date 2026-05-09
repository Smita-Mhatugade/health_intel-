"""
Train Heart Failure Prediction model from clinical records.
Extracts logic from Heart Failure Prediction/heart_failure.ipynb
Saves: models/heart_failure_lr.pkl (dict with 'model', 'scaler', 'feature_names')
"""
import os
import sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings

warnings.filterwarnings("ignore")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "Heart Failure Prediction", "heart_failure_clinical_records_dataset.csv.xls")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "heart_failure_lr.pkl")


def train():
    print("=" * 60)
    print("Training Heart Failure Prediction Model")
    print("=" * 60)

    # Load data
    print(f"\n[1/5] Loading data from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"  Dataset shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")

    # Features and target
    feature_names = [
        "age", "anaemia", "creatinine_phosphokinase", "diabetes",
        "ejection_fraction", "high_blood_pressure", "platelets",
        "serum_creatinine", "serum_sodium", "sex", "smoking", "time"
    ]
    target = "DEATH_EVENT"

    X = df[feature_names].values
    y = df[target].values

    # Train-test split
    print("\n[2/5] Splitting data (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {X_train.shape[0]} samples")
    print(f"  Test:  {X_test.shape[0]} samples")

    # Scale features
    print("\n[3/5] Scaling features with StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    print("\n[4/5] Training Logistic Regression...")
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n  Test Accuracy: {accuracy:.4f}")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Survived", "Death Event"]))

    # Save model
    print(f"\n[5/5] Saving model to: {MODEL_PATH}")
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_artifact = {
        "model": model,
        "scaler": scaler,
        "feature_names": feature_names,
        "accuracy": accuracy,
        "model_type": "LogisticRegression",
        "target": target,
    }
    joblib.dump(model_artifact, MODEL_PATH)
    print(f"  Model saved successfully!")
    print("=" * 60)

    return model_artifact


if __name__ == "__main__":
    train()
