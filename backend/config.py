"""Backend configuration and settings."""
import os
import json
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = BASE_DIR / "uploads"

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Model paths
HEART_FAILURE_MODEL_PATH = MODELS_DIR / "heart_failure_lr.pkl"
ALZHEIMER_MODEL_PATH = MODELS_DIR / "alzheimer_rf.pkl"
SYMPTOM_MODELS_DIR = MODELS_DIR / "symptom_prediction"
EYE_DISEASE_MODEL_PATH = MODELS_DIR / "eye_disease_model.h5"
PARKINSONS_MODEL_PATH = MODELS_DIR / "parkinsons_model.pkl"
HEART_DISEASE_MODEL_PATH = MODELS_DIR / "heart_disease_model.pkl"

# Data paths
DISEASE_SPECIALTIES_PATH = DATA_DIR / "disease_specialties.json"
HOSPITALS_CSV_PATH = DATA_DIR / "hospitals.csv"
SYMPTOM_DATA_DIR = DATA_DIR / "symptom_data"
SYMPTOM_TRAINING_CSV = SYMPTOM_DATA_DIR / "training.csv"

# Load disease specialties config
def load_disease_config():
    with open(DISEASE_SPECIALTIES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# Supported disease categories
DISEASE_CATEGORIES = [
    "alzheimer", 
    "heart_failure", 
    "symptom_prediction", 
    "eye_disease", 
    "parkinsons", 
    "heart_disease"
]

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000

# Hospital recommendation
HOSPITAL_SEARCH_RADIUS_KM = 50
OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
GEOAPIFY_API_KEY = os.getenv("GEOAPIFY_API_KEY", "")

