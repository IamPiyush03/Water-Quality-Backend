from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score
from sklearn.metrics import classification_report, roc_auc_score
import pandas as pd
import numpy as np
from datetime import datetime
import json
from joblib import dump, load
import os
from .database import ModelVersion, init_db

class ModelManager:
    def __init__(self, model_dir="models"):
        self.model_dir = model_dir
        self.session = init_db()
        self.current_model = None
        self.current_version = None
        
    def train_new_version(self, data_path, model_type="random_forest"):
        """Train a new model version and save it"""
        # Load and prepare data
        df = pd.read_excel(data_path)
        X = df.drop(['Potability', 'Stationcode', 'Locations', 'Capitalcity', 'State'], axis=1)
        y = df['Potability']
        
        # Initialize model based on type
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=5,
                min_samples_split=10,
                min_samples_leaf=2,
                random_state=42
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=3,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == "svm":
            model = SVC(
                kernel='rbf',
                probability=True,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Perform cross-validation
        cv_scores = cross_val_score(model, X, y, cv=5, scoring='roc_auc')
        mean_cv_score = cv_scores.mean()
        std_cv_score = cv_scores.std()
        
        # Train final model
        model.fit(X, y)
        
        # Generate version number
        version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Save model
        os.makedirs(self.model_dir, exist_ok=True)
        model_path = os.path.join(self.model_dir, f"model_{version}.joblib")
        dump(model, model_path)
        
        # Create model version record
        metrics = {
            "cv_mean_roc_auc": mean_cv_score,
            "cv_std_roc_auc": std_cv_score,
            "training_date": datetime.now().isoformat()
        }
        
        model_version = ModelVersion(
            version=version,
            model_type=model_type,
            performance_metrics=json.dumps(metrics),
            is_active=False
        )
        
        self.session.add(model_version)
        self.session.commit()
        
        return version, metrics
    
    def activate_version(self, version):
        """Activate a specific model version"""
        # Deactivate current active version
        self.session.query(ModelVersion).filter(
            ModelVersion.is_active == True
        ).update({"is_active": False})
        
        # Activate new version
        model_version = self.session.query(ModelVersion).filter(
            ModelVersion.version == version
        ).first()
        
        if model_version:
            model_version.is_active = True
            self.session.commit()
            
            # Load the model
            model_path = os.path.join(self.model_dir, f"model_{version}.joblib")
            self.current_model = load(model_path)
            self.current_version = version
            
            return True
        return False
    
    def get_active_model(self):
        """Get the currently active model"""
        if not self.current_model:
            active_version = self.session.query(ModelVersion).filter(
                ModelVersion.is_active == True
            ).first()
            
            if active_version:
                model_path = os.path.join(self.model_dir, f"model_{active_version.version}.joblib")
                self.current_model = load(model_path)
                self.current_version = active_version.version
        
        return self.current_model
    
    def predict(self, data):
        """Make predictions using the active model"""
        model = self.get_active_model()
        if not model:
            raise ValueError("No active model found")
        
        return model.predict(data)
    
    def predict_proba(self, data):
        """Get prediction probabilities using the active model"""
        model = self.get_active_model()
        if not model:
            raise ValueError("No active model found")
        
        return model.predict_proba(data)
    
    def get_model_versions(self):
        """Get all model versions with their performance metrics"""
        versions = self.session.query(ModelVersion).all()
        return [
            {
                "version": v.version,
                "model_type": v.model_type,
                "performance_metrics": json.loads(v.performance_metrics),
                "is_active": v.is_active,
                "created_at": v.created_at.isoformat()
            }
            for v in versions
        ]
    
    def compare_versions(self, version1, version2):
        """Compare performance metrics of two model versions"""
        v1 = self.session.query(ModelVersion).filter(
            ModelVersion.version == version1
        ).first()
        
        v2 = self.session.query(ModelVersion).filter(
            ModelVersion.version == version2
        ).first()
        
        if not v1 or not v2:
            raise ValueError("One or both versions not found")
        
        metrics1 = json.loads(v1.performance_metrics)
        metrics2 = json.loads(v2.performance_metrics)
        
        comparison = {
            "version1": {
                "version": v1.version,
                "model_type": v1.model_type,
                "metrics": metrics1
            },
            "version2": {
                "version": v2.version,
                "model_type": v2.model_type,
                "metrics": metrics2
            },
            "differences": {
                k: metrics2[k] - metrics1[k]
                for k in metrics1.keys()
                if isinstance(metrics1[k], (int, float))
            }
        }
        
        return comparison 