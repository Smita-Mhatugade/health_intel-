"""
Unified medical analyzers for HealthIntel.
Combines all disease-specific analysis logic into a single maintainable file.
"""
import numpy as np
import pandas as pd
import joblib
import io
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod
from PIL import Image

# We use a lazy loading approach for tensorflow/keras to avoid crashes on incompatible CPUs
_keras_load_model = None
HAS_TENSORFLOW = False

def check_tensorflow():
    """Lazy check for TensorFlow availability without crashing the process."""
    global _keras_load_model, HAS_TENSORFLOW
    if HAS_TENSORFLOW:
        return True
    
    try:
        # We import inside a function to avoid top-level initialization crashes
        import tensorflow as tf
        # Check if it actually works by accessing a basic attribute
        _ = tf.__version__
        _keras_load_model = tf.keras.models.load_model
        HAS_TENSORFLOW = True
        return True
    except (ImportError, AttributeError, Exception) as e:
        print(f"[System] TensorFlow/Keras not available or failed to initialize: {e}")
        HAS_TENSORFLOW = False
        return False

from backend.schemas.schemas import SeverityLevel, AnalysisResult
from backend import config


class BaseAnalyzer(ABC):
    """Abstract base class for all disease analyzers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the underlying model is loaded and ready."""
        pass

    @abstractmethod
    def preprocess(self, data: Any) -> Any:
        """Transform raw input data into model-ready format."""
        pass

    @abstractmethod
    def predict(self, processed_input: Any) -> Dict[str, Any]:
        """Run inference and return raw prediction results."""
        pass

    @abstractmethod
    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        """Determine severity level from prediction results."""
        pass

    @abstractmethod
    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        """Generate a human-readable summary of the findings."""
        pass

    def analyze(self, data: Any) -> AnalysisResult:
        """Full analysis pipeline: preprocess -> predict -> assess -> summarize."""
        if not self.is_available():
            return AnalysisResult(
                disease_category="unknown",
                prediction="unavailable",
                prediction_label="Model Not Available",
                confidence=0.0,
                severity=SeverityLevel(level="Unknown", label="Model Not Loaded", color="#6b7280"),
                summary="The analysis module is currently unavailable."
            )

        try:
            processed = self.preprocess(data)
            prediction = self.predict(processed)
            severity = self.assess_severity(prediction)
            summary = self.generate_summary(prediction, severity)

            return AnalysisResult(
                disease_category=prediction.get("disease_category", "unknown"),
                prediction=prediction["prediction"],
                prediction_label=prediction["prediction_label"],
                confidence=prediction["confidence"],
                severity=severity,
                summary=summary,
                details=prediction.get("details")
            )
        except Exception as e:
            print(f"[Analyzer Error] {str(e)}")
            raise e


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
            if config.HEART_FAILURE_MODEL_PATH.exists():
                artifact = joblib.load(config.HEART_FAILURE_MODEL_PATH)
                self._model = artifact["model"]
                self._scaler = artifact["scaler"]
                self._feature_names = artifact["feature_names"]
                self._loaded = True
                print("[HeartFailureAnalyzer] Model loaded.")
        except Exception as e:
            print(f"[HeartFailureAnalyzer] Load failed: {e}")

    def is_available(self) -> bool:
        return self._loaded

    def preprocess(self, data: Dict[str, Any]) -> np.ndarray:
        values = [float(data[f]) for f in self._feature_names]
        arr = np.array(values).reshape(1, -1)
        return self._scaler.transform(arr)

    def predict(self, processed_input: np.ndarray) -> Dict[str, Any]:
        probabilities = self._model.predict_proba(processed_input)[0]
        prediction = 1 if probabilities[1] > 0.5 else 0
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
        summary = f"**Heart Failure Risk Assessment**\n\nEstimated Mortality Risk: {death_prob}%\nRisk Level: {severity.label}\n\n"
        if severity.level == "Severe":
            summary += "⚠️ High risk detected. Immediate cardiologist consultation recommended."
        return summary


