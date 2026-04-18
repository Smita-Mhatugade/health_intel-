# 🏥 HealthIntel

**AI-Based Medical Report Analysis and Hospital Recommendation System**

HealthIntel is a disease-specific intelligent healthcare decision-support system that analyzes medical inputs (diagnostic reports, clinical data, medical images) using pre-trained machine learning models to estimate disease severity, generate structured health summaries, and recommend nearby hospitals.

> ⚠️ **Disclaimer**: HealthIntel is strictly a decision-support tool and does NOT replace professional medical diagnosis. Always consult qualified healthcare professionals.

---

## 🎯 Features

| Module | Input Type | Model | Status |
|--------|-----------|-------|--------|
| Alzheimer's Detection | Excel (clinical/cognitive/neuroimaging) | Random Forest | ✅ Available |
| Heart Failure Prediction | Clinical form (12 parameters) | Logistic Regression | ✅ Available |
| Disease from Symptoms | Symptom checklist | Ensemble (RF, XGBoost, CatBoost, LGBM) | ✅ Available |
| Eye Disease Detection | Retinal images | ResNet34 (fastai) | ⚠️ Dataset Required |

- **Severity Assessment**: Automated severity levels (Normal → Mild → Moderate → Severe)
- **Health Summaries**: Patient-friendly analysis reports
- **Hospital Recommendations**: Powered by OpenStreetMap (free, no API key needed)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd "Health Intel"
pip install -r requirements.txt
```

### 2. Train Models

```bash
# Heart Failure model
python training/train_heart_failure.py

# Alzheimer model
python training/train_alzheimer.py

# Copy pre-trained Symptom models
python training/setup_symptom_models.py
```

### 3. Start Backend (FastAPI)

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation available at: http://localhost:8000/docs

### 4. Start Frontend (Streamlit)

```bash
streamlit run frontend/app.py
```

Open http://localhost:8501 in your browser.

---

## 📁 Project Structure

```
Health Intel/
├── requirements.txt              # All dependencies
├── README.md                     # This file
├── models/                       # Trained model artifacts (.pkl)
├── data/                         # Static data (hospitals, configs)
│   ├── disease_specialties.json  # Disease → specialty mapping
│   ├── hospitals.csv             # Fallback hospital database
│   └── symptom_data/             # Symptom training/testing CSVs
├── training/                     # Model training scripts
├── backend/                      # FastAPI application
│   ├── main.py                   # API entry point
│   ├── config.py                 # Settings
│   ├── routers/                  # API endpoints
│   ├── models/                   # Pydantic schemas
│   └── services/                 # Business logic
│       ├── analyzers/            # Disease-specific analyzers
│       ├── model_loader.py       # Model initialization
│       └── hospital_recommender.py
├── frontend/                     # Streamlit application
│   ├── app.py                    # Main UI
│   └── assets/                   # CSS styles
├── Alzheimer Detection/          # Original notebooks (preserved)
├── Eye Disease Detection/
├── Heart Failure Prediction/
└── Disease-Prediction-Based-on-Symptoms-main/
```

---

## 🔧 Technology Stack

- **Backend**: FastAPI, Uvicorn
- **Frontend**: Streamlit
- **ML/DL**: scikit-learn, XGBoost, CatBoost, LightGBM
- **Data**: Pandas, NumPy
- **Hospital Search**: OpenStreetMap Overpass API (free), Nominatim (free geocoding)
- **Mapping**: Folium + streamlit-folium

---

## 🔒 Ethical & Safety Considerations

- System does NOT provide medical diagnoses or prescriptions
- Clear disclaimers on all analysis pages
- User data is NOT permanently stored
- Follows responsible AI principles
