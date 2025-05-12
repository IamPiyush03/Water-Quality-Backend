import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import pandas as pd

class WaterQualityVisualizer:
    def __init__(self, session):
        self.session = session
    
    def create_trend_plot(self, location, parameter, days=30):
        """Create a trend plot for a specific parameter over time"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        data = self.session.query(
            WaterQualityMeasurement.timestamp,
            getattr(WaterQualityMeasurement, parameter)
        ).filter(
            WaterQualityMeasurement.location == location,
            WaterQualityMeasurement.timestamp >= start_date,
            WaterQualityMeasurement.timestamp <= end_date
        ).order_by(WaterQualityMeasurement.timestamp).all()
        
        if not data:
            return None
            
        timestamps, values = zip(*data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=values,
            mode='lines+markers',
            name=parameter
        ))
        
        # Add acceptable range lines if available
        if parameter in ['ph', 'dissolved_oxygen', 'conductivity']:
            ranges = {
                'ph': [6.5, 8.5],
                'dissolved_oxygen': [5.0, 8.0],
                'conductivity': [200, 800]
            }
            fig.add_hline(y=ranges[parameter][0], line_dash="dash", line_color="red")
            fig.add_hline(y=ranges[parameter][1], line_dash="dash", line_color="red")
        
        fig.update_layout(
            title=f"{parameter} Trend for {location}",
            xaxis_title="Date",
            yaxis_title=parameter,
            showlegend=True
        )
        
        return fig
    
    def create_parameter_correlation_plot(self, location):
        """Create a correlation matrix for water quality parameters"""
        data = self.session.query(
            WaterQualityMeasurement.ph,
            WaterQualityMeasurement.dissolved_oxygen,
            WaterQualityMeasurement.conductivity,
            WaterQualityMeasurement.bod,
            WaterQualityMeasurement.nitrate
        ).filter(
            WaterQualityMeasurement.location == location
        ).all()
        
        if not data:
            return None
            
        df = pd.DataFrame(data, columns=['pH', 'DO', 'Conductivity', 'BOD', 'Nitrate'])
        corr = df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr,
            x=corr.columns,
            y=corr.columns,
            colorscale='RdBu',
            zmin=-1,
            zmax=1
        ))
        
        fig.update_layout(
            title=f"Parameter Correlations for {location}",
            xaxis_title="Parameters",
            yaxis_title="Parameters"
        )
        
        return fig
    
    def create_recommendation_status_pie(self, location):
        """Create a pie chart showing recommendation status distribution"""
        data = self.session.query(
            Recommendation.status,
            func.count(Recommendation.id)
        ).join(
            WaterQualityMeasurement
        ).filter(
            WaterQualityMeasurement.location == location
        ).group_by(Recommendation.status).all()
        
        if not data:
            return None
            
        statuses, counts = zip(*data)
        
        fig = go.Figure(data=[go.Pie(
            labels=statuses,
            values=counts,
            hole=.3
        )])
        
        fig.update_layout(
            title=f"Recommendation Status Distribution for {location}"
        )
        
        return fig
    
    def create_parameter_distribution_plot(self, location, parameter):
        """Create a distribution plot for a specific parameter"""
        data = self.session.query(
            getattr(WaterQualityMeasurement, parameter)
        ).filter(
            WaterQualityMeasurement.location == location
        ).all()
        
        if not data:
            return None
            
        values = [d[0] for d in data]
        
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=values,
            nbinsx=30,
            name=parameter
        ))
        
        fig.update_layout(
            title=f"{parameter} Distribution for {location}",
            xaxis_title=parameter,
            yaxis_title="Frequency"
        )
        
        return fig
    
    def create_dashboard(self, location):
        """Create a comprehensive dashboard for a location"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                "pH Trend", "Parameter Correlations",
                "DO Trend", "Recommendation Status"
            )
        )
        
        # Add pH trend
        ph_trend = self.create_trend_plot(location, 'ph')
        if ph_trend:
            fig.add_trace(ph_trend.data[0], row=1, col=1)
        
        # Add correlation plot
        corr_plot = self.create_parameter_correlation_plot(location)
        if corr_plot:
            fig.add_trace(corr_plot.data[0], row=1, col=2)
        
        # Add DO trend
        do_trend = self.create_trend_plot(location, 'dissolved_oxygen')
        if do_trend:
            fig.add_trace(do_trend.data[0], row=2, col=1)
        
        # Add recommendation status
        status_pie = self.create_recommendation_status_pie(location)
        if status_pie:
            fig.add_trace(status_pie.data[0], row=2, col=2)
        
        fig.update_layout(
            height=800,
            width=1200,
            title_text=f"Water Quality Dashboard for {location}",
            showlegend=True
        )
        
        return fig 