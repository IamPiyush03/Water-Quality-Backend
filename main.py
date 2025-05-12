from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from models.predict import WaterQualityPredictor
from recommender.rules import WaterQualityRecommender
from utils.visualization import WaterQualityVisualizer
from database.config import SessionLocal
from sqlalchemy.orm import Session
import numpy as np
import joblib
import pandas as pd
from datetime import datetime

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class WaterQualityData(BaseModel):
    location: str
    latitude: float
    longitude: float
    temperature: float
    DO: float
    ph: float
    conductivity: float
    BOD: float
    nitrate: float
    fecalcaliform: int
    totalcaliform: int

app = FastAPI(
    title="Water Quality Analysis API",
    description="API for analyzing water quality and providing recommendations",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
predictor = WaterQualityPredictor()
recommender = WaterQualityRecommender()
visualizer = WaterQualityVisualizer()

# Load the trained model
model = joblib.load('models/water_quality_model.joblib')

predictor.train("data/aquaattributes.xlsx")

class WaterQualityInput(BaseModel):
    location: str
    latitude: float
    longitude: float
    temperature: float
    DO: float
    ph: float
    conductivity: float
    BOD: float
    nitrate: float
    fecalcaliform: int
    totalcaliform: int

    class Config:
        schema_extra = {
            "example": {
                "location": "River",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "temperature": 20.0,
                "DO": 6.5,
                "ph": 7.0,
                "conductivity": 500,
                "BOD": 2.0,
                "nitrate": 5.0,
                "fecalcaliform": 50,
                "totalcaliform": 100
            }
        }

class WaterQualityResponse(BaseModel):
    location: str
    latitude: float
    longitude: float
    timestamp: datetime
    temperature: float
    ph: float
    DO: float
    conductivity: float
    BOD: float
    nitrate: float
    fecalcaliform: int
    totalcaliform: int
    is_potable: bool
    confidence: float

class Recommendations(BaseModel):
    immediate: List[str]
    short_term: List[str]
    long_term: List[str]
    preventive: List[str]

    class Config:
        schema_extra = {
            "example": {
                "immediate": ["Increase aeration in treatment process"],
                "short_term": ["Install aeration system"],
                "long_term": ["Review water source and treatment process"],
                "preventive": ["Regular DO monitoring"]
            }
        }

class AnalysisResponse(BaseModel):
    potable: bool
    confidence: float
    recommendations: Optional[Recommendations] = None

    class Config:
        schema_extra = {
            "example": {
                "potable": True,
                "confidence": 0.95,
                "recommendations": None
            }
        }

@app.get("/")
async def root():
    return {"message": "Welcome to Water Quality Analysis API"}

@app.get("/api/trends/{location}")
async def get_trends(
    location: str,
    days: int = 30,
    parameter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get trend data for a specific location and parameter"""
    try:
        if parameter:
            # Get trend plot for specific parameter
            fig = visualizer.create_trend_plot(location, parameter, days)
            if not fig:
                raise HTTPException(status_code=404, detail=f"No data found for {parameter} at {location}")
            
            # Convert plot to JSON
            return fig.to_json()
        else:
            # Get dashboard with multiple parameters
            fig = visualizer.create_dashboard(location)
            if not fig:
                raise HTTPException(status_code=404, detail=f"No data found for {location}")
            
            # Convert dashboard to JSON
            return fig.to_json()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommend")
async def get_recommendations(data: WaterQualityData):
    """Get recommendations based on water quality data"""
    try:
        recommendations = recommender.generate_recommendations(data.dict())
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict")
async def predict_water_quality(data: WaterQualityData):
    """Predict water quality based on input parameters"""
    try:
        # Convert input data to feature array
        features = np.array([
            data.temperature, data.do, data.ph, data.conductivity,
            data.bod, data.nitrate, data.fecalcaliform, data.totalcaliform
        ]).reshape(1, -1)
        
        # Make prediction
        prediction = predictor.predict(features)
        confidence = predictor.get_prediction_confidence(features)
        
        return {
            "location": data.location,
            "is_potable": bool(prediction[0]),
            "confidence": float(confidence * 100),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_water_quality(input_data: WaterQualityInput):
    try:
        # Convert input to dictionary
        input_dict = input_data.dict()
        
        # Make prediction
        potable, confidence = predictor.predict(input_dict)
        
        # Generate recommendations if water is not potable
        recommendations = None
        if not potable:
            recommendations = recommender.generate_recommendations(input_dict)
        
        return {
            "potable": potable,
            "confidence": confidence,
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 