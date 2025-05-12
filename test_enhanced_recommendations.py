from recommender.rules import WaterQualityRecommender

def test_enhanced_recommendations():
    # Initialize the recommender
    try:
        recommender = WaterQualityRecommender()
        print("\nInitialized WaterQualityRecommender successfully")
    except Exception as e:
        print(f"Error initializing recommender: {str(e)}")
        return

    # Test cases with various water quality scenarios
    test_cases = [
        {
            "name": "Severe pH and BOD Issues",
            "data": {
                "ph": 4.2,  # Critical low pH
                "d_o": 6.0,  # Normal DO
                "conductivity": 500,  # Normal conductivity
                "b_o_d": 16.0,  # Critical high BOD
                "nitrate": 5.0,  # Normal nitrate
                "fecalcaliform": 50,  # Normal fecal coliform
                "totalcaliform": 100  # Normal total coliform
            }
        },
        {
            "name": "Multiple Moderate Issues",
            "data": {
                "ph": 5.8,  # Moderate low pH
                "d_o": 3.5,  # Moderate low DO
                "conductivity": 1100,  # Moderate high conductivity
                "b_o_d": 7.0,  # Moderate high BOD
                "nitrate": 25.0,  # Moderate high nitrate
                "fecalcaliform": 300,  # Moderate high fecal coliform
                "totalcaliform": 600  # Moderate high total coliform
            }
        },
        {
            "name": "Mild Issues",
            "data": {
                "ph": 6.2,  # Mild low pH
                "d_o": 4.5,  # Mild low DO
                "conductivity": 900,  # Mild high conductivity
                "b_o_d": 4.0,  # Mild high BOD
                "nitrate": 15.0,  # Mild high nitrate
                "fecalcaliform": 150,  # Mild high fecal coliform
                "totalcaliform": 300  # Mild high total coliform
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
            traceback.print_exc()
        
        print("\n" + "="*50)

if __name__ == "__main__":
    test_enhanced_recommendations() 