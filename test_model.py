from models.predict import WaterQualityPredictor
import pandas as pd

def test_model():
    # Initialize predictor
    predictor = WaterQualityPredictor()
    
    # Load sample data
    print("Loading sample data...")
    df = pd.read_excel('data/aquaattributes.xlsx')
    
    # Train model if not already trained
    print("\nTraining model...")
    predictor.train('data/aquaattributes.xlsx')
    
    # Get first row as sample
    sample = df.iloc[0].to_dict()
    
    # Remove non-numeric columns
    columns_to_remove = ['Stationcode', 'Locations', 'Capitalcity', 'State', 'Potability']
    for col in columns_to_remove:
        if col in sample:
            del sample[col]
    
    # Make prediction
    print("\nMaking prediction for sample data:")
    print("Input parameters:")
    for key, value in sample.items():
        print(f"{key}: {value}")
    
    try:
        is_potable, probability = predictor.predict(sample)
        print(f"\nPrediction Result:")
        print(f"Is Potable: {'Yes' if is_potable else 'No'}")
        print(f"Confidence: {probability:.2%}")
    except Exception as e:
        print(f"\nError making prediction: {str(e)}")

if __name__ == "__main__":
    test_model() 