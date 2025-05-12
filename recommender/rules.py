from typing import Dict, List
from .guidelines import GUIDELINES

class WaterQualityRecommender:
    def __init__(self):
        self.guidelines = GUIDELINES
    
    def _get_severity_level(self, value: float, param: str, direction: str) -> str:
        """Determine severity level based on value and parameter"""
        if param not in self.guidelines:
            return "unknown"
            
        param_guidelines = self.guidelines[param]
        severity_levels = param_guidelines["severity_levels"]
        
        if direction == "low":
            for level, threshold in severity_levels.items():
                if value <= threshold:
                    return level
        else:  # high
            for level, threshold in severity_levels.items():
                if value >= threshold:
                    return level
                    
        return "normal"
    
    def generate_recommendations(self, input_values: Dict[str, float]) -> Dict[str, List[str]]:
        """Generate comprehensive recommendations based on input values and WHO guidelines"""
        recommendations = {
            "immediate": [],
            "short_term": [],
            "long_term": [],
            "preventive": []
        }
        
        for param, value in input_values.items():
            try:
                # Check if parameter exists in guidelines
                if param not in self.guidelines:
                    print(f"Warning: No guidelines found for parameter {param}")
                    continue
                    
                param_guidelines = self.guidelines[param]
                min_val, max_val = param_guidelines["range"]
                
                # Determine if value is low or high
                if value < min_val:
                    direction = "low"
                    severity = self._get_severity_level(value, param, direction)
                elif value > max_val:
                    direction = "high"
                    severity = self._get_severity_level(value, param, direction)
                else:
                    continue  # Value is within acceptable range
                
                # Get measures for the current direction and severity
                measures = param_guidelines["measures"][direction]
                
                # Add recommendations based on priority
                for priority in ["immediate", "short_term", "long_term", "preventive"]:
                    if priority in measures and measures[priority]:
                        # Add parameter name and severity to each recommendation
                        param_recommendations = [
                            f"[{param.upper()}] [{severity.upper()}] {action}" 
                            for action in measures[priority]
                        ]
                        recommendations[priority].extend(param_recommendations)
                        
            except Exception as e:
                print(f"Error processing {param}: {str(e)}")
                continue
        
        return recommendations 