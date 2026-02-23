import pandas as pd
import datetime
from .database import SessionLocal
from .models import TimeSeriesDataModel, GridNodeModel
import random

class RealDataIngester:
    """
    Ingests real-world grid data from various sources.
    For the A16Z demo, we priority-support IEX (India) and EIA (US).
    """
    
    @staticmethod
    def ingest_from_csv(file_path: str, source_type: str = "iex"):
        db = SessionLocal()
        print(f"Ingesting data from {file_path} (Type: {source_type})...")
        
        try:
            df = pd.read_csv(file_path)
            # Logic would vary based on CSV structure
            # Example for IEX-like hourly market data
            for index, row in df.iterrows():
                # Map CSV columns to our Telemetry model
                # This is a template - actual mapping depends on real CSV headers
                telemetry = TimeSeriesDataModel(
                    node_id="n4", # Defaulting to Main Substation for demo
                    timestamp=datetime.datetime.now(),
                    demand_mw=row.get('demand', 400.0) + random.uniform(-10, 10),
                    supply_mw=row.get('supply', 410.0),
                    carbon_intensity=row.get('carbon', 0.45),
                    reliability_score=row.get('reliability', 0.999)
                )
                db.add(telemetry)
            
            db.commit()
            print(f"Successfully ingested {len(df)} records.")
        except Exception as e:
            print(f"Ingestion failed: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    def create_sample_iex_data():
        """Generates a CSV that mimics real IEX market data for the demo."""
        data = []
        base_time = datetime.datetime.now()
        for i in range(24):
            data.append({
                "time": (base_time - datetime.timedelta(hours=i)).isoformat(),
                "demand": 400 + 50 * (1 if 9 <= (base_time - datetime.timedelta(hours=i)).hour <= 18 else 0.5) + random.uniform(-20, 20),
                "supply": 450 + random.uniform(-10, 10),
                "carbon": 0.4 + random.uniform(0.1, 0.2),
                "reliability": 0.99 + random.uniform(0, 0.01)
            })
        df = pd.DataFrame(data)
        df.to_csv("iex_market_data.csv", index=False)
        print("Generated iex_market_data.csv for ingestion testing.")

if __name__ == "__main__":
    # Test path
    RealDataIngester.create_sample_iex_data()
    RealDataIngester.ingest_from_csv("iex_market_data.csv")
