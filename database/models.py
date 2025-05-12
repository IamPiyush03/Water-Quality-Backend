from sqlalchemy import Column, Integer, Float, Boolean, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .config import Base

class WaterQualityMeasurement(Base):
    __tablename__ = "water_quality_measurements"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(String)
    Lat = Column(Float)
    Lon = Column(Float)
    Temperature = Column(Float)
    DO = Column(Float, name="D.O")
    pH = Column(Float)
    Conductivity = Column(Float)
    BOD = Column(Float, name="B.O.D")
    Nitrate = Column(Float)
    Fecalcaliform = Column(Float)
    Totalcaliform = Column(Float)
    
    # Relationship with predictions
    predictions = relationship("WaterQualityPrediction", back_populates="measurement")

class WaterQualityPrediction(Base):
    __tablename__ = "water_quality_predictions"

    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(Integer, ForeignKey("water_quality_measurements.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    is_potable = Column(Boolean)
    confidence = Column(Float)
    model_version = Column(String)
    
    # Relationship with measurement
    measurement = relationship("WaterQualityMeasurement", back_populates="predictions")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    measurement_id = Column(Integer, ForeignKey("water_quality_measurements.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    parameter = Column(String)  # e.g., "pH", "DO", etc.
    severity = Column(String)  # e.g., "mild", "moderate", "severe"
    priority = Column(String)  # e.g., "immediate", "short_term", "long_term", "preventive"
    recommendation = Column(String)
    estimated_cost = Column(Float, nullable=True)
    implementation_timeframe = Column(String, nullable=True)
    
    # Relationship with measurement
    measurement = relationship("WaterQualityMeasurement") 