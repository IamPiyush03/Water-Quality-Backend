from database.config import Base, engine
from database.models import WaterQualityMeasurement, WaterQualityPrediction, Recommendation
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def init_db():
    print("Creating database tables...")
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure PostgreSQL is running")
        print("2. Verify your .env file has the correct DATABASE_URL")
        print("3. Check if the database 'water_quality' exists")
        print("4. Verify your PostgreSQL username and password")

if __name__ == "__main__":
    init_db() 