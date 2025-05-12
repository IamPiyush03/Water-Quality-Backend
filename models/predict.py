import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from joblib import dump, load
import os
import matplotlib.pyplot as plt
import seaborn as sns

class WaterQualityPredictor:
    def __init__(self, model_path: str = None):
        self.model = None
        self.scaler = None
        self.label_encoder = None
        self.model_path = model_path or "models/water_quality_model.joblib"
        self.scaler_path = model_path.replace('.joblib', '_scaler.joblib') if model_path else "models/water_quality_scaler.joblib"
        self.encoder_path = model_path.replace('.joblib', '_encoder.joblib') if model_path else "models/water_quality_encoder.joblib"
        self.feature_columns = None
        self.target_column = None
        
    def train(self, data_path: str):
        """Train the model using the provided dataset"""
        try:
            # Load and prepare data
            print(f"Loading data from {data_path}...")
            df = pd.read_excel(data_path)
            print(f"Available columns: {df.columns.tolist()}")
            
            # Look for potability column with case-insensitive match
            self.target_column = None
            for col in df.columns:
                if col.lower() == 'potability':
                    self.target_column = col
                    break
            
            if self.target_column is None:
                raise ValueError("Could not find 'Potability' column in dataset")
            
            # Drop non-numeric columns that aren't relevant for prediction
            columns_to_drop = ['Stationcode', 'Locations', 'Capitalcity', 'State']
            df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
            
            # Convert remaining columns to numeric, replacing non-numeric values with NaN
            for col in df.columns:
                if col != self.target_column:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Drop rows with NaN values
            df = df.dropna()
            
            # Prepare features and target
            X = df.drop([self.target_column], axis=1)
            y = df[self.target_column]
            
            # Encode target variable
            self.label_encoder = LabelEncoder()
            y_encoded = self.label_encoder.fit_transform(y)
            
            # Store feature columns for later use in prediction
            self.feature_columns = X.columns.tolist()
            
            print(f"\nFeatures after preprocessing: {self.feature_columns}")
            print(f"Target column: {self.target_column}")
            print(f"Number of samples after preprocessing: {len(df)}")
            
            # Analyze class distribution
            print("\nClass distribution:")
            print(y.value_counts(normalize=True))
            
            # Visualize feature distributions
            self._plot_feature_distributions(X, y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded)
            print(f"\nTraining set size: {len(X_train)}")
            print(f"Test set size: {len(X_test)}")
            
            # Scale features
            self.scaler = StandardScaler()
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Calculate class weights
            class_weights = dict(zip(np.unique(y_encoded), len(y_encoded) / (2 * np.bincount(y_encoded))))
            print(f"\nClass weights: {class_weights}")
            
            # Define parameter grid for grid search
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, 15],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'class_weight': [None, 'balanced', class_weights]
            }
            
            # Initialize base model
            base_model = RandomForestClassifier(random_state=42)
            
            # Perform grid search
            print("\nPerforming grid search...")
            grid_search = GridSearchCV(
                estimator=base_model,
                param_grid=param_grid,
                cv=5,
                scoring='roc_auc',
                n_jobs=-1,
                verbose=1
            )
            grid_search.fit(X_train_scaled, y_train)
            
            # Get best model
            self.model = grid_search.best_estimator_
            print(f"\nBest parameters: {grid_search.best_params_}")
            
            # Perform cross-validation with best model
            cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
            print(f"\nCross-validation ROC-AUC scores: {cv_scores}")
            print(f"Mean CV ROC-AUC: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")
            
            # Evaluate on test set
            y_pred = self.model.predict(X_test_scaled)
            y_prob = self.model.predict_proba(X_test_scaled)[:, 1]
            
            print("\nClassification Report:")
            print(classification_report(y_test, y_pred, target_names=self.label_encoder.classes_))
            
            print(f"\nROC-AUC Score: {roc_auc_score(y_test, y_prob):.2%}")
            
            # Plot confusion matrix
            self._plot_confusion_matrix(y_test, y_pred)
            
            # Analyze feature importance
            self._plot_feature_importance(X)
            
            # Save model, scaler, and encoder
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            dump(self.model, self.model_path)
            dump(self.scaler, self.scaler_path)
            dump(self.label_encoder, self.encoder_path)
            
            return cv_scores.mean()
            
        except Exception as e:
            print(f"Error during training: {str(e)}")
            return None
    
    def _plot_feature_distributions(self, X, y):
        """Plot distributions of features for each class"""
        plt.figure(figsize=(15, 10))
        for i, feature in enumerate(X.columns):
            plt.subplot(3, 4, i+1)
            sns.boxplot(x=y, y=X[feature])
            plt.title(feature)
        plt.tight_layout()
        plt.savefig('feature_distributions.png')
        plt.close()
    
    def _plot_confusion_matrix(self, y_true, y_pred):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=self.label_encoder.classes_,
                   yticklabels=self.label_encoder.classes_)
        plt.title('Confusion Matrix')
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.savefig('confusion_matrix.png')
        plt.close()
    
    def _plot_feature_importance(self, X):
        """Plot feature importance"""
        importance = pd.Series(self.model.feature_importances_, index=X.columns)
        importance = importance.sort_values(ascending=False)
        plt.figure(figsize=(10, 6))
        sns.barplot(x=importance.values, y=importance.index)
        plt.title('Feature Importance')
        plt.tight_layout()
        plt.savefig('feature_importance.png')
        plt.close()
    
    def load_model(self):
        """Load the trained model, scaler, and encoder"""
        if all(os.path.exists(path) for path in [self.model_path, self.scaler_path, self.encoder_path]):
            try:
                self.model = load(self.model_path)
                self.scaler = load(self.scaler_path)
                self.label_encoder = load(self.encoder_path)
                return True
            except Exception as e:
                print(f"Error loading model: {e}")
                return False
        return False
    
    def predict(self, input_data: dict) -> tuple[bool, float]:
        """Make prediction for new input data"""
        try:
            if self.model is None and not self.load_model():
                raise ValueError("Model not trained or loaded")
            
            if self.feature_columns is None:
                raise ValueError("Model not properly trained - feature columns not available")
                
            # Convert input to DataFrame with correct column order
            input_df = pd.DataFrame([input_data], columns=self.feature_columns)
            
            # Scale features
            input_scaled = self.scaler.transform(input_df)
            
            # Make prediction
            prediction = self.model.predict(input_scaled)[0]
            probability = self.model.predict_proba(input_scaled)[0][1]
            
            # Convert prediction back to original label
            prediction_label = self.label_encoder.inverse_transform([prediction])[0]
            
            return bool(prediction_label == 'yes'), float(probability)
        except Exception as e:
            print(f"Error during prediction: {e}")
            raise 