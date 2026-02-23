from sqlalchemy import create_engine, inspect
import os

DB_URL = "sqlite:///./edl_core.db"
engine = create_engine(DB_URL)

def check_schema():
    inspector = inspect(engine)
    if 'nodes' not in inspector.get_table_names():
        print("Table 'nodes' not found.")
        return
        
    columns = [col['name'] for col in inspector.get_columns('nodes')]
    print(f"Columns in 'nodes': {columns}")
    
    if 'health_index' in columns:
        print("SUCCESS: 'health_index' exists.")
    else:
        print("FAILURE: 'health_index' missing.")

if __name__ == "__main__":
    print(f"Current Working Directory: {os.getcwd()}")
    print(f"Checking DB: {DB_URL}")
    check_schema()
