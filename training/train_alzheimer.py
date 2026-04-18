"""
Train Alzheimer Detection model from clinical/cognitive/neuroimaging data.
Extracts logic from Alzheimer Detection/Alzheimer.ipynb
Saves: models/alzheimer_rf.pkl (dict with 'model', 'scaler', 'label_encoder', 'feature_names')
"""
import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import warnings

warnings.filterwarnings("ignore")

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "Alzheimer Detection", "CSI_7_MAL_2324_CW_resit_data.xlsx")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "alzheimer_rf.pkl")


def train():
    print("=" * 60)
    print("Training Alzheimer Detection Model")
    print("=" * 60)

    # Load data from Excel sheets
    print(f"\n[1/7] Loading data from: {DATA_PATH}")
    diagnosis_df = pd.read_excel(DATA_PATH, sheet_name="Diagnosis target")
    cognitive_scores_df = pd.read_excel(DATA_PATH, sheet_name="Cognitive score")
    data_df = pd.read_excel(DATA_PATH, sheet_name="Data")

    print(f"  Diagnosis shape: {diagnosis_df.shape}")
    print(f"  Cognitive scores shape: {cognitive_scores_df.shape}")
    print(f"  Data shape: {data_df.shape}")

    # Handle missing values
    print("\n[2/7] Handling missing values...")
    diagnosis_df.dropna(inplace=True)
    cognitive_scores_df.dropna(inplace=True)
    data_df.dropna(inplace=True)

    # Merge dataframes on RID
    print("\n[3/7] Merging dataframes on RID...")
    merged_df = diagnosis_df.merge(cognitive_scores_df, on="RID")
    merged_df = merged_df.merge(data_df, on="RID")
    print(f"  Merged shape: {merged_df.shape}")

    # Prepare features and target
    print("\n[4/7] Preparing features...")
    target_col = "Diagnosis"
    
    # Encode target
    le = LabelEncoder()
    y = le.fit_transform(merged_df[target_col])
    class_names = list(le.classes_)
    print(f"  Classes: {class_names}")

    # Drop non-feature columns
    cols_to_drop = [target_col, "RID"]
    test_data_cols = [c for c in merged_df.columns if "Test_data" in c]
    cols_to_drop.extend(test_data_cols)
    
    feature_df = merged_df.drop(columns=cols_to_drop, errors="ignore")

    # Encode categorical columns
    categorical_cols = feature_df.select_dtypes(include=["object"]).columns.tolist()
    label_encoders = {}
    for col in categorical_cols:
        col_le = LabelEncoder()
        feature_df[col] = col_le.fit_transform(feature_df[col].astype(str))
        label_encoders[col] = col_le

    feature_names = list(feature_df.columns)
    X = feature_df.values

    # Train-test split
    print(f"\n[5/7] Splitting data (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"  Train: {X_train.shape[0]} samples")
    print(f"  Test:  {X_test.shape[0]} samples")

    # Scale features
    print("\n[6/7] Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    print("\n[7/7] Training Random Forest Classifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n  Test Accuracy: {accuracy:.4f}")
    print(f"\n  Classification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names))

    # Save model
    print(f"\n  Saving model to: {MODEL_PATH}")
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_artifact = {
        "model": model,
        "scaler": scaler,
        "label_encoder": le,
        "label_encoders_categorical": label_encoders,
        "feature_names": feature_names,
        "class_names": class_names,
        "accuracy": accuracy,
        "model_type": "RandomForestClassifier",
    }
    joblib.dump(model_artifact, MODEL_PATH)
    print(f"  Model saved successfully!")
    print("=" * 60)

    return model_artifact


if __name__ == "__main__":
    train()
