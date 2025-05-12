from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class WaterQualityMeasurementBase(BaseModel):
    location: str
    latitude: float = Field(..., alias="Lat")
    longitude: float = Field(..., alias="Lon")
    temperature: float = Field(..., alias="Temperature")
    dissolved_oxygen: float = Field(..., alias="D.O")
    ph: float = Field(..., alias="pH")
    conductivity: float = Field(..., alias="Conductivity")
    bod: float = Field(..., alias="B.O.D")
    nitrate: float = Field(..., alias="Nitrate")
    fecal_coliform: float = Field(..., alias="Fecalcaliform")
    total_coliform: float = Field(..., alias="Totalcaliform")

    class Config:
        populate_by_name = True
        from_attributes = True

class WaterQualityMeasurementCreate(WaterQualityMeasurementBase):
    pass

class WaterQualityMeasurement(WaterQualityMeasurementBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True
        populate_by_name = True

class WaterQualityPredictionBase(BaseModel):
    is_potable: bool
    confidence: float
    model_version: str

class WaterQualityPredictionCreate(WaterQualityPredictionBase):
    measurement_id: int

class WaterQualityPrediction(WaterQualityPredictionBase):
    id: int
    measurement_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class RecommendationBase(BaseModel):
    parameter: str
    severity: str
    priority: str
    recommendation: str
    estimated_cost: Optional[float] = None
    implementation_timeframe: Optional[str] = None

class RecommendationCreate(RecommendationBase):
    measurement_id: int

class Recommendation(RecommendationBase):
    id: int
    measurement_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

# Combined response models
class WaterQualityResponse(BaseModel):
    measurement: WaterQualityMeasurement
    prediction: WaterQualityPrediction
    recommendations: List[Recommendation]
    
    class Config:
        from_attributes = True
        populate_by_name = True 