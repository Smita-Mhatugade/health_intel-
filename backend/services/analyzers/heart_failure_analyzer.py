"""Heart Failure Prediction Analyzer."""
import numpy as np
import joblib
from typing import Any, Dict
from backend.services.analyzers.base import BaseAnalyzer
from backend.models.schemas import SeverityLevel
from backend import config


class HeartFailureAnalyzer(BaseAnalyzer):
    """Analyzes clinical data to predict heart failure mortality risk."""

    def __init__(self):
        self._model = None
        self._scaler = None
        self._feature_names = None
        self._loaded = False
        self._load_model()

    def _load_model(self):
        try:
            artifact = joblib.load(config.HEART_FAILURE_MODEL_PATH)
            self._model = artifact["model"]
            self._scaler = artifact["scaler"]
            self._feature_names = artifact["feature_names"]
            self._loaded = True
            print("[HeartFailureAnalyzer] Model loaded successfully.")
        except Exception as e:
            print(f"[HeartFailureAnalyzer] Failed to load model: {e}")
            self._loaded = False

    def is_available(self) -> bool:
        return self._loaded

    def preprocess(self, data: Dict[str, Any]) -> np.ndarray:
        values = [float(data[f]) for f in self._feature_names]
        arr = np.array(values).reshape(1, -1)
        return self._scaler.transform(arr)

    def predict(self, processed_input: np.ndarray) -> Dict[str, Any]:
        prediction = self._model.predict(processed_input)[0]
        probabilities = self._model.predict_proba(processed_input)[0]
        death_prob = float(probabilities[1])

        return {
            "disease_category": "heart_failure",
            "prediction": "high_risk" if prediction == 1 else "low_risk",
            "prediction_label": "High Risk of Heart Failure Mortality" if prediction == 1
                else "Low Risk of Heart Failure Mortality",
            "confidence": round(max(probabilities) * 100, 2),
            "death_probability": round(death_prob * 100, 2),
            "details": {
                "survival_probability": round((1 - death_prob) * 100, 2),
                "death_probability": round(death_prob * 100, 2),
                "raw_prediction": int(prediction),
            },
        }

    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        death_prob = prediction["death_probability"] / 100.0
        if death_prob < 0.3:
            return SeverityLevel(level="Normal", label="Low Risk", color="#22c55e", confidence=prediction["confidence"])
        elif death_prob < 0.6:
            return SeverityLevel(level="Moderate", label="Moderate Risk", color="#f59e0b", confidence=prediction["confidence"])
        else:
            return SeverityLevel(level="Severe", label="High Risk", color="#ef4444", confidence=prediction["confidence"])

    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        death_prob = prediction["death_probability"]
        survival_prob = prediction["details"]["survival_probability"]

        summary = f"**Heart Failure Risk Assessment**\n\n"
        summary += f"Based on the clinical parameters provided, the AI model estimates:\n\n"
        summary += f"- **Survival Probability**: {survival_prob}%\n"
        summary += f"- **Mortality Risk**: {death_prob}%\n"
        summary += f"- **Risk Level**: {severity.label}\n\n"

        if severity.level == "Severe":
            summary += ("⚠️ The analysis indicates a **high risk** of heart failure mortality. "
                        "Immediate consultation with a cardiologist is strongly recommended. "
                        "Factors such as ejection fraction, serum creatinine, and follow-up period "
                        "significantly influence this assessment.")
        elif severity.level == "Moderate":
            summary += ("The analysis indicates a **moderate risk** level. Regular monitoring and "
                        "follow-up with a healthcare provider is recommended to manage risk factors.")
        else:
            summary += ("The analysis indicates a **low risk** level. Continue regular health "
                        "check-ups and maintain a healthy lifestyle to keep risk factors managed.")

        return summary
