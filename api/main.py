from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.predict import WaterQualityPredictor
from recommender.rules import WaterQualityRecommender
from database.models import WaterQualityMeasurement, WaterQualityPrediction, Recommendation
from database.config import SessionLocal, engine
from sqlalchemy.orm import Session

app = FastAPI()

# Create database tables
WaterQualityMeasurement.metadata.create_all(bind=engine)

# Initialize models
predictor = WaterQualityPredictor()
recommender = WaterQualityRecommender()

class WaterQualityRequest(BaseModel):
    location: str
    Lat: float
    Lon: float
    Temperature: float
    DO: float
    pH: float
    Conductivity: float
    BOD: float
    Nitrate: float
    Fecalcaliform: float
    Totalcaliform: float

class WaterQualityResponse(BaseModel):
    location: str
    is_potable: bool
    confidence: float
    recommendations: List[dict]

@app.post("/predict", response_model=WaterQualityResponse)
async def predict_water_quality(request: WaterQualityRequest):
    try:
        # Create database session
        db = SessionLocal()
        
        # Create measurement record
        measurement = WaterQualityMeasurement(
            location=request.location,
            Lat=request.Lat,
            Lon=request.Lon,
            Temperature=request.Temperature,
            DO=request.DO,
            pH=request.pH,
            Conductivity=request.Conductivity,
            BOD=request.BOD,
            Nitrate=request.Nitrate,
            Fecalcaliform=request.Fecalcaliform,
            Totalcaliform=request.Totalcaliform
        )
        db.add(measurement)
        db.commit()
        db.refresh(measurement)
        
        # Make prediction
        prediction = predictor.predict({
            "Lat": request.Lat,
            "Lon": request.Lon,
            "Temperature": request.Temperature,
            "DO": request.DO,
            "pH": request.pH,
            "Conductivity": request.Conductivity,
            "BOD": request.BOD,
            "Nitrate": request.Nitrate,
            "Fecalcaliform": request.Fecalcaliform,
            "Totalcaliform": request.Totalcaliform
        })
        
        # Create prediction record
        prediction_record = WaterQualityPrediction(
            measurement_id=measurement.id,
            is_potable=prediction["is_potable"],
            confidence=prediction["confidence"],
            model_version="1.0"
        )
        db.add(prediction_record)
        
        # Generate recommendations
        recommendations = recommender.generate_recommendations({
            "pH": request.pH,
            "DO": request.DO,
            "Conductivity": request.Conductivity,
            "BOD": request.BOD,
            "Nitrate": request.Nitrate,
            "Fecalcaliform": request.Fecalcaliform,
            "Totalcaliform": request.Totalcaliform
        })
        
        # Create recommendation records
        for rec in recommendations:
            recommendation = Recommendation(
                measurement_id=measurement.id,
                parameter=rec["parameter"],
                severity=rec["severity"],
                priority=rec["priority"],
                recommendation=rec["recommendation"]
            )
            db.add(recommendation)
        
        db.commit()
        
        return WaterQualityResponse(
            location=request.location,
            is_potable=prediction["is_potable"],
            confidence=prediction["confidence"],
            recommendations=recommendations
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 