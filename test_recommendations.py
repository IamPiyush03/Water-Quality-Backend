import requests
import json

def test_recommendations():
    # API endpoint
    url = "http://localhost:8000/predict"
    
    # Test cases
    test_cases = [
        {
            "name": "Severe Issues",
            "data": {
                "location": "Test Location 1",
                "Lat": 32.244947,
                "Lon": 77.19108,
                "Temperature": 9.0,
                "D.O": 2.0,  # Low DO
                "pH": 4.0,  # Low pH
                "Conductivity": 2000,  # High conductivity
                "B.O.D": 15.0,  # High BOD
                "Nitrate": 20.0,  # High nitrate
                "Fecalcaliform": 500,  # High fecal coliform
                "Totalcaliform": 1000  # High total coliform
            }
        },
        {
            "name": "Moderate Issues",
            "data": {
                "location": "Test Location 2",
                "Lat": 32.244947,
                "Lon": 77.19108,
                "Temperature": 9.0,
                "D.O": 4.0,
                "pH": 6.0,
                "Conductivity": 1000,
                "B.O.D": 8.0,
                "Nitrate": 15.0,
                "Fecalcaliform": 200,
                "Totalcaliform": 400
            }
        },
        {
            "name": "Mild Issues",
            "data": {
                "location": "Test Location 3",
                "Lat": 32.244947,
                "Lon": 77.19108,
                "Temperature": 9.0,
                "D.O": 6.0,
                "pH": 6.2,
                "Conductivity": 900,
                "B.O.D": 5.0,
                "Nitrate": 12.0,
                "Fecalcaliform": 150,
                "Totalcaliform": 300
            }
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        print(f"Request data: {json.dumps(test['data'], indent=2)}")
        
        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=test['data'], headers=headers)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("\nPrediction Results:")
                    print(f"Location: {result['measurement']['location']}")
                    print(f"Is Potable: {result['prediction']['is_potable']}")
                    print(f"Confidence: {result['prediction']['confidence']:.2f}%")
                    
                    if result['recommendations']:
                        print("\nRecommendations:")
                        for rec in result['recommendations']:
                            print(f"\n{rec['priority'].upper()} - {rec['parameter']} ({rec['severity']}):")
                            print(f"- {rec['recommendation']}")
                            print(f"  Estimated Cost: ${rec['estimated_cost']:.2f}")
                            print(f"  Implementation Time: {rec['implementation_timeframe']}")
                except json.JSONDecodeError:
                    print("Error: Could not parse JSON response")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    test_recommendations() 