from models.predict import WaterQualityPredictor
import os

def main():
    # Initialize predictor
    predictor = WaterQualityPredictor()
    
    # Train model
    print("Training model...")
    accuracy = predictor.train("data/aquaattributes.xlsx")
    
    if accuracy is not None:
        print(f"Model trained successfully with accuracy: {accuracy:.2%}")
        print(f"Model saved to: {predictor.model_path}")
    else:
        print("Model training failed!")

if __name__ == "__main__":
    main() 