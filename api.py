from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi import Request
from pydantic import BaseModel, Field
from models.predict import WaterQualityPredictor
from database import (
    get_db,
    create_water_quality_measurement,
    create_prediction,
    create_recommendation,
    get_measurement,
    get_predictions_by_measurement,
    get_recommendations_by_measurement,
    WaterQualityResponse,
    WaterQualityMeasurementCreate,
    WaterQualityPredictionCreate,
    RecommendationCreate
)
from sqlalchemy.orm import Session
import uvicorn
import os
from dotenv import load_dotenv
from utils.trend_analysis import WaterQualityTrendAnalyzer
from utils.dashboard import WaterQualityDashboard
import io

# Load environment variables
load_dotenv()

# Create necessary directories
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Initialize and train the model
print("Training model...")
predictor = WaterQualityPredictor()
predictor.train('data/aquaattributes.xlsx')

app = FastAPI(title="Water Quality Prediction API")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Initialize trend analyzer and dashboard
trend_analyzer = WaterQualityTrendAnalyzer(get_db())
dashboard = WaterQualityDashboard(get_db())

class WaterQualityInput(BaseModel):
    location: str = Field(..., description="Location name")
    Lat: float = Field(..., description="Latitude")
    Lon: float = Field(..., description="Longitude")
    Temperature: float = Field(..., description="Temperature in Celsius")
    D_O: float = Field(..., alias="D.O", description="Dissolved Oxygen")
    pH: float = Field(..., description="pH value")
    Conductivity: float = Field(..., description="Conductivity")
    B_O_D: float = Field(..., alias="B.O.D", description="Biochemical Oxygen Demand")
    Nitrate: float = Field(..., description="Nitrate concentration")
    Fecalcaliform: float = Field(..., description="Fecal Coliform count")
    Totalcaliform: float = Field(..., description="Total Coliform count")

    class Config:
        populate_by_name = True

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict_water_quality(
    data: WaterQualityInput,
    db: Session = Depends(get_db)
) -> WaterQualityResponse:
    try:
        # Convert input data to match model features
        model_input = {
            'Lat': float(data.Lat),
            'Lon': float(data.Lon),
            'Temperature': float(data.Temperature),
            'D.O': float(data.D_O),
            'pH': float(data.pH),
            'Conductivity': float(data.Conductivity),
            'B.O.D': float(data.B_O_D),
            'Nitrate': float(data.Nitrate),
            'Fecalcaliform': float(data.Fecalcaliform),
            'Totalcaliform': float(data.Totalcaliform)
        }
        
        # Make prediction
        is_potable, probability = predictor.predict(model_input)
        
        # Create measurement record with proper field mapping
        measurement_data = WaterQualityMeasurementCreate(
            location=data.location,
            Lat=data.Lat,
            Lon=data.Lon,
            Temperature=data.Temperature,
            **{"D.O": data.D_O},
            pH=data.pH,
            Conductivity=data.Conductivity,
            **{"B.O.D": data.B_O_D},
            Nitrate=data.Nitrate,
            Fecalcaliform=data.Fecalcaliform,
            Totalcaliform=data.Totalcaliform
        )
        
        # Create the measurement in the database
        measurement = create_water_quality_measurement(db, measurement_data)
        
        # Create prediction record
        prediction_data = WaterQualityPredictionCreate(
            measurement_id=measurement.id,
            is_potable=is_potable,
            confidence=probability,
            model_version=os.getenv("MODEL_VERSION", "v1.0.0")
        )
        prediction = create_prediction(db, prediction_data)
        
        # Generate recommendations
        recommendations = []
        if not is_potable:
            # Add recommendations based on parameter values
            for param, value in model_input.items():
                if param == 'pH' and (value < 6.5 or value > 8.5):
                    recommendation_data = RecommendationCreate(
                        measurement_id=measurement.id,
                        parameter="pH",
                        severity="moderate" if 6.0 <= value <= 9.0 else "severe",
                        priority="immediate",
                        recommendation="Add calcium carbonate to adjust pH levels" if value < 7.0 else "Add acid to reduce pH",
                        estimated_cost=100.0,
                        implementation_timeframe="1-2 hours"
                    )
                    recommendation = create_recommendation(db, recommendation_data)
                    recommendations.append(recommendation)
                elif param == 'D.O' and value < 5.0:
                    recommendation_data = RecommendationCreate(
                        measurement_id=measurement.id,
                        parameter="Dissolved Oxygen",
                        severity="moderate" if value >= 4.0 else "severe",
                        priority="immediate",
                        recommendation="Increase aeration or use oxygen injection",
                        estimated_cost=200.0,
                        implementation_timeframe="2-4 hours"
                    )
                    recommendation = create_recommendation(db, recommendation_data)
                    recommendations.append(recommendation)
        
        # Create the response
        response = WaterQualityResponse(
            measurement=measurement,
            prediction=prediction,
            recommendations=recommendations
        )
        
        return response
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/measurements/{measurement_id}")
async def get_measurement_details(
    measurement_id: int,
    db: Session = Depends(get_db)
) -> WaterQualityResponse:
    measurement = get_measurement(db, measurement_id)
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    
    predictions = get_predictions_by_measurement(db, measurement_id)
    if not predictions:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    recommendations = get_recommendations_by_measurement(db, measurement_id)
    
    return WaterQualityResponse(
        measurement=measurement,
        prediction=predictions[0],  # Assuming one prediction per measurement
        recommendations=recommendations
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/trends/{location}")
async def get_trends(location: str, days: int = 30):
    """Get trend analysis for a specific location"""
    try:
        report = trend_analyzer.generate_report(location, days)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/{location}")
async def get_dashboard(location: str, days: int = 30):
    """Get dashboard for a specific location"""
    try:
        dashboard_data = dashboard.create_overview_dashboard(location, days)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/{location}/parameter/{parameter}")
async def get_parameter_dashboard(location: str, parameter: str, days: int = 30):
    """Get detailed dashboard for a specific parameter at a location"""
    try:
        dashboard_data = dashboard.create_parameter_dashboard(location, parameter, days)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/compare")
async def get_comparison_dashboard(locations: str, days: int = 30):
    """Get comparison dashboard for multiple locations"""
    try:
        location_list = locations.split(',')
        dashboard_data = dashboard.create_comparison_dashboard(location_list, days)
        return dashboard_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export/{location}")
async def export_data(location: str, days: int = 30, format: str = 'csv'):
    """Export water quality data for a location"""
    try:
        df = trend_analyzer.get_historical_data(location, days)
        data = trend_analyzer.export_data(df, format)
        
        if format.lower() == 'csv':
            return StreamingResponse(
                io.BytesIO(data),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment;filename={location}_water_quality.csv"}
            )
        elif format.lower() == 'excel':
            return StreamingResponse(
                io.BytesIO(data),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment;filename={location}_water_quality.xlsx"}
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Get port from environment variable
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port) 