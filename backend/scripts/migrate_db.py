import sqlite3
import os

DB_PATH = "edl_core.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Nodes columns
    nodes_cols = {
        "voltage_level_kv": "REAL DEFAULT 220.0",
        "health_index": "REAL DEFAULT 1.0",
        "pd_activity": "REAL DEFAULT 0.0"
    }

    cursor.execute("PRAGMA table_info(nodes)")
    current_nodes_cols = [row[1] for row in cursor.fetchall()]
    
    for col, spec in nodes_cols.items():
        if col not in current_nodes_cols:
            print(f"Adding column {col} to nodes table...")
            cursor.execute(f"ALTER TABLE nodes ADD COLUMN {col} {spec}")

    # Links columns
    links_cols = {
        "resistance_ohms": "REAL DEFAULT 0.1",
        "reactance_ohms": "REAL DEFAULT 0.5",
        "max_thermal_rating_mva": "REAL DEFAULT 500.0",
        "static_rating_mva": "REAL DEFAULT 500.0",
        "dynamic_rating_mva": "REAL DEFAULT 500.0",
        "limiting_factor": "TEXT DEFAULT 'Static'",
        "health_index": "REAL DEFAULT 1.0",
        "pd_activity": "REAL DEFAULT 0.0"
    }

    cursor.execute("PRAGMA table_info(links)")
    current_links_cols = [row[1] for row in cursor.fetchall()]

    for col, spec in links_cols.items():
        if col not in current_links_cols:
            print(f"Adding column {col} to links table...")
            cursor.execute(f"ALTER TABLE links ADD COLUMN {col} {spec}")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
