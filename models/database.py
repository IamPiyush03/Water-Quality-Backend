from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class WaterQualityMeasurement(Base):
    __tablename__ = 'water_quality_measurements'
    
    id = Column(Integer, primary_key=True)
    station_code = Column(String(50))
    location = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    temperature = Column(Float)
    dissolved_oxygen = Column(Float)
    ph = Column(Float)
    conductivity = Column(Float)
    bod = Column(Float)
    nitrate = Column(Float)
    fecal_coliform = Column(Float)
    total_coliform = Column(Float)
    potability = Column(Boolean)
    timestamp = Column(DateTime, default=datetime.utcnow)
    recommendations = relationship("Recommendation", back_populates="measurement")

class Recommendation(Base):
    __tablename__ = 'recommendations'
    
    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('water_quality_measurements.id'))
    parameter = Column(String(50))
    severity = Column(String(20))
    priority = Column(String(20))
    action = Column(String(500))
    estimated_cost = Column(Float)
    implementation_time = Column(String(50))
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    measurement = relationship("WaterQualityMeasurement", back_populates="recommendations")

class ModelVersion(Base):
    __tablename__ = 'model_versions'
    
    id = Column(Integer, primary_key=True)
    version = Column(String(20))
    model_type = Column(String(50))
    performance_metrics = Column(String(500))  # JSON string of metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)

def init_db():
    """Initialize the database connection and create tables"""
    database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/water_quality')
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def add_measurement(session, data):
    """Add a new water quality measurement to the database"""
    measurement = WaterQualityMeasurement(**data)
    session.add(measurement)
    session.commit()
    return measurement

def add_recommendation(session, measurement_id, recommendation_data):
    """Add a recommendation for a measurement"""
    recommendation = Recommendation(measurement_id=measurement_id, **recommendation_data)
    session.add(recommendation)
    session.commit()
    return recommendation

def get_historical_data(session, location=None, start_date=None, end_date=None):
    """Get historical water quality data with optional filters"""
    query = session.query(WaterQualityMeasurement)
    
    if location:
        query = query.filter(WaterQualityMeasurement.location == location)
    if start_date:
        query = query.filter(WaterQualityMeasurement.timestamp >= start_date)
    if end_date:
        query = query.filter(WaterQualityMeasurement.timestamp <= end_date)
        
    return query.order_by(WaterQualityMeasurement.timestamp.desc()).all()

def get_recommendations(session, measurement_id):
    """Get all recommendations for a specific measurement"""
    return session.query(Recommendation).filter(
        Recommendation.measurement_id == measurement_id
    ).order_by(Recommendation.priority).all() 