"""Alzheimer Detection Analyzer."""
import numpy as np
import pandas as pd
import joblib
from typing import Any, Dict
from backend.services.analyzers.base import BaseAnalyzer
from backend.models.schemas import SeverityLevel
from backend import config


class AlzheimerAnalyzer(BaseAnalyzer):
    """Analyzes clinical/cognitive/neuroimaging data for Alzheimer classification."""

    def __init__(self):
        self._model = None
        self._scaler = None
        self._label_encoder = None
        self._label_encoders_cat = None
        self._feature_names = None
        self._class_names = None
        self._loaded = False
        self._load_model()

    def _load_model(self):
        try:
            artifact = joblib.load(config.ALZHEIMER_MODEL_PATH)
            self._model = artifact["model"]
            self._scaler = artifact["scaler"]
            self._label_encoder = artifact["label_encoder"]
            self._label_encoders_cat = artifact.get("label_encoders_categorical", {})
            self._feature_names = artifact["feature_names"]
            self._class_names = artifact["class_names"]
            self._loaded = True
            print("[AlzheimerAnalyzer] Model loaded successfully.")
        except Exception as e:
            print(f"[AlzheimerAnalyzer] Failed to load model: {e}")
            self._loaded = False

    def is_available(self) -> bool:
        return self._loaded

    def preprocess(self, data: Any) -> np.ndarray:
        """
        Accepts a pandas DataFrame (from uploaded Excel).
        Uses the first row for prediction.
        """
        if isinstance(data, pd.DataFrame):
            df = data.copy()
        else:
            raise ValueError("AlzheimerAnalyzer expects a pandas DataFrame")

        # Keep only feature columns that exist
        available_features = [f for f in self._feature_names if f in df.columns]
        missing = [f for f in self._feature_names if f not in df.columns]

        if missing:
            # Fill missing columns with 0
            for col in missing:
                df[col] = 0

        df = df[self._feature_names]

        # Encode categorical columns
        for col, le in self._label_encoders_cat.items():
            if col in df.columns:
                try:
                    df[col] = le.transform(df[col].astype(str))
                except ValueError:
                    df[col] = 0  # Unknown category → 0

        values = df.iloc[0:1].values.astype(float)
        return self._scaler.transform(values)

    def predict(self, processed_input: np.ndarray) -> Dict[str, Any]:
        prediction_idx = self._model.predict(processed_input)[0]
        probabilities = self._model.predict_proba(processed_input)[0]
        predicted_class = self._label_encoder.inverse_transform([prediction_idx])[0]

        class_probs = {}
        for i, cls in enumerate(self._class_names):
            class_probs[cls] = round(float(probabilities[i]) * 100, 2)

        return {
            "disease_category": "alzheimer",
            "prediction": predicted_class,
            "prediction_label": self._get_label(predicted_class),
            "confidence": round(float(max(probabilities)) * 100, 2),
            "details": {
                "class_probabilities": class_probs,
                "classes": self._class_names,
            },
        }

    def _get_label(self, prediction: str) -> str:
        labels = {
            "CN": "Cognitive Normal",
            "AD": "Alzheimer's Disease",
            "LMCI": "Late Mild Cognitive Impairment",
        }
        return labels.get(prediction, prediction)

    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        pred = prediction["prediction"]
        severity_map = {
            "CN": SeverityLevel(level="Normal", label="Cognitive Normal", color="#22c55e",
                                confidence=prediction["confidence"]),
            "LMCI": SeverityLevel(level="Moderate", label="Late Mild Cognitive Impairment",
                                  color="#f59e0b", confidence=prediction["confidence"]),
            "AD": SeverityLevel(level="Severe", label="Alzheimer's Disease", color="#ef4444",
                                confidence=prediction["confidence"]),
        }
        return severity_map.get(pred, SeverityLevel(
            level="Unknown", label="Unknown", color="#6b7280", confidence=prediction["confidence"]
        ))

    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        pred_label = prediction["prediction_label"]
        confidence = prediction["confidence"]
        class_probs = prediction["details"]["class_probabilities"]

        summary = f"**Alzheimer's Disease Assessment**\n\n"
        summary += f"Based on the clinical, cognitive, and neuroimaging data provided, "
        summary += f"the AI model classifies the patient as: **{pred_label}** "
        summary += f"(Confidence: {confidence}%)\n\n"
        summary += "**Class Probabilities:**\n"
        for cls, prob in class_probs.items():
            summary += f"- {self._get_label(cls)}: {prob}%\n"
        summary += "\n"

        if prediction["prediction"] == "AD":
            summary += ("⚠️ The analysis suggests indicators consistent with **Alzheimer's Disease**. "
                        "It is strongly recommended to consult a neurologist or geriatric specialist "
                        "for comprehensive evaluation, including additional cognitive testing and "
                        "brain imaging studies.")
        elif prediction["prediction"] == "LMCI":
            summary += ("The analysis suggests indicators of **Late Mild Cognitive Impairment**, "
                        "which may represent an early or transitional stage. Regular monitoring "
                        "and consultation with a neurologist is recommended to track progression.")
        else:
            summary += ("The analysis suggests **normal cognitive function** based on the provided data. "
                        "Continue regular health check-ups and cognitive health maintenance.")

        return summary
