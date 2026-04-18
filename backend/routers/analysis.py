"""Analysis router — handles medical data analysis requests."""
import io
import json
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.models.schemas import AnalysisResult, HeartFailureInput, SymptomInput
from backend.services import model_loader

router = APIRouter(prefix="/api", tags=["Analysis"])


@router.get("/status")
async def get_status():
    """Get availability status of all disease analysis modules."""
    return {
        "status": "healthy",
        "models": model_loader.get_all_status(),
    }


@router.post("/analyze/heart-failure", response_model=AnalysisResult)
async def analyze_heart_failure(data: HeartFailureInput):
    """Analyze heart failure risk from clinical parameters."""
    analyzer = model_loader.get_analyzer("heart_failure")
    if not analyzer.is_available():
        raise HTTPException(status_code=503, detail="Heart failure model not available. Run training first.")
    return analyzer.analyze(data.model_dump())


@router.post("/analyze/alzheimer", response_model=AnalysisResult)
async def analyze_alzheimer(file: UploadFile = File(...)):
    """Analyze Alzheimer's disease risk from uploaded Excel data."""
    analyzer = model_loader.get_analyzer("alzheimer")
    if not analyzer.is_available():
        raise HTTPException(status_code=503, detail="Alzheimer model not available. Run training first.")

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Please upload an Excel file (.xlsx or .xls)")

    try:
        contents = await file.read()
        # Try to load and merge sheets like the training pipeline
        xls = pd.ExcelFile(io.BytesIO(contents))
        sheets = xls.sheet_names

        if len(sheets) >= 3:
            diagnosis_df = pd.read_excel(io.BytesIO(contents), sheet_name=sheets[0])
            cognitive_df = pd.read_excel(io.BytesIO(contents), sheet_name=sheets[1])
            data_df = pd.read_excel(io.BytesIO(contents), sheet_name=sheets[2])
            diagnosis_df.dropna(inplace=True)
            cognitive_df.dropna(inplace=True)
            data_df.dropna(inplace=True)
            merged = diagnosis_df.merge(cognitive_df, on="RID").merge(data_df, on="RID")
        else:
            merged = pd.read_excel(io.BytesIO(contents))
            merged.dropna(inplace=True)

        if merged.empty:
            raise HTTPException(status_code=400, detail="No valid data rows found after processing.")

        return analyzer.analyze(merged)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/analyze/symptoms", response_model=AnalysisResult)
async def analyze_symptoms(data: SymptomInput):
    """Predict disease from symptom checklist."""
    analyzer = model_loader.get_analyzer("symptom_prediction")
    if not analyzer.is_available():
        raise HTTPException(status_code=503, detail="Symptom prediction models not available.")
    return analyzer.analyze({"symptoms": data.symptoms})


@router.get("/symptoms")
async def get_symptom_list():
    """Get available symptoms for the symptom prediction module."""
    analyzer = model_loader.get_analyzer("symptom_prediction")
    if not analyzer.is_available():
        raise HTTPException(status_code=503, detail="Symptom prediction not available.")
    return {
        "symptoms": analyzer.get_symptom_list(),
        "raw_symptoms": analyzer.get_raw_symptom_list(),
    }


@router.post("/analyze/eye-disease", response_model=AnalysisResult)
async def analyze_eye_disease(file: UploadFile = File(...)):
    """Analyze eye disease from uploaded image (currently unavailable)."""
    analyzer = model_loader.get_analyzer("eye_disease")
    return analyzer.analyze(None)


@router.get("/disease-config")
async def get_disease_config():
    """Get disease configuration including input types, specialties, etc."""
    from backend.config import load_disease_config
    config = load_disease_config()
    status = model_loader.get_all_status()
    for key in config:
        config[key]["model_available"] = status.get(key, False)
    return config
