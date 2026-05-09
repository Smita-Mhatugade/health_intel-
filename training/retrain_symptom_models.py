"""
Retrain symptom prediction models to ensure compatibility with current scikit-learn.
"""
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from catboost import CatBoostClassifier
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models", "symptom_prediction")
DATA_DIR = os.path.join(BASE_DIR, "data", "symptom_data")
TRAIN_CSV = os.path.join(DATA_DIR, "training.csv")

def train_and_save():
    print("=" * 60)
    print("Retraining Symptom Prediction Models")
    print("=" * 60)

    if not os.path.exists(TRAIN_CSV):
        print(f"Error: Training data not found at {TRAIN_CSV}")
        return

    os.makedirs(MODEL_DIR, exist_ok=True)

    # Load data
    print("Loading data...")
    df = pd.read_csv(TRAIN_CSV)
    
    # Preprocess
    X = df.drop(columns=['prognosis'])
    y = df['prognosis']

    # Label encode the target because XGBoost requires numeric targets
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    # We don't save the label encoder because the original analyzer doesn't load one.
    # Wait, the original analyzer uses string outputs directly?
    # Yes, let's look at the original analyzer code:
    # m.predict(processed_input)[0] ... and disease_labels.get(p, p).
    # If XGBoost returns numeric, it will map to numbers. We should train RandomForest 
    # and CatBoost on strings, but XGBoost might need numeric. Let's see if the original 
    # used strings for XGBoost. XGBoost < 2.0 allowed strings sometimes, or the user 
    # might have used label encoder. Let's train them all without label encoder and see 
    # if XGBoost complains. If it does, we use LabelEncoder. But wait, XGBoost requires 
    # numeric. If the original analyzer didn't load an encoder, maybe it expects strings?
    # Actually, in scikit-learn pipeline or original implementation, they probably used 
    # strings and maybe an older XGBoost. Let's just train RandomForest for now to be safe,
    # as the analyzer only strictly needs one model to work.
    # Actually, let's train all three, but for XGBoost, if we must encode, we can encode 
    # and save.
    
    print("Training RandomForest...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y) # RF accepts strings
    joblib.dump(rf, os.path.join(MODEL_DIR, "RandomForest_model.pkl"))

    print("Training XGBoost...")
    # XGBClassifier requires numeric labels in recent versions
    xgb = XGBClassifier(random_state=42)
    xgb.fit(X, y_encoded)
    # If we save this, the analyzer will get numeric predictions. 
    # The analyzer does: `p = str(m.predict(processed_input)[0]).strip("[] ")`
    # and `disease_labels.get(p, p)`.
    # `disease_labels` is loaded from the CSV unique values. 
    # `disease_labels = {str(i): d for i, d in enumerate(unique)}`
    # Ah! The analyzer creates a mapping from index to string based on `sorted(df["prognosis"].unique())`!
    # So if XGBoost returns `0`, it gets mapped correctly. If RF returns `"Fungal infection"`, it falls back to `d`.
    # So both string and numeric are supported!
    joblib.dump(xgb, os.path.join(MODEL_DIR, "Xgboost_model.pkl"))

    print("Training CatBoost...")
    cb = CatBoostClassifier(iterations=100, verbose=False, random_state=42)
    cb.fit(X, y_encoded) # Also using encoded to be safe
    joblib.dump(cb, os.path.join(MODEL_DIR, "catboost_model.pkl"))

    print("Done! Models saved to", MODEL_DIR)

if __name__ == "__main__":
    train_and_save()
