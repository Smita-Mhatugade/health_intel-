"""Model loader — initializes and caches all disease analyzers."""
from backend.services.analyzers.heart_failure_analyzer import HeartFailureAnalyzer
from backend.services.analyzers.alzheimer_analyzer import AlzheimerAnalyzer
from backend.services.analyzers.symptom_analyzer import SymptomAnalyzer
from backend.services.analyzers.eye_disease_analyzer import EyeDiseaseAnalyzer
from backend.services.analyzers.base import BaseAnalyzer

_analyzers = {}


def load_all_models():
    """Load all disease analyzers at startup."""
    global _analyzers
    print("\n" + "=" * 60)
    print("Loading HealthIntel ML Models...")
    print("=" * 60)

    _analyzers["heart_failure"] = HeartFailureAnalyzer()
    _analyzers["alzheimer"] = AlzheimerAnalyzer()
    _analyzers["symptom_prediction"] = SymptomAnalyzer()
    _analyzers["eye_disease"] = EyeDiseaseAnalyzer()

    available = [k for k, v in _analyzers.items() if v.is_available()]
    unavailable = [k for k, v in _analyzers.items() if not v.is_available()]

    print(f"\n[OK] Available models: {available}")
    if unavailable:
        print(f"[WARN] Unavailable models: {unavailable}")
    print("=" * 60 + "\n")


def get_analyzer(disease_category: str) -> BaseAnalyzer:
    """Get a specific analyzer by disease category."""
    analyzer = _analyzers.get(disease_category)
    if analyzer is None:
        raise ValueError(f"Unknown disease category: {disease_category}")
    return analyzer


def get_all_status() -> dict:
    """Get availability status of all analyzers."""
    return {k: v.is_available() for k, v in _analyzers.items()}
