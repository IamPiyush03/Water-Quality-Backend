from sqlalchemy.orm import Session
from . import models, schemas
from typing import List, Optional
from datetime import datetime, timedelta

def create_water_quality_measurement(db: Session, measurement: schemas.WaterQualityMeasurementCreate):
    db_measurement = models.WaterQualityMeasurement(
        location=measurement.location,
        latitude=measurement.latitude,
        longitude=measurement.longitude,
        temperature=measurement.temperature,
        dissolved_oxygen=measurement.dissolved_oxygen,
        ph=measurement.ph,
        conductivity=measurement.conductivity,
        bod=measurement.bod,
        nitrate=measurement.nitrate,
        fecal_coliform=measurement.fecal_coliform,
        total_coliform=measurement.total_coliform
    )
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def create_prediction(db: Session, prediction: schemas.WaterQualityPredictionCreate):
    db_prediction = models.WaterQualityPrediction(**prediction.model_dump())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def create_recommendation(db: Session, recommendation: schemas.RecommendationCreate):
    db_recommendation = models.Recommendation(**recommendation.model_dump())
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

def get_measurement(db: Session, measurement_id: int):
    return db.query(models.WaterQualityMeasurement).filter(
        models.WaterQualityMeasurement.id == measurement_id
    ).first()

def get_measurements(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    location: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    query = db.query(models.WaterQualityMeasurement)
    
    if location:
        query = query.filter(models.WaterQualityMeasurement.location == location)
    if start_date:
        query = query.filter(models.WaterQualityMeasurement.timestamp >= start_date)
    if end_date:
        query = query.filter(models.WaterQualityMeasurement.timestamp <= end_date)
    
    return query.offset(skip).limit(limit).all()

def get_predictions_by_measurement(db: Session, measurement_id: int):
    return db.query(models.WaterQualityPrediction).filter(
        models.WaterQualityPrediction.measurement_id == measurement_id
    ).all()

def get_recommendations_by_measurement(
    db: Session,
    measurement_id: int,
    priority: Optional[str] = None
):
    query = db.query(models.Recommendation).filter(
        models.Recommendation.measurement_id == measurement_id
    )
    
    if priority:
        query = query.filter(models.Recommendation.priority == priority)
    
    return query.all()

def get_recent_measurements(
    db: Session,
    hours: int = 24,
    location: Optional[str] = None
):
    query = db.query(models.WaterQualityMeasurement).filter(
        models.WaterQualityMeasurement.timestamp >= datetime.now() - timedelta(hours=hours)
    )
    
    if location:
        query = query.filter(models.WaterQualityMeasurement.location == location)
    
    return query.all()

def update_recommendation(
    db: Session,
    recommendation_id: int,
    estimated_cost: Optional[float] = None,
    implementation_timeframe: Optional[str] = None
):
    db_recommendation = db.query(models.Recommendation).filter(
        models.Recommendation.id == recommendation_id
    ).first()
    
    if db_recommendation:
        if estimated_cost is not None:
            db_recommendation.estimated_cost = estimated_cost
        if implementation_timeframe is not None:
            db_recommendation.implementation_timeframe = implementation_timeframe
        
        db.commit()
        db.refresh(db_recommendation)
    
    return db_recommendation 