from .database import SessionLocal, engine, Base
from .models import GridNodeModel, GridLinkModel, PolicyModel, TimeSeriesDataModel
from .mock_data import MockDataService

def init_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Check if nodes exist, if not seed them
    if not db.query(GridNodeModel).first():
        print("Seeding database with initial topology...")
        
        # Pull from existing MockDataService to preserve continuity
        default_state = MockDataService.get_default_state()
        
        # Seed Nodes
        for source in default_state.sources:
            # Note: sources in schemas.py are slightly different from GridNode in infrastructure.py
            # I'll manually seed based on api/infrastructure.py MOCK_NODES for better topological resolution
            pass
        
        # Better approach: Redefine the core MOCK_NODES here for the DB
        # This matches backend/api/infrastructure.py
        mock_nodes = [
            {"id": "n1", "name": "Solar Farm Alpha", "type": "generator", "capacity_mw": 150, "location_x": 77.594, "location_y": 12.971, "location_z": 5.0, "status": "online"},
            {"id": "n2", "name": "Wind Park Beta", "type": "generator", "capacity_mw": 200, "location_x": 77.610, "location_y": 12.920, "location_z": 50.0, "status": "online"},
            {"id": "n3", "name": "Thermal Plant Gamma", "type": "generator", "capacity_mw": 500, "location_x": 77.550, "location_y": 13.010, "location_z": 2.0, "status": "online"},
            {"id": "n4", "name": "Main City Substation", "type": "load", "capacity_mw": 0, "location_x": 77.580, "location_y": 12.950, "location_z": 10.0, "status": "online"},
            {"id": "n5", "name": "Industrial Zone", "type": "load", "capacity_mw": 0, "location_x": 77.620, "location_y": 12.980, "location_z": 5.0, "status": "online"},
            {"id": "n6", "name": "Grid Battery Storage", "type": "storage", "capacity_mw": 100, "location_x": 77.560, "location_y": 12.940, "location_z": 8.0, "status": "online"},
            {"id": "n7", "name": "BSR-220 SMR (Nuclear)", "type": "nuclear", "capacity_mw": 220, "location_x": 77.650, "location_y": 13.050, "location_z": -10.0, "status": "online"},
        ]
        
        for node_data in mock_nodes:
            db.add(GridNodeModel(**node_data))
            
        mock_links = [
            {"id": "l1", "source_id": "n1", "target_id": "n4", "capacity_mw": 200, "current_load_mw": 120, "resistance": 0.05, "reactance": 0.2, "length_km": 45.0},
            {"id": "l2", "source_id": "n2", "target_id": "n4", "capacity_mw": 250, "current_load_mw": 180, "resistance": 0.08, "reactance": 0.3, "length_km": 60.0},
            {"id": "l3", "source_id": "n3", "target_id": "n4", "capacity_mw": 600, "current_load_mw": 400, "resistance": 0.02, "reactance": 0.1, "length_km": 30.0},
            {"id": "l4", "source_id": "n4", "target_id": "n5", "capacity_mw": 400, "current_load_mw": 0, "resistance": 0.04, "reactance": 0.15, "length_km": 25.0, "status": "failed", "fault_position": 0.72},
            {"id": "l5", "source_id": "n6", "target_id": "n4", "capacity_mw": 100, "current_load_mw": 0, "resistance": 0.01, "reactance": 0.05, "length_km": 5.0},
            {"id": "l6", "source_id": "n7", "target_id": "n5", "capacity_mw": 300, "current_load_mw": 150, "resistance": 0.03, "reactance": 0.12, "length_km": 40.0},
        ]
        
        for link_data in mock_links:
            db.add(GridLinkModel(**link_data))
            
        # Seed Default Policy
        db.add(PolicyModel(
            max_cost_per_mwh=100.0,
            max_carbon_per_mwh=0.5,
            min_reliability_score=0.99,
            risk_tolerance="neutral"
        ))
        
        db.commit()

        # Seed initial telemetry (last 24 hours)
        import datetime
        import random
        print("Seeding telemetry history...")
        for i in range(24):
            ts = datetime.datetime.utcnow() - datetime.timedelta(hours=(24-i))
            db.add(TimeSeriesDataModel(
                node_id="n4",
                timestamp=ts,
                demand_mw=400.0 + random.uniform(-50, 50),
                supply_mw=420.0 + random.uniform(-40, 60),
                carbon_intensity=0.3 + random.uniform(-0.1, 0.1),
                reliability_score=0.99
            ))
        
        db.commit()
        print("Database initialized and seeded.")
    else:
        print("Database already initialized.")
    
    db.close()

if __name__ == "__main__":
    init_db()