class AlzheimerAnalyzer(BaseAnalyzer):
    """Analyzes clinical/cognitive data for Alzheimer classification."""

    def __init__(self):
        self._model = None
        self._scaler = None
        self._label_encoder = None
        self._feature_names = None
        self._class_names = None
        self._loaded = False
        self._load_model()

    def _load_model(self):
        try:
            if config.ALZHEIMER_MODEL_PATH.exists():
                artifact = joblib.load(config.ALZHEIMER_MODEL_PATH)
                self._model = artifact["model"]
                self._scaler = artifact["scaler"]
                self._label_encoder = artifact["label_encoder"]
                self._feature_names = artifact["feature_names"]
                self._class_names = artifact["class_names"]
                self._label_encoders_cat = artifact.get("label_encoders_categorical", {})
                self._loaded = True
                print("[AlzheimerAnalyzer] Model loaded.")
        except Exception as e:
            print(f"[AlzheimerAnalyzer] Load failed: {e}")

    def is_available(self) -> bool:
        return self._loaded

    def preprocess(self, data: Any) -> np.ndarray:
        if not isinstance(data, pd.DataFrame):
            raise ValueError("AlzheimerAnalyzer requires a DataFrame")
        df = data.copy()
        # Add all missing columns at once to avoid DataFrame fragmentation
        missing_cols = [f for f in self._feature_names if f not in df.columns]
        if missing_cols:
            missing_df = pd.DataFrame(0, index=df.index, columns=missing_cols)
            df = pd.concat([df, missing_df], axis=1)
        df = df[self._feature_names]
        for col, le in self._label_encoders_cat.items():
            if col in df.columns:
                try: df[col] = le.transform(df[col].astype(str))
                except: df[col] = 0
        return self._scaler.transform(df.iloc[0:1].values.astype(float))

    def predict(self, processed_input: np.ndarray) -> Dict[str, Any]:
        probs = self._model.predict_proba(processed_input)[0]
        idx = np.argmax(probs)
        pred_class = self._label_encoder.inverse_transform([idx])[0]
        labels = {"CN": "Cognitive Normal", "AD": "Alzheimer's Disease", "LMCI": "Late Mild Cognitive Impairment"}
        return {
            "disease_category": "alzheimer",
            "prediction": pred_class,
            "prediction_label": labels.get(pred_class, pred_class),
            "confidence": round(float(probs[idx]) * 100, 2),
            "details": {"class_probabilities": {c: round(float(probs[i])*100, 2) for i, c in enumerate(self._class_names)}}
        }

    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        p = prediction["prediction"]
        if p == "CN": return SeverityLevel(level="Normal", label="Normal", color="#22c55e", confidence=prediction["confidence"])
        if p == "LMCI": return SeverityLevel(level="Moderate", label="Late MCI", color="#f59e0b", confidence=prediction["confidence"])
        return SeverityLevel(level="Severe", label="Alzheimer's", color="#ef4444", confidence=prediction["confidence"])

    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        return f"**Alzheimer's Assessment**\n\nClassification: **{prediction['prediction_label']}**\nConfidence: {prediction['confidence']}%"


