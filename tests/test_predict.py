import pytest
from models.predict import WaterQualityPredictor

def test_predictor_initialization():
    predictor = WaterQualityPredictor()
    assert predictor.model is None
    assert predictor.model_path == "models/water_quality_model.joblib"

def test_predictor_load_model_nonexistent():
    predictor = WaterQualityPredictor("nonexistent_model.joblib")
    assert not predictor.load_model()

def test_predictor_predict_without_model():
    predictor = WaterQualityPredictor()
    with pytest.raises(ValueError):
        predictor.predict({
            "ph": 7.0,
            "hardness": 100,
            "solids": 500,
            "chloramines": 2.0,
            "sulfate": 200,
            "conductivity": 400,
            "organic_carbon": 1.0,
            "trihalomethanes": 0.05,
            "turbidity": 2.0
        }) 