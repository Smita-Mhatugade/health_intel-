"""
Copy pre-trained symptom prediction models and data to the project models/ directory.
"""
import os
import shutil

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DIR = os.path.join(BASE_DIR, "Disease-Prediction-Based-on-Symptoms-main")
MODEL_DIR = os.path.join(BASE_DIR, "models", "symptom_prediction")
DATA_DIR = os.path.join(BASE_DIR, "data", "symptom_data")


def copy_models():
    print("=" * 60)
    print("Copying Symptom Prediction Models")
    print("=" * 60)

    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    # Copy model files
    model_files = [
        "RandomForest_model.pkl",
        "Xgboost_model.pkl",
        "catboost_model.pkl",
        "LGBM_model.pkl",
        "naive_bayes.pkl",
    ]

    for fname in model_files:
        src = os.path.join(SOURCE_DIR, fname)
        dst = os.path.join(MODEL_DIR, fname)
        if os.path.exists(src):
            print(f"  Copying {fname}...")
            shutil.copy2(src, dst)
        else:
            print(f"  WARNING: {fname} not found at {src}")

    # Copy data files
    data_files = ["training.csv", "testing.csv"]
    for fname in data_files:
        src = os.path.join(SOURCE_DIR, fname)
        dst = os.path.join(DATA_DIR, fname)
        if os.path.exists(src):
            print(f"  Copying {fname}...")
            shutil.copy2(src, dst)
        else:
            print(f"  WARNING: {fname} not found at {src}")

    print("\n  Done!")
    print("=" * 60)


if __name__ == "__main__":
    copy_models()
