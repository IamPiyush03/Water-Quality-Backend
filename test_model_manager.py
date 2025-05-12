from models.model_manager import ModelManager
import pandas as pd
import numpy as np

def test_model_manager():
    # Initialize model manager
    manager = ModelManager()
    
    # Test training different model types
    print("\n1. Training Different Model Types")
    print("-" * 50)
    
    # Train Random Forest
    rf_version, rf_metrics = manager.train_new_version(
        "data/aquaattributes.xlsx",
        model_type="random_forest"
    )
    print(f"Random Forest Version: {rf_version}")
    print(f"Performance Metrics: {rf_metrics}")
    
    # Train Gradient Boosting
    gb_version, gb_metrics = manager.train_new_version(
        "data/aquaattributes.xlsx",
        model_type="gradient_boosting"
    )
    print(f"\nGradient Boosting Version: {gb_version}")
    print(f"Performance Metrics: {gb_metrics}")
    
    # Train SVM
    svm_version, svm_metrics = manager.train_new_version(
        "data/aquaattributes.xlsx",
        model_type="svm"
    )
    print(f"\nSVM Version: {svm_version}")
    print(f"Performance Metrics: {svm_metrics}")
    
    # Test version activation
    print("\n2. Version Activation")
    print("-" * 50)
    manager.activate_version(rf_version)
    print(f"Activated Random Forest version: {rf_version}")
    
    # Test prediction
    print("\n3. Making Predictions")
    print("-" * 50)
    # Create sample data
    sample_data = pd.DataFrame({
        'Temperature': [25.0],
        'Dissolved Oxygen': [7.5],
        'pH': [7.0],
        'Conductivity': [500],
        'BOD': [2.0],
        'Nitrate': [5.0],
        'Fecal Coliform': [50],
        'Total Coliform': [100]
    })
    
    predictions = manager.predict(sample_data)
    probabilities = manager.predict_proba(sample_data)
    print(f"Predictions: {predictions}")
    print(f"Probabilities: {probabilities}")
    
    # Test version comparison
    print("\n4. Version Comparison")
    print("-" * 50)
    comparison = manager.compare_versions(rf_version, gb_version)
    print(f"Comparison between {rf_version} and {gb_version}:")
    print(f"Performance differences: {comparison['differences']}")
    
    # List all versions
    print("\n5. All Model Versions")
    print("-" * 50)
    versions = manager.get_model_versions()
    for v in versions:
        print(f"\nVersion: {v['version']}")
        print(f"Type: {v['model_type']}")
        print(f"Active: {v['is_active']}")
        print(f"Metrics: {v['performance_metrics']}")

if __name__ == "__main__":
    test_model_manager() 