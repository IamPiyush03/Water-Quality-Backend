# Water Quality Analysis API

A FastAPI-based backend service for analyzing water quality and providing recommendations based on WHO guidelines.

## Features

- Predict water potability using machine learning
- Generate detailed recommendations based on WHO guidelines
- RESTful API endpoints for easy integration
- Comprehensive water quality parameter analysis

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd water-quality-analysis
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the API server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation at `http://localhost:8000/docs`

## API Endpoints

### POST /predict
Predicts whether water is potable based on input parameters.

### POST /analyze
Provides comprehensive analysis including potability prediction and recommendations.

## Project Structure

```
backend/
├── main.py              # FastAPI application
├── models/
│   └── predict.py       # ML prediction model
├── recommender/
│   └── rules.py         # WHO guidelines and recommendations
├── data/
│   └── aquaattributes.xlsx  # Training data
├── utils/
│   └── parser.py        # PDF parsing utilities
└── tests/               # Test files
```

## Development

1. Training the model:
```python
from models.predict import WaterQualityPredictor

predictor = WaterQualityPredictor()
predictor.train("data/aquaattributes.xlsx")
```

2. Generating recommendations:
```python
from recommender.rules import WaterQualityRecommender

recommender = WaterQualityRecommender()
recommendations = recommender.generate_recommendations({
    "ph": 7.5,
    "hardness": 150,
    # ... other parameters
})
```

## License

MIT License #   W a t e r - Q u a l i t y - B a c k e n d  
 