class SymptomAnalyzer(BaseAnalyzer):
    """Predicts disease from symptom checklist using ensemble."""

    def __init__(self):
        self._models = {}
        self._symptom_columns = []
        self._disease_labels = {}
        self._loaded = False
        self._load_models()

    def _load_models(self):
        try:
            if not config.SYMPTOM_MODELS_DIR.exists(): return
            for f in ["RandomForest_model.pkl", "Xgboost_model.pkl", "catboost_model.pkl"]:
                path = config.SYMPTOM_MODELS_DIR / f
                if path.exists(): self._models[f.split('_')[0]] = joblib.load(path)
            if config.SYMPTOM_TRAINING_CSV.exists():
                df = pd.read_csv(config.SYMPTOM_TRAINING_CSV)
                self._symptom_columns = [c for c in df.columns if c.lower() != "prognosis"]
                if "prognosis" in df.columns:
                    unique = sorted(df["prognosis"].unique())
                    self._disease_labels = {str(i): d for i, d in enumerate(unique)}
                    for d in unique: self._disease_labels[d] = d
            self._loaded = len(self._models) > 0 and len(self._symptom_columns) > 0
            if self._loaded: print(f"[SymptomAnalyzer] Loaded with {len(self._models)} models.")
        except Exception as e: print(f"[SymptomAnalyzer] Load failed: {e}")

    def is_available(self) -> bool: return self._loaded

    def get_symptom_list(self) -> List[str]: return [s.replace("_", " ").title() for s in self._symptom_columns]

    def get_raw_symptom_list(self) -> List[str]: return list(self._symptom_columns)

    def preprocess(self, data: Dict[str, Any]) -> np.ndarray:
        symptoms = [s.lower().replace(" ", "_") for s in data.get("symptoms", [])]
        vec = np.zeros(len(self._symptom_columns))
        for i, c in enumerate(self._symptom_columns):
            if c in symptoms: vec[i] = 1
        return vec.reshape(1, -1)

    def predict(self, processed_input: np.ndarray) -> Dict[str, Any]:
        preds = {}
        for name, m in self._models.items():
            p = str(m.predict(processed_input)[0]).strip("[] ")
            preds[name] = self._disease_labels.get(p, p)
        from collections import Counter
        votes = Counter(preds.values())
        consensus, count = votes.most_common(1)[0]
        return {
            "disease_category": "symptom_prediction",
            "prediction": consensus, "prediction_label": consensus,
            "confidence": round((count / len(preds)) * 100, 2),
            "details": {"model_predictions": preds}
        }

    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        c = prediction["confidence"]
        lvl = "Moderate" if c >= 80 else "Mild"
        return SeverityLevel(level=lvl, label=f"Confidence: {c}%", color="#f59e0b" if lvl=="Moderate" else "#3b82f6", confidence=c)

    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        return f"**Symptom Prediction**\n\nPredicted Disease: **{prediction['prediction']}**\nConfidence: {prediction['confidence']}%"


class EyeDiseaseAnalyzer(BaseAnalyzer):
    """Analyzes eye images for diseases using a VGG19-based Keras model."""

    def __init__(self):
        self._model = None
        self._classes = ["Cataract", "Diabetic Retinopathy", "Glaucoma", "Normal"]
        self._loaded = False
        self._load_model()

    def _load_model(self):
        if not check_tensorflow():
            print("[EyeDiseaseAnalyzer] Skipping Eye Disease module (TensorFlow initialization failed).")
            return
        try:
            if config.EYE_DISEASE_MODEL_PATH.exists():
                self._model = _keras_load_model(str(config.EYE_DISEASE_MODEL_PATH))
                self._loaded = True
                print("[EyeDiseaseAnalyzer] VGG19 model loaded.")
        except Exception as e:
            print(f"[EyeDiseaseAnalyzer] Load failed: {e}")

    def is_available(self) -> bool: return self._loaded

    def preprocess(self, data: Any) -> np.ndarray:
        # data is expected to be bytes from the uploaded image
        img = Image.open(io.BytesIO(data)).convert("RGB")
        img = img.resize((224, 224))  # VGG19 input size
        arr = np.array(img) / 255.0
        return np.expand_dims(arr, axis=0)

    def predict(self, processed_input: np.ndarray) -> Dict[str, Any]:
        preds = self._model.predict(processed_input)[0]
        idx = np.argmax(preds)
        return {
            "disease_category": "eye_disease",
            "prediction": self._classes[idx],
            "prediction_label": self._classes[idx],
            "confidence": round(float(preds[idx]) * 100, 2),
            "details": {c: round(float(preds[i])*100, 2) for i, c in enumerate(self._classes)}
        }

    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        p = prediction["prediction"]
        if p == "Normal":
            return SeverityLevel(level="Normal", label="Healthy Eye", color="#22c55e", confidence=prediction["confidence"])
        elif p == "Cataract":
            return SeverityLevel(level="Moderate", label="Cataract Detected", color="#f59e0b", confidence=prediction["confidence"])
        elif p == "Glaucoma":
            return SeverityLevel(level="Severe", label="Glaucoma Detected", color="#ef4444", confidence=prediction["confidence"])
        elif p == "Diabetic Retinopathy":
            return SeverityLevel(level="Severe", label="Diabetic Retinopathy Detected", color="#ef4444", confidence=prediction["confidence"])
        return SeverityLevel(level="Moderate", label="Consult Specialist", color="#f59e0b", confidence=prediction["confidence"])

    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        return f"**Eye Disease Detection**\n\nResult: **{prediction['prediction']}**\nConfidence: {prediction['confidence']}%"


