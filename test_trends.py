import requests
import json

def test_trends():
    # API endpoint
    base_url = "http://localhost:8000"
    
    # Test cases
    test_cases = [
        {
            "name": "Test Location 1 - All Parameters",
            "endpoint": f"{base_url}/api/trends/Test%20Location%201"
        },
        {
            "name": "Test Location 1 - pH Only",
            "endpoint": f"{base_url}/api/trends/Test%20Location%201?parameter=ph"
        },
        {
            "name": "Test Location 1 - Last 7 Days",
            "endpoint": f"{base_url}/api/trends/Test%20Location%201?days=7"
        }
    ]
    
    for test in test_cases:
        print(f"\nTesting: {test['name']}")
        print(f"Endpoint: {test['endpoint']}")
        
        try:
            response = requests.get(test['endpoint'])
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {response.headers}")
            
            if response.status_code == 200:
                try:
                    result = response.json()
                    print("Successfully received trend data")
                except json.JSONDecodeError:
                    print("Error: Could not parse JSON response")
            else:
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"Error making request: {str(e)}")

if __name__ == "__main__":
    test_trends() 