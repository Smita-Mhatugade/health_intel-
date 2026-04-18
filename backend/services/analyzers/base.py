"""Abstract base class for all disease analyzers."""
from abc import ABC, abstractmethod
from typing import Any, Dict
from backend.models.schemas import AnalysisResult, SeverityLevel


class BaseAnalyzer(ABC):
    """Base class that all disease-specific analyzers must implement."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is loaded and ready for inference."""
        pass

    @abstractmethod
    def preprocess(self, data: Any) -> Any:
        """Preprocess raw input data into model-ready format."""
        pass

    @abstractmethod
    def predict(self, processed_input: Any) -> Dict[str, Any]:
        """Run inference and return raw prediction results."""
        pass

    @abstractmethod
    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        """Convert raw prediction into a severity assessment."""
        pass

    @abstractmethod
    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        """Generate a patient-friendly summary from the prediction and severity."""
        pass

    def analyze(self, data: Any) -> AnalysisResult:
        """Full analysis pipeline: preprocess → predict → assess → summarize."""
        processed = self.preprocess(data)
        prediction = self.predict(processed)
        severity = self.assess_severity(prediction)
        summary = self.generate_summary(prediction, severity)

        return AnalysisResult(
            disease_category=prediction.get("disease_category", "unknown"),
            prediction=prediction.get("prediction", "unknown"),
            prediction_label=prediction.get("prediction_label", "Unknown"),
            confidence=prediction.get("confidence", 0.0),
            severity=severity,
            summary=summary,
            details=prediction.get("details"),
        )