class ParkinsonAnalyzer(BaseAnalyzer):
    """Predicts Parkinson's disease from vocal parameters."""

    def __init__(self):
        self._model = None
        self._scaler = None
        self._feature_names = None
        self._loaded = False
        self._load_model()

    def _load_model(self):
        try:
            if config.PARKINSONS_MODEL_PATH.exists():
                artifact = joblib.load(config.PARKINSONS_MODEL_PATH)
                self._model = artifact["model"]
                self._scaler = artifact["scaler"]
                self._feature_names = artifact["feature_names"]
                self._loaded = True
                print("[ParkinsonAnalyzer] Model loaded.")
        except Exception as e: print(f"[ParkinsonAnalyzer] Load failed: {e}")

    def is_available(self) -> bool: return self._loaded

    def preprocess(self, data: Dict[str, Any]) -> np.ndarray:
        values = [float(data[f]) for f in self._feature_names]
        return self._scaler.transform(np.array(values).reshape(1, -1))

    def predict(self, processed_input: np.ndarray) -> Dict[str, Any]:
        probabilities = self._model.predict_proba(processed_input)[0]
        prediction = int(np.argmax(probabilities))
        return {
            "disease_category": "parkinsons",
            "prediction": "positive" if prediction == 1 else "negative",
            "prediction_label": "Parkinson's Detected" if prediction == 1 else "No Parkinson's Detected",
            "confidence": round(float(max(probabilities)) * 100, 2),
        }

    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        if prediction["prediction"] == "positive":
            return SeverityLevel(level="Severe", label="High Probability", color="#ef4444", confidence=prediction["confidence"])
        return SeverityLevel(level="Normal", label="Low Probability", color="#22c55e", confidence=prediction["confidence"])

    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        return f"**Parkinson's Assessment**\n\nResult: **{prediction['prediction_label']}**\nConfidence: {prediction['confidence']}%"


class HeartDiseaseAnalyzer(BaseAnalyzer):
    """Predicts Heart Disease risk using clinical parameters."""

    def __init__(self):
        self._model = None
        self._scaler = None
        self._feature_names = None
        self._loaded = False
        self._load_model()

    def _load_model(self):
        try:
            if config.HEART_DISEASE_MODEL_PATH.exists():
                artifact = joblib.load(config.HEART_DISEASE_MODEL_PATH)
                self._model = artifact["model"]
                self._scaler = artifact["scaler"]
                self._feature_names = artifact["feature_names"]
                self._loaded = True
                print("[HeartDiseaseAnalyzer] Model loaded.")
        except Exception as e: print(f"[HeartDiseaseAnalyzer] Load failed: {e}")

    def is_available(self) -> bool: return self._loaded

    def preprocess(self, data: Dict[str, Any]) -> np.ndarray:
        values = [float(data[f]) for f in self._feature_names]
        return self._scaler.transform(np.array(values).reshape(1, -1))

    def predict(self, processed_input: np.ndarray) -> Dict[str, Any]:
        probabilities = self._model.predict_proba(processed_input)[0]
        prediction = int(np.argmax(probabilities))
        return {
            "disease_category": "heart_disease",
            "prediction": "positive" if prediction == 1 else "negative",
            "prediction_label": "Heart Disease Detected" if prediction == 1 else "No Heart Disease Detected",
            "confidence": round(float(max(probabilities)) * 100, 2),
        }

    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        if prediction["prediction"] == "positive":
            return SeverityLevel(level="Severe", label="Positive Indicators", color="#ef4444", confidence=prediction["confidence"])
        return SeverityLevel(level="Normal", label="Negative Indicators", color="#22c55e", confidence=prediction["confidence"])

    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        return f"**Heart Disease Risk Assessment**\n\nResult: **{prediction['prediction_label']}**\nConfidence: {prediction['confidence']}%"
