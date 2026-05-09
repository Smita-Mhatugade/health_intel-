"""Model loader — initializes and caches all disease analyzers."""
from backend.services.analyzers.all_analyzers import (
    HeartFailureAnalyzer,
    AlzheimerAnalyzer,
    SymptomAnalyzer,
    EyeDiseaseAnalyzer,
    ParkinsonAnalyzer,
    HeartDiseaseAnalyzer,
    BaseAnalyzer
)

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
    _analyzers["parkinsons"] = ParkinsonAnalyzer()
    _analyzers["heart_disease"] = HeartDiseaseAnalyzer()

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
