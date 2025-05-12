import requests
import json
import time
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api():
    # API endpoint
    url = "http://localhost:8000/api/predict"
    
    # Sample water quality data
    data = {
        "location": "Test Location 1",
        "latitude": 32.244947,
        "longitude": 77.19108,
        "temperature": 9.0,
        "do": 9.0,
        "ph": 8.0,
        "conductivity": 85,
        "bod": 0.1,
        "nitrate": 0.0,
        "fecalcaliform": 0,
        "totalcaliform": 0
    }
    
    try:
        # Make the request
        print("Making request to API...")
        print(f"Request data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data)
        
        # Print response details
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Body: {response.text}")
        
        try:
            result = response.json()
            print("\nPrediction Results:")
            print(f"Location: {result.get('location')}")
            print(f"Is Potable: {result.get('is_potable')}")
            print(f"Confidence: {result.get('confidence', 0):.2f}%")
            print("\nRecommendations:")
            for rec in result.get('recommendations', []):
                print(f"- {rec.get('parameter')}: {rec.get('recommendation')} (Priority: {rec.get('priority')})")
        except json.JSONDecodeError:
            print("\nError: Could not parse JSON response")
            
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    test_api() 