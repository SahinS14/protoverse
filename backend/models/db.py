from pathlib import Path
import sqlite3

 # Set the database path according to the project directory structure
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "astm.db"  # AstroGuard database path (legacy name retained for compatibility)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    curr = conn.cursor()

    # TLE Table
    curr.execute("""
        CREATE TABLE IF NOT EXISTS raw_tles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sat_name TEXT,
            line1 TEXT,
            line2 TEXT,
            epoch TEXT,
            source TEXT,
            fetched_at TEXT
        )
    """)

    # Conjunction Alerts Table
    # Default value is 'COLLISION'
    # For docking events, we will use 'DOCKING'
    curr.execute("""
        CREATE TABLE IF NOT EXISTS conjunction_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sat1_id INTEGER,
            sat2_id INTEGER,
            tca TEXT,
            miss_distance_km REAL,
            rel_velocity_km_s REAL,
            score REAL,
            event_type TEXT DEFAULT 'COLLISION', 
            created_at TEXT
        )
        """)

    curr.execute("""
        CREATE TABLE IF NOT EXISTS satellite_intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sat_id INTEGER UNIQUE,
            predicted_category TEXT,
            predicted_country TEXT,
            confidence REAL,
            cluster_id INTEGER,
            is_anomaly INTEGER,
            decay_risk TEXT, 
            predicted_at TEXT,
            FOREIGN KEY (sat_id) REFERENCES raw_tles(id)
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database tables created/updated successfully.")
