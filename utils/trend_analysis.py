import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import WaterQualityMeasurement
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

class WaterQualityTrendAnalyzer:
    def __init__(self, db: Session):
        self.db = db

    def get_historical_data(self, location: str, days: int = 30) -> pd.DataFrame:
        """Get historical water quality data for a specific location"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        measurements = self.db.query(WaterQualityMeasurement).filter(
            WaterQualityMeasurement.location == location,
            WaterQualityMeasurement.timestamp >= start_date,
            WaterQualityMeasurement.timestamp <= end_date
        ).all()
        
        data = []
        for m in measurements:
            data.append({
                'timestamp': m.timestamp,
                'ph': m.ph,
                'DO': m.DO,
                'conductivity': m.conductivity,
                'BOD': m.BOD,
                'nitrate': m.nitrate,
                'fecalcaliform': m.fecalcaliform,
                'totalcaliform': m.totalcaliform,
                'is_potable': m.is_potable
            })
        
        return pd.DataFrame(data)

    def analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze trends in water quality parameters"""
        trends = {}
        
        for column in df.columns:
            if column not in ['timestamp', 'is_potable']:
                # Calculate basic statistics
                stats = {
                    'mean': df[column].mean(),
                    'std': df[column].std(),
                    'min': df[column].min(),
                    'max': df[column].max(),
                    'trend': self._calculate_trend(df[column])
                }
                trends[column] = stats
        
        return trends

    def _calculate_trend(self, series: pd.Series) -> str:
        """Calculate trend direction and strength"""
        if len(series) < 2:
            return "insufficient data"
        
        # Calculate linear regression
        x = np.arange(len(series))
        slope, _ = np.polyfit(x, series, 1)
        
        if abs(slope) < 0.1:
            return "stable"
        elif slope > 0:
            return "increasing"
        else:
            return "decreasing"

    def generate_trend_plot(self, df: pd.DataFrame, parameter: str) -> str:
        """Generate a trend plot for a specific parameter"""
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df, x='timestamp', y=parameter)
        plt.title(f'{parameter} Trend Over Time')
        plt.xlabel('Date')
        plt.ylabel(parameter)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save plot to bytes
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close()
        
        # Convert to base64
        return base64.b64encode(buffer.getvalue()).decode()

    def export_data(self, df: pd.DataFrame, format: str = 'csv') -> bytes:
        """Export data in specified format"""
        if format.lower() == 'csv':
            return df.to_csv(index=False).encode()
        elif format.lower() == 'excel':
            buffer = BytesIO()
            df.to_excel(buffer, index=False)
            return buffer.getvalue()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def generate_report(self, location: str, days: int = 30) -> Dict:
        """Generate a comprehensive report with trends and visualizations"""
        df = self.get_historical_data(location, days)
        trends = self.analyze_trends(df)
        
        report = {
            'location': location,
            'period': f'Last {days} days',
            'trends': trends,
            'plots': {}
        }
        
        # Generate plots for each parameter
        for parameter in trends.keys():
            report['plots'][parameter] = self.generate_trend_plot(df, parameter)
        
        return report 