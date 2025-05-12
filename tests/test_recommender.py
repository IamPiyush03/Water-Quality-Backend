import pytest
from recommender.rules import WaterQualityRecommender

def test_recommender_initialization():
    recommender = WaterQualityRecommender()
    assert recommender.guidelines is not None
    assert "ph" in recommender.guidelines
    assert "range" in recommender.guidelines["ph"]
    assert "measures" in recommender.guidelines["ph"]

def test_generate_recommendations():
    recommender = WaterQualityRecommender()
    
    # Test with pH below range
    recommendations = recommender.generate_recommendations({"ph": 5.0})
    assert any("calcium carbonate" in rec.lower() for rec in recommendations)
    
    # Test with pH above range
    recommendations = recommender.generate_recommendations({"ph": 9.0})
    assert any("acid dosing" in rec.lower() for rec in recommendations)
    
    # Test with multiple parameters
    recommendations = recommender.generate_recommendations({
        "ph": 9.0,
        "hardness": 150,
        "conductivity": 1000
    })
    assert len(recommendations) >= 3  # Should have recommendations for all out-of-range parameters

def test_generate_recommendations_with_valid_values():
    recommender = WaterQualityRecommender()
    recommendations = recommender.generate_recommendations({
        "ph": 7.0,
        "hardness": 100,
        "conductivity": 400
    })
    assert len(recommendations) == 0  # No recommendations for values within range 