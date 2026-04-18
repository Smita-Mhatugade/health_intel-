"""
HealthIntel Backend — FastAPI Application
==========================================
AI-Based Medical Report Analysis and Hospital Recommendation System.

Run with: uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.services.model_loader import load_all_models
from backend.routers import analysis, hospitals


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models on startup."""
    load_all_models()
    yield
    print("HealthIntel backend shutting down.")


app = FastAPI(
    title="HealthIntel API",
    description=(
        "AI-Based Medical Report Analysis and Hospital Recommendation System. "
        "This system analyzes medical reports, estimates disease severity, "
        "generates health summaries, and recommends nearby hospitals."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analysis.router)
app.include_router(hospitals.router)


@app.get("/")
async def root():
    return {
        "name": "HealthIntel API",
        "version": "1.0.0",
        "description": "AI-Based Medical Report Analysis and Hospital Recommendation System",
        "docs_url": "/docs",
        "endpoints": {
            "status": "/api/status",
            "disease_config": "/api/disease-config",
            "analyze_heart_failure": "/api/analyze/heart-failure",
            "analyze_alzheimer": "/api/analyze/alzheimer",
            "analyze_symptoms": "/api/analyze/symptoms",
            "analyze_eye_disease": "/api/analyze/eye-disease",
            "recommend_hospitals": "/api/recommend-hospitals",
            "symptom_list": "/api/symptoms",
        },
    }
