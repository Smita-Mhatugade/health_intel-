"""Symptom-Based Disease Prediction Analyzer."""
import numpy as np
import pandas as pd
import joblib
from typing import Any, Dict, List
from backend.services.analyzers.base import BaseAnalyzer
from backend.models.schemas import SeverityLevel
from backend import config


class SymptomAnalyzer(BaseAnalyzer):
    """Predicts disease from symptom checklist using ensemble of pre-trained models."""

    def __init__(self):
        self._models = {}
        self._symptom_columns = []
        self._disease_labels = {}  # numeric -> disease name mapping
        self._loaded = False
        self._load_models()

    def _load_models(self):
        try:
            model_files = {
                "Random Forest": "RandomForest_model.pkl",
                "XGBoost": "Xgboost_model.pkl",
            }
            optional_models = {
                "CatBoost": "catboost_model.pkl",
                "LightGBM": "LGBM_model.pkl",
                "Naive Bayes": "naive_bayes.pkl",
            }

            for name, fname in {**model_files, **optional_models}.items():
                path = config.SYMPTOM_MODELS_DIR / fname
                if path.exists():
                    try:
                        self._models[name] = joblib.load(path)
                        print(f"[SymptomAnalyzer] Loaded {name}")
                    except Exception as e:
                        print(f"[SymptomAnalyzer] Could not load {name}: {e}")

            # Load symptom columns and disease label mapping from training data
            if config.SYMPTOM_TRAINING_CSV.exists():
                training_df = pd.read_csv(config.SYMPTOM_TRAINING_CSV)
                self._symptom_columns = [
                    col for col in training_df.columns
                    if col.lower() != "prognosis"
                ]
                # Build label mapping: the prognosis column may have disease names
                if "prognosis" in training_df.columns:
                    unique_diseases = sorted(training_df["prognosis"].unique())
                    # Check if values are already strings (disease names)
                    if all(isinstance(d, str) for d in unique_diseases):
                        self._disease_labels = {str(i): d for i, d in enumerate(unique_diseases)}
                        # Also map disease name to itself for models that return strings
                        for d in unique_diseases:
                            self._disease_labels[d] = d
                    else:
                        self._disease_labels = {str(d): str(d) for d in unique_diseases}

                print(f"[SymptomAnalyzer] {len(self._symptom_columns)} symptoms loaded.")
                if self._disease_labels:
                    num_labels = len([k for k in self._disease_labels.keys() if k.isdigit()])
                    print(f"[SymptomAnalyzer] {num_labels} disease labels mapped.")

            self._loaded = len(self._models) > 0 and len(self._symptom_columns) > 0
            if self._loaded:
                print(f"[SymptomAnalyzer] Ready with {len(self._models)} models.")
        except Exception as e:
            print(f"[SymptomAnalyzer] Failed to initialize: {e}")
            self._loaded = False

    def is_available(self) -> bool:
        return self._loaded

    def get_symptom_list(self) -> List[str]:
        """Return available symptom names for the UI."""
        return [s.replace("_", " ").title() for s in self._symptom_columns]

    def get_raw_symptom_list(self) -> List[str]:
        return list(self._symptom_columns)

    def _decode_prediction(self, raw_pred) -> str:
        """Decode a raw model prediction to a disease name."""
        # Handle CatBoost array-style output like "[0]" or array([0])
        pred_str = str(raw_pred).strip("[] ")
        # Try to look up in disease labels
        if pred_str in self._disease_labels:
            return self._disease_labels[pred_str]
        return pred_str.replace("_", " ").title() if pred_str else "Unknown"

    def preprocess(self, data: Dict[str, Any]) -> np.ndarray:
        symptoms = data.get("symptoms", [])
        normalized = [s.lower().replace(" ", "_") for s in symptoms]
        feature_vector = np.zeros(len(self._symptom_columns))
        for i, col in enumerate(self._symptom_columns):
            if col in normalized:
                feature_vector[i] = 1
        return feature_vector.reshape(1, -1)

    def predict(self, processed_input: np.ndarray) -> Dict[str, Any]:
        raw_predictions = {}
        decoded_predictions = {}

        for name, model in self._models.items():
            try:
                pred = model.predict(processed_input)[0]
                raw_pred_str = str(pred).strip("[] ")
                decoded = self._decode_prediction(pred)
                raw_predictions[name] = raw_pred_str
                decoded_predictions[name] = decoded
            except Exception as e:
                print(f"[SymptomAnalyzer] {name} prediction failed: {e}")

        if not decoded_predictions:
            return {
                "disease_category": "symptom_prediction",
                "prediction": "unknown",
                "prediction_label": "Unable to predict",
                "confidence": 0.0,
                "details": {},
            }

        # Majority voting on decoded (human-readable) predictions
        from collections import Counter
        vote_counts = Counter(decoded_predictions.values())
        most_common = vote_counts.most_common(1)[0]
        consensus_disease = most_common[0]
        consensus_count = most_common[1]
        total_models = len(decoded_predictions)
        confidence = round((consensus_count / total_models) * 100, 2)

        return {
            "disease_category": "symptom_prediction",
            "prediction": consensus_disease,
            "prediction_label": consensus_disease,
            "confidence": confidence,
            "details": {
                "model_predictions": decoded_predictions,
                "consensus_count": consensus_count,
                "total_models": total_models,
                "vote_distribution": dict(vote_counts),
            },
        }

    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        confidence = prediction.get("confidence", 0)
        if confidence >= 80:
            return SeverityLevel(level="Moderate", label="Predicted with High Confidence",
                                color="#f59e0b", confidence=confidence)
        elif confidence >= 50:
            return SeverityLevel(level="Mild", label="Predicted with Moderate Confidence",
                                color="#3b82f6", confidence=confidence)
        else:
            return SeverityLevel(level="Mild", label="Low Confidence Prediction",
                                color="#6b7280", confidence=confidence)

    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        disease = prediction["prediction_label"]
        confidence = prediction["confidence"]
        details = prediction.get("details", {})
        model_preds = details.get("model_predictions", {})

        summary = f"**Symptom-Based Disease Prediction**\n\n"
        summary += f"Based on the symptoms provided, the AI ensemble predicts: **{disease}** "
        summary += f"(Confidence: {confidence}%)\n\n"

        if model_preds:
            summary += "**Individual Model Predictions:**\n"
            for model_name, pred in model_preds.items():
                match = "[AGREE]" if pred == prediction["prediction"] else "[DIFFER]"
                summary += f"- {model_name}: {pred} {match}\n"
            summary += "\n"

        summary += (f"The prediction is based on consensus from {details.get('total_models', 0)} "
                    f"ML models, with {details.get('consensus_count', 0)} models agreeing on the "
                    f"diagnosis.\n\n")
        summary += ("Please consult a general practitioner or appropriate specialist for proper "
                    "clinical evaluation and confirmation of this prediction.")

        return summary
