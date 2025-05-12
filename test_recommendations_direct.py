from recommender.rules import WaterQualityRecommender
import sys

def test_recommendations():
    # Initialize the recommender
    try:
        recommender = WaterQualityRecommender()
        print("\nInitialized WaterQualityRecommender successfully")
    except Exception as e:
        print(f"Error initializing recommender: {str(e)}")
        return

    # Test data with various water quality issues
    test_cases = [
        {
            "name": "Low pH and High BOD",
            "data": {
                "ph": 5.0,
                "d_o": 6.0,
                "conductivity": 500,
                "b_o_d": 8.0,
                "nitrate": 5.0,
                "fecalcaliform": 50,
                "totalcaliform": 100
            }
        },
        {
            "name": "High Nitrate and Fecal Coliform",
            "data": {
                "ph": 7.0,
                "d_o": 6.0,
                "conductivity": 500,
                "b_o_d": 2.0,
                "nitrate": 25.0,
                "fecalcaliform": 300,
                "totalcaliform": 500
            }
        },
        {
            "name": "Multiple Issues (Severe)",
            "data": {
                "ph": 4.5,
                "d_o": 3.0,
                "conductivity": 1200,
                "b_o_d": 15.0,
                "nitrate": 30.0,
                "fecalcaliform": 800,
                "totalcaliform": 1000
            }
        }
    ]

    print("\nAvailable parameters in guidelines:")
    for param in recommender.guidelines.keys():
        print(f"  - {param}")
    print("\nStarting tests...\n" + "="*50)

    for test_case in test_cases:
        print(f"\nTest Case: {test_case['name']}")
        print("-"*30)
        
        try:
            print(f"\nInput values:")
            for param, value in test_case["data"].items():
                print(f"  {param}: {value}")
            
            # Generate recommendations
            recommendations = recommender.generate_recommendations(test_case["data"])
            
            if not any(recommendations.values()):
                print("\nNo recommendations needed - all parameters within acceptable ranges.")
                continue
                
            print("\nRecommendations by Priority:")
            
            for priority in ["immediate", "short_term", "long_term", "preventive"]:
                if recommendations[priority]:
                    print(f"\n{priority.replace('_', ' ').title()} Actions:")
                    for action in recommendations[priority]:
                        print(f"  - {action}")
            
        except Exception as e:
            print(f"\nError processing test case: {str(e)}")
            import traceback
            traceback.print_exc(file=sys.stdout)
        
        print("\n" + "="*50)

if __name__ == "__main__":
    test_recommendations() 