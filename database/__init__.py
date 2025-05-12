from .config import Base, engine, get_db
from .models import WaterQualityMeasurement, WaterQualityPrediction, Recommendation
from .schemas import (
    WaterQualityMeasurementCreate,
    WaterQualityMeasurement as WaterQualityMeasurementSchema,
    WaterQualityPredictionCreate,
    WaterQualityPrediction as WaterQualityPredictionSchema,
    RecommendationCreate,
    Recommendation as RecommendationSchema,
    WaterQualityResponse
)
from .crud import (
    create_water_quality_measurement,
    create_prediction,
    create_recommendation,
    get_measurement,
    get_measurements,
    get_predictions_by_measurement,
    get_recommendations_by_measurement,
    get_recent_measurements,
    update_recommendation
)

# Create all tables
Base.metadata.create_all(bind=engine) 