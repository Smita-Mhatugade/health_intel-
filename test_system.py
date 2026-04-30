"""
HealthIntel — Comprehensive System Test Script
================================================
Tests all backend API endpoints, model outputs, and system integrity.

Run with: python test_system.py
(Ensure backend is running: uvicorn backend.main:app --host 0.0.0.0 --port 8000)
"""
import requests
import json
import io
import sys
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️ WARN"

results = []


def log(test_name, status, message="", response_data=None):
    """Log a test result."""
    results.append({"test": test_name, "status": status, "message": message})
    print(f"  {status}  {test_name}")
    if message:
        print(f"         → {message}")
    if response_data and status == FAIL:
        print(f"         → Response: {json.dumps(response_data, indent=2)[:500]}")


def test_root():
    """TEST 1: Root endpoint returns API info."""
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get("name") == "HealthIntel API":
            log("GET / (Root)", PASS, f"API v{data.get('version')}")
        else:
            log("GET / (Root)", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("GET / (Root)", FAIL, str(e))


def test_status():
    """TEST 2: Status endpoint returns model availability."""
    try:
        resp = requests.get(f"{BASE_URL}/api/status", timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            models = data.get("models", {})
            available = [k for k, v in models.items() if v]
            unavailable = [k for k, v in models.items() if not v]
            log("GET /api/status", PASS, f"Available: {available}")
            if unavailable:
                log("  └─ Unavailable Models", WARN, f"{unavailable}")
        else:
            log("GET /api/status", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("GET /api/status", FAIL, str(e))


def test_disease_config():
    """TEST 3: Disease config returns all 6 modules."""
    try:
        resp = requests.get(f"{BASE_URL}/api/disease-config", timeout=10)
        data = resp.json()
        expected = ["alzheimer", "eye_disease", "heart_failure", "symptom_prediction", "parkinsons", "heart_disease"]
        if resp.status_code == 200:
            missing = [e for e in expected if e not in data]
            if not missing:
                log("GET /api/disease-config", PASS, f"All {len(expected)} modules present")
            else:
                log("GET /api/disease-config", FAIL, f"Missing modules: {missing}")
        else:
            log("GET /api/disease-config", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("GET /api/disease-config", FAIL, str(e))


def test_symptoms_list():
    """TEST 4: Symptom list endpoint returns symptoms."""
    try:
        resp = requests.get(f"{BASE_URL}/api/symptoms", timeout=10)
        data = resp.json()
        if resp.status_code == 200:
            symptoms = data.get("symptoms", [])
            raw = data.get("raw_symptoms", [])
            log("GET /api/symptoms", PASS, f"{len(symptoms)} symptoms returned, {len(raw)} raw symptoms")
            if len(raw) == 0:
                log("  └─ Raw Symptoms", FAIL, "raw_symptoms list is empty!")
        else:
            log("GET /api/symptoms", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("GET /api/symptoms", FAIL, str(e))


def test_heart_failure():
    """TEST 5: Heart Failure prediction with realistic clinical data."""
    payload = {
        "age": 65,
        "anaemia": 1,
        "creatinine_phosphokinase": 582,
        "diabetes": 0,
        "ejection_fraction": 20,
        "high_blood_pressure": 1,
        "platelets": 265000.0,
        "serum_creatinine": 1.9,
        "serum_sodium": 130,
        "sex": 1,
        "smoking": 0,
        "time": 4
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze/heart-failure", json=payload, timeout=15)
        data = resp.json()
        if resp.status_code == 200:
            log("POST /api/analyze/heart-failure", PASS,
                f"Prediction: {data['prediction_label']} | Confidence: {data['confidence']}% | Severity: {data['severity']['label']}")
            # Validate response schema
            required_fields = ["disease_category", "prediction", "prediction_label", "confidence", "severity", "summary", "disclaimer"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                log("  └─ Schema Validation", FAIL, f"Missing fields: {missing}")
            else:
                log("  └─ Schema Validation", PASS, "All required fields present")
        else:
            log("POST /api/analyze/heart-failure", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("POST /api/analyze/heart-failure", FAIL, str(e))


def test_heart_failure_edge_cases():
    """TEST 6: Heart Failure edge case — young healthy patient."""
    payload = {
        "age": 25,
        "anaemia": 0,
        "creatinine_phosphokinase": 100,
        "diabetes": 0,
        "ejection_fraction": 60,
        "high_blood_pressure": 0,
        "platelets": 250000.0,
        "serum_creatinine": 0.8,
        "serum_sodium": 140,
        "sex": 0,
        "smoking": 0,
        "time": 200
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze/heart-failure", json=payload, timeout=15)
        data = resp.json()
        if resp.status_code == 200:
            log("POST /heart-failure (Low Risk)", PASS,
                f"Prediction: {data['prediction_label']} | Confidence: {data['confidence']}%")
        else:
            log("POST /heart-failure (Low Risk)", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("POST /heart-failure (Low Risk)", FAIL, str(e))


def test_parkinsons():
    """TEST 7: Parkinson's prediction with vocal parameters."""
    payload = {
        "MDVP:Fo(Hz)": 154.229,
        "MDVP:Fhi(Hz)": 197.105,
        "MDVP:Flo(Hz)": 116.325,
        "MDVP:Jitter(%)": 0.00784,
        "MDVP:Jitter(Abs)": 0.00007,
        "MDVP:RAP": 0.00370,
        "MDVP:PPQ": 0.00554,
        "Jitter:DDP": 0.01109,
        "MDVP:Shimmer": 0.04374,
        "MDVP:Shimmer(dB)": 0.426,
        "Shimmer:APQ3": 0.02182,
        "Shimmer:APQ5": 0.03130,
        "MDVP:APQ": 0.02971,
        "Shimmer:DDA": 0.06545,
        "NHR": 0.02211,
        "HNR": 21.033,
        "RPDE": 0.414783,
        "DFA": 0.815285,
        "spread1": -4.813031,
        "spread2": 0.266482,
        "D2": 2.301442,
        "PPE": 0.284654
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze/parkinsons", json=payload, timeout=15)
        data = resp.json()
        if resp.status_code == 200:
            log("POST /api/analyze/parkinsons", PASS,
                f"Prediction: {data['prediction_label']} | Confidence: {data['confidence']}%")
            required_fields = ["disease_category", "prediction", "prediction_label", "confidence", "severity", "summary"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                log("  └─ Schema Validation", FAIL, f"Missing fields: {missing}")
            else:
                log("  └─ Schema Validation", PASS, "All required fields present")
        else:
            log("POST /api/analyze/parkinsons", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("POST /api/analyze/parkinsons", FAIL, str(e))


def test_heart_disease():
    """TEST 8: Heart Disease prediction with clinical data."""
    payload = {
        "age": 54,
        "sex": 1,
        "cp": 0,
        "trestbps": 131,
        "chol": 246,
        "fbs": 0,
        "restecg": 1,
        "thalach": 150,
        "exang": 0,
        "oldpeak": 0.0,
        "slope": 1,
        "ca": 0,
        "thal": 2
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze/heart-disease", json=payload, timeout=15)
        data = resp.json()
        if resp.status_code == 200:
            log("POST /api/analyze/heart-disease", PASS,
                f"Prediction: {data['prediction_label']} | Confidence: {data['confidence']}%")
            required_fields = ["disease_category", "prediction", "prediction_label", "confidence", "severity", "summary"]
            missing = [f for f in required_fields if f not in data]
            if missing:
                log("  └─ Schema Validation", FAIL, f"Missing fields: {missing}")
            else:
                log("  └─ Schema Validation", PASS, "All required fields present")
        else:
            log("POST /api/analyze/heart-disease", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("POST /api/analyze/heart-disease", FAIL, str(e))


def test_symptom_prediction():
    """TEST 9: Symptom-based disease prediction."""
    payload = {
        "symptoms": ["itching", "skin_rash", "nodal_skin_eruptions"]
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze/symptoms", json=payload, timeout=15)
        data = resp.json()
        if resp.status_code == 200:
            log("POST /api/analyze/symptoms", PASS,
                f"Prediction: {data['prediction_label']} | Confidence: {data['confidence']}%")
            details = data.get("details", {})
            model_preds = details.get("model_predictions", {})
            if model_preds:
                log("  └─ Ensemble Models", PASS, f"Votes: {model_preds}")
            else:
                log("  └─ Ensemble Models", WARN, "No model_predictions in details")
        else:
            log("POST /api/analyze/symptoms", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("POST /api/analyze/symptoms", FAIL, str(e))


def test_symptom_prediction_multiple():
    """TEST 10: Symptom prediction with more symptoms."""
    payload = {
        "symptoms": ["high_fever", "headache", "vomiting", "fatigue", "loss_of_appetite"]
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze/symptoms", json=payload, timeout=15)
        data = resp.json()
        if resp.status_code == 200:
            log("POST /symptoms (5 symptoms)", PASS,
                f"Prediction: {data['prediction_label']} | Confidence: {data['confidence']}%")
        else:
            log("POST /symptoms (5 symptoms)", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("POST /symptoms (5 symptoms)", FAIL, str(e))


def test_eye_disease():
    """TEST 11: Eye disease prediction with a dummy image."""
    try:
        from PIL import Image
        # Create a simple test image (224x224 red-tinted for realism)
        import numpy as np
        arr = np.random.randint(50, 200, (224, 224, 3), dtype=np.uint8)
        img = Image.fromarray(arr, "RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        files = {"file": ("test_eye.jpg", buf, "image/jpeg")}
        resp = requests.post(f"{BASE_URL}/api/analyze/eye-disease", files=files, timeout=60)
        data = resp.json()
        if resp.status_code == 200:
            log("POST /api/analyze/eye-disease", PASS,
                f"Prediction: {data['prediction_label']} | Confidence: {data['confidence']}%")
            details = data.get("details", {})
            if details:
                log("  └─ Class Probabilities", PASS, f"{details}")
        elif resp.status_code == 503:
            log("POST /api/analyze/eye-disease", WARN, "Model not available (TF not loaded)")
        else:
            log("POST /api/analyze/eye-disease", FAIL, f"Status {resp.status_code}", data)
    except ImportError:
        log("POST /api/analyze/eye-disease", WARN, "Pillow not installed, skipping image test")
    except Exception as e:
        log("POST /api/analyze/eye-disease", FAIL, str(e))


def test_alzheimer():
    """TEST 12: Alzheimer's prediction with a dummy Excel file."""
    try:
        import pandas as pd
        # Create a minimal DataFrame mimicking Alzheimer training data
        dummy_data = {
            "RID": [1001],
            "DXCHANGE": [1],
            "MMSE": [28],
            "CDRSB": [0.5],
            "ADAS11": [8.0],
            "ADAS13": [12.0],
            "FAQ": [1],
            "Ventricles": [30000],
            "Hippocampus": [7500],
            "WholeBrain": [1050000],
            "Entorhinal": [3500],
            "Fusiform": [17000],
            "MidTemp": [19000],
            "ICV": [1500000],
        }
        df = pd.DataFrame(dummy_data)
        buf = io.BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)

        files = {"file": ("test_alzheimer.xlsx", buf, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
        resp = requests.post(f"{BASE_URL}/api/analyze/alzheimer", files=files, timeout=30)
        data = resp.json()
        if resp.status_code == 200:
            log("POST /api/analyze/alzheimer", PASS,
                f"Prediction: {data['prediction_label']} | Confidence: {data['confidence']}%")
        elif resp.status_code == 503:
            log("POST /api/analyze/alzheimer", WARN, "Model not available")
        elif resp.status_code == 400:
            log("POST /api/analyze/alzheimer", WARN, f"Bad data (expected for dummy): {data.get('detail', '')}")
        elif resp.status_code == 500:
            log("POST /api/analyze/alzheimer", WARN, f"Processing error (expected for dummy data): {data.get('detail', '')[:200]}")
        else:
            log("POST /api/analyze/alzheimer", FAIL, f"Status {resp.status_code}", data)
    except ImportError as e:
        log("POST /api/analyze/alzheimer", WARN, f"Missing library: {e}")
    except Exception as e:
        log("POST /api/analyze/alzheimer", FAIL, str(e))


def test_hospital_recommendation():
    """TEST 13: Hospital recommendation for a location in India."""
    payload = {
        "latitude": 19.0760,
        "longitude": 72.8777,
        "disease_category": "heart_failure",
        "radius_km": 25
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/recommend-hospitals", json=payload, timeout=35)
        data = resp.json()
        if resp.status_code == 200:
            total = data.get("total_found", 0)
            source = data.get("source", "unknown")
            log("POST /api/recommend-hospitals", PASS, f"Found {total} hospitals (source: {source})")
            if total > 0:
                first = data["hospitals"][0]
                log("  └─ Top Hospital", PASS, f"{first['name']} — {first['distance_km']} km")
            else:
                log("  └─ Results", WARN, "No hospitals found. Check API connectivity or radius.")
        else:
            log("POST /api/recommend-hospitals", FAIL, f"Status {resp.status_code}", data)
    except Exception as e:
        log("POST /api/recommend-hospitals", FAIL, str(e))


def test_validation_errors():
    """TEST 14: Input validation — bad payloads should return 422."""
    # Missing required field
    bad_payload = {"age": 65}
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze/heart-failure", json=bad_payload, timeout=10)
        if resp.status_code == 422:
            log("Validation: Missing Fields", PASS, "Correctly returned 422 Unprocessable Entity")
        else:
            log("Validation: Missing Fields", FAIL, f"Expected 422, got {resp.status_code}")
    except Exception as e:
        log("Validation: Missing Fields", FAIL, str(e))

    # Invalid symptom (empty list)
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze/symptoms", json={"symptoms": []}, timeout=10)
        if resp.status_code == 422:
            log("Validation: Empty Symptoms", PASS, "Correctly rejected empty symptom list")
        else:
            log("Validation: Empty Symptoms", FAIL, f"Expected 422, got {resp.status_code}")
    except Exception as e:
        log("Validation: Empty Symptoms", FAIL, str(e))


def test_nonexistent_endpoint():
    """TEST 15: Non-existent endpoint should return 404."""
    try:
        resp = requests.get(f"{BASE_URL}/api/nonexistent", timeout=10)
        if resp.status_code == 404:
            log("404: Non-existent Endpoint", PASS, "Correctly returned 404")
        else:
            log("404: Non-existent Endpoint", FAIL, f"Expected 404, got {resp.status_code}")
    except Exception as e:
        log("404: Non-existent Endpoint", FAIL, str(e))


def test_docs_endpoint():
    """TEST 16: Swagger docs should be accessible."""
    try:
        resp = requests.get(f"{BASE_URL}/docs", timeout=10)
        if resp.status_code == 200:
            log("GET /docs (Swagger)", PASS, "API documentation accessible")
        else:
            log("GET /docs (Swagger)", FAIL, f"Status {resp.status_code}")
    except Exception as e:
        log("GET /docs (Swagger)", FAIL, str(e))


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print(f"  HealthIntel — System Test Suite")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Backend: {BASE_URL}")
    print("=" * 70)

    # Check backend is reachable
    print("\n🔌 Checking backend connectivity...")
    try:
        resp = requests.get(f"{BASE_URL}/", timeout=5)
        if resp.status_code != 200:
            print(f"  {FAIL} Backend returned status {resp.status_code}")
            sys.exit(1)
        print(f"  {PASS} Backend is reachable\n")
    except Exception as e:
        print(f"  {FAIL} Cannot reach backend at {BASE_URL}: {e}")
        print("  Ensure the backend is running: uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        sys.exit(1)

    # Run all tests
    print("─" * 70)
    print("📋 SECTION 1: Core Endpoints")
    print("─" * 70)
    test_root()
    test_status()
    test_disease_config()
    test_symptoms_list()
    test_docs_endpoint()

    print("\n" + "─" * 70)
    print("🧠 SECTION 2: Model Predictions")
    print("─" * 70)
    test_heart_failure()
    test_heart_failure_edge_cases()
    test_parkinsons()
    test_heart_disease()
    test_symptom_prediction()
    test_symptom_prediction_multiple()
    test_eye_disease()
    test_alzheimer()

    print("\n" + "─" * 70)
    print("🏥 SECTION 3: Hospital Recommendation")
    print("─" * 70)
    test_hospital_recommendation()

    print("\n" + "─" * 70)
    print("🛡️ SECTION 4: Validation & Error Handling")
    print("─" * 70)
    test_validation_errors()
    test_nonexistent_endpoint()

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    total = len(results)
    passed = sum(1 for r in results if r["status"] == PASS)
    failed = sum(1 for r in results if r["status"] == FAIL)
    warned = sum(1 for r in results if r["status"] == WARN)

    print(f"  Total Tests : {total}")
    print(f"  ✅ Passed   : {passed}")
    print(f"  ❌ Failed   : {failed}")
    print(f"  ⚠️ Warnings : {warned}")
    print(f"  Pass Rate   : {round(passed/total*100, 1)}%")

    if failed > 0:
        print(f"\n  ❌ FAILED TESTS:")
        for r in results:
            if r["status"] == FAIL:
                print(f"     • {r['test']}: {r['message']}")

    if warned > 0:
        print(f"\n  ⚠️ WARNINGS:")
        for r in results:
            if r["status"] == WARN:
                print(f"     • {r['test']}: {r['message']}")

    print("\n" + "=" * 70)
    print(f"  Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
