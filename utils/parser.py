import pdfplumber
import json
import os
from typing import Dict, List, Optional
import re

class WHOGuidelinesParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pdf = None
        
    def open_document(self) -> bool:
        """Open the PDF document"""
        try:
            self.pdf = pdfplumber.open(self.pdf_path)
            return True
        except Exception as e:
            print(f"Error opening PDF: {e}")
            return False
    
    def extract_text(self, page_num: int) -> str:
        """Extract text from a specific page"""
        if not self.pdf:
            return ""
        try:
            page = self.pdf.pages[page_num]
            return page.extract_text()
        except Exception as e:
            print(f"Error extracting text from page {page_num}: {e}")
            return ""
    
    def find_parameter_section(self, parameter: str) -> Optional[int]:
        """Find the page number containing the parameter section"""
        if not self.pdf:
            return None
            
        for page_num in range(len(self.pdf.pages)):
            text = self.extract_text(page_num)
            if parameter.lower() in text.lower():
                return page_num
        return None
    
    def _extract_range(self, text: str) -> List[float]:
        """Extract numeric range from text"""
        # Look for patterns like "6.5-8.5" or "6.5 to 8.5"
        range_pattern = r'(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)'
        match = re.search(range_pattern, text)
        if match:
            return [float(match.group(1)), float(match.group(2))]
        return [0, 0]
    
    def _extract_severity_levels(self, text: str) -> Dict[str, List[float]]:
        """Extract severity level thresholds from text"""
        severity_levels = {}
        # Look for patterns like "Severe: > 8.5" or "Critical: > 9.0"
        severity_pattern = r'(mild|moderate|severe|critical)\s*[:>]\s*(\d+\.?\d*)'
        matches = re.finditer(severity_pattern, text.lower())
        for match in matches:
            severity_levels[match.group(1)] = float(match.group(2))
        return severity_levels
    
    def _extract_measures(self, text: str, direction: str) -> Dict[str, List[str]]:
        """Extract measures for a specific direction (low/high)"""
        measures = {
            "immediate": [],
            "short_term": [],
            "long_term": [],
            "preventive": []
        }
        
        # Look for measures in the text
        priority_patterns = {
            "immediate": r'immediate\s*actions?[:;]?\s*(.*?)(?=\n|short|long|preventive|$)',
            "short_term": r'short\s*term\s*actions?[:;]?\s*(.*?)(?=\n|long|preventive|$)',
            "long_term": r'long\s*term\s*actions?[:;]?\s*(.*?)(?=\n|preventive|$)',
            "preventive": r'preventive\s*measures?[:;]?\s*(.*?)(?=\n|$)'
        }
        
        for priority, pattern in priority_patterns.items():
            matches = re.finditer(pattern, text.lower())
            for match in matches:
                measures[priority].extend([m.strip() for m in match.group(1).split('\n') if m.strip()])
        
        return measures
    
    def _parse_parameter_section(self, text: str) -> Dict:
        """Parse a specific parameter section from the text"""
        # Extract range
        range_values = self._extract_range(text)
        
        # Extract severity levels
        severity_levels = self._extract_severity_levels(text)
        
        # Extract measures for low and high values
        low_measures = self._extract_measures(text, "low")
        high_measures = self._extract_measures(text, "high")
        
        return {
            "range": range_values,
            "severity_levels": severity_levels,
            "measures": {
                "low": low_measures,
                "high": high_measures
            }
        }
    
    def parse_guidelines(self) -> Dict:
        """Parse WHO guidelines from the PDF"""
        if not self.open_document():
            return {}
            
        guidelines = {}
        parameters = [
            "pH", "Hardness", "Solids", "Chloramines",
            "Sulfate", "Conductivity", "Organic Carbon",
            "Trihalomethanes", "Turbidity", "Dissolved Oxygen",
            "BOD", "Nitrate", "Fecal Coliform", "Total Coliform"
        ]
        
        for param in parameters:
            page_num = self.find_parameter_section(param)
            if page_num is not None:
                text = self.extract_text(page_num)
                guidelines[param.lower()] = self._parse_parameter_section(text)
        
        return guidelines
    
    def save_guidelines(self, output_path: str) -> bool:
        """Save parsed guidelines to a JSON file"""
        guidelines = self.parse_guidelines()
        try:
            with open(output_path, 'w') as f:
                json.dump(guidelines, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving guidelines: {e}")
            return False 