"""Eye Disease Detection Analyzer (Placeholder - model not yet trained)."""
from typing import Any, Dict
from backend.services.analyzers.base import BaseAnalyzer
from backend.models.schemas import AnalysisResult, SeverityLevel


class EyeDiseaseAnalyzer(BaseAnalyzer):
    """
    Placeholder analyzer for Eye Disease Detection.
    The full image dataset is required to train the ResNet34 model.
    """

    def __init__(self):
        self._loaded = False
        print("[EyeDiseaseAnalyzer] Model not available - full dataset required for training.")

    def is_available(self) -> bool:
        return False

    def preprocess(self, data: Any) -> Any:
        raise NotImplementedError(
            "Eye Disease model is not yet trained. "
            "Please provide the full Augmented Dataset with all 5 class folders "
            "(Glaucoma, Cataracts, Uveitis, Crossed Eyes, Bulging Eyes) "
            "and run training/train_eye_disease.py first."
        )

    def predict(self, processed_input: Any) -> Dict[str, Any]:
        raise NotImplementedError("Eye Disease model not available.")

    def assess_severity(self, prediction: Dict[str, Any]) -> SeverityLevel:
        raise NotImplementedError("Eye Disease model not available.")

    def generate_summary(self, prediction: Dict[str, Any], severity: SeverityLevel) -> str:
        raise NotImplementedError("Eye Disease model not available.")

    def analyze(self, data: Any) -> AnalysisResult:
        return AnalysisResult(
            disease_category="eye_disease",
            prediction="unavailable",
            prediction_label="Model Not Available",
            confidence=0.0,
            severity=SeverityLevel(
                level="Unknown", label="Model Not Trained", color="#6b7280"
            ),
            summary=(
                "**Eye Disease Detection Module - Not Available**\n\n"
                "The Eye Disease Detection model requires the full image dataset "
                "for training. Currently, the dataset is incomplete.\n\n"
                "**To enable this module:**\n"
                "1. Provide the complete Augmented Dataset with all 5 class folders:\n"
                "   - Glaucoma\n"
                "   - Cataracts\n"
                "   - Uveitis\n"
                "   - Crossed Eyes\n"
                "   - Bulging Eyes\n"
                "2. Run `python training/train_eye_disease.py`\n"
                "3. Restart the backend server"
            ),
        )
