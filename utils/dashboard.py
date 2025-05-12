import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database.models import WaterQualityMeasurement
from typing import Dict, List
import json

class WaterQualityDashboard:
    def __init__(self, db: Session):
        self.db = db

    def create_overview_dashboard(self, location: str, days: int = 30) -> Dict:
        """Create an overview dashboard with multiple visualizations"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        measurements = self.db.query(WaterQualityMeasurement).filter(
            WaterQualityMeasurement.location == location,
            WaterQualityMeasurement.timestamp >= start_date,
            WaterQualityMeasurement.timestamp <= end_date
        ).all()
        
        # Convert to DataFrame
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
        df = pd.DataFrame(data)
        
        # Create subplots
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=('pH', 'Dissolved Oxygen', 'Conductivity',
                          'BOD', 'Nitrate', 'Fecal Coliform',
                          'Total Coliform', 'Potability', 'Parameter Correlations'),
            specs=[[{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}],
                  [{"type": "scatter"}, {"type": "scatter"}, {"type": "scatter"}],
                  [{"type": "scatter"}, {"type": "bar"}, {"type": "heatmap"}]]
        )
        
        # Add traces for each parameter
        parameters = ['ph', 'DO', 'conductivity', 'BOD', 'nitrate', 'fecalcaliform', 'totalcaliform']
        for i, param in enumerate(parameters):
            row = (i // 3) + 1
            col = (i % 3) + 1
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df[param], name=param),
                row=row, col=col
            )
        
        # Add potability bar chart
        potability_counts = df['is_potable'].value_counts()
        fig.add_trace(
            go.Bar(x=['Not Potable', 'Potable'], y=potability_counts.values),
            row=3, col=2
        )
        
        # Add correlation heatmap
        corr_matrix = df[parameters].corr()
        fig.add_trace(
            go.Heatmap(z=corr_matrix.values,
                      x=parameters,
                      y=parameters,
                      colorscale='RdBu'),
            row=3, col=3
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            width=1200,
            title_text=f"Water Quality Dashboard - {location}",
            showlegend=True
        )
        
        # Convert to JSON for web display
        return json.loads(fig.to_json())

    def create_parameter_dashboard(self, location: str, parameter: str, days: int = 30) -> Dict:
        """Create a detailed dashboard for a specific parameter"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        measurements = self.db.query(WaterQualityMeasurement).filter(
            WaterQualityMeasurement.location == location,
            WaterQualityMeasurement.timestamp >= start_date,
            WaterQualityMeasurement.timestamp <= end_date
        ).all()
        
        # Convert to DataFrame
        data = []
        for m in measurements:
            data.append({
                'timestamp': m.timestamp,
                parameter: getattr(m, parameter),
                'is_potable': m.is_potable
            })
        df = pd.DataFrame(data)
        
        # Create figure
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(f'{parameter} Over Time', f'{parameter} Distribution'),
            specs=[[{"type": "scatter"}], [{"type": "box"}]]
        )
        
        # Add time series
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df[parameter], name=parameter),
            row=1, col=1
        )
        
        # Add box plot
        fig.add_trace(
            go.Box(y=df[parameter], name=parameter),
            row=2, col=1
        )
        
        # Update layout
        fig.update_layout(
            height=800,
            width=1000,
            title_text=f"{parameter} Analysis - {location}",
            showlegend=True
        )
        
        # Calculate statistics
        stats = {
            'mean': df[parameter].mean(),
            'median': df[parameter].median(),
            'std': df[parameter].std(),
            'min': df[parameter].min(),
            'max': df[parameter].max(),
            'count': len(df)
        }
        
        return {
            'plot': json.loads(fig.to_json()),
            'statistics': stats
        }

    def create_comparison_dashboard(self, locations: List[str], days: int = 30) -> Dict:
        """Create a dashboard comparing multiple locations"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get data for all locations
        all_data = []
        for location in locations:
            measurements = self.db.query(WaterQualityMeasurement).filter(
                WaterQualityMeasurement.location == location,
                WaterQualityMeasurement.timestamp >= start_date,
                WaterQualityMeasurement.timestamp <= end_date
            ).all()
            
            for m in measurements:
                all_data.append({
                    'location': location,
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
        
        df = pd.DataFrame(all_data)
        
        # Create figure
        fig = make_subplots(
            rows=3, cols=3,
            subplot_titles=('pH', 'Dissolved Oxygen', 'Conductivity',
                          'BOD', 'Nitrate', 'Fecal Coliform',
                          'Total Coliform', 'Potability', 'Parameter Averages'),
            specs=[[{"type": "box"}, {"type": "box"}, {"type": "box"}],
                  [{"type": "box"}, {"type": "box"}, {"type": "box"}],
                  [{"type": "box"}, {"type": "bar"}, {"type": "bar"}]]
        )
        
        # Add box plots for each parameter
        parameters = ['ph', 'DO', 'conductivity', 'BOD', 'nitrate', 'fecalcaliform', 'totalcaliform']
        for i, param in enumerate(parameters):
            row = (i // 3) + 1
            col = (i % 3) + 1
            fig.add_trace(
                go.Box(y=df[param], x=df['location'], name=param),
                row=row, col=col
            )
        
        # Add potability bar chart
        potability_counts = df.groupby('location')['is_potable'].mean()
        fig.add_trace(
            go.Bar(x=potability_counts.index, y=potability_counts.values),
            row=3, col=2
        )
        
        # Add parameter averages
        param_avgs = df.groupby('location')[parameters].mean()
        fig.add_trace(
            go.Bar(x=param_avgs.index, y=param_avgs.mean(axis=1)),
            row=3, col=3
        )
        
        # Update layout
        fig.update_layout(
            height=1200,
            width=1200,
            title_text="Water Quality Comparison Dashboard",
            showlegend=True
        )
        
        return json.loads(fig.to_json()) 