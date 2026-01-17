from pathlib import Path
import sqlite3
import logging

 # Set the database path according to the project directory structure
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "astm.db"  # AstroGuard database path (legacy name retained for compatibility)
logging.basicConfig(level=logging.INFO)
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

    # --- MIGRATION: Add missing columns country, priority, mission_priority ---
    curr.execute("PRAGMA table_info(raw_tles)")
    columns = [row[1] for row in curr.fetchall()]
    missing = []
    if "country" not in columns:
        try:
            curr.execute("ALTER TABLE raw_tles ADD COLUMN country TEXT DEFAULT 'Global'")
            logging.info("Migrated: Added 'country' column to raw_tles.")
        except Exception as e:
            missing.append("country")
            logging.warning(f"Could not ALTER TABLE for 'country': {e}")
    if "priority" not in columns:
        try:
            curr.execute("ALTER TABLE raw_tles ADD COLUMN priority TEXT DEFAULT 'SECONDARY'")
            logging.info("Migrated: Added 'priority' column to raw_tles.")
        except Exception as e:
            missing.append("priority")
            logging.warning(f"Could not ALTER TABLE for 'priority': {e}")
    if "mission_priority" not in columns:
        try:
            curr.execute("ALTER TABLE raw_tles ADD COLUMN mission_priority TEXT DEFAULT 'NORMAL'")
            logging.info("Migrated: Added 'mission_priority' column to raw_tles.")
        except Exception as e:
            missing.append("mission_priority")
            logging.warning(f"Could not ALTER TABLE for 'mission_priority': {e}")

    # If ALTER TABLE failed, recreate table and migrate data
    if missing:
        logging.info("Recreating raw_tles table to add missing columns: %s", missing)
        curr.execute("PRAGMA foreign_keys=off")
        curr.execute("BEGIN TRANSACTION")
        curr.execute("""
            CREATE TABLE IF NOT EXISTS raw_tles_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sat_name TEXT,
                line1 TEXT,
                line2 TEXT,
                epoch TEXT,
                source TEXT,
                fetched_at TEXT,
                country TEXT DEFAULT 'Global',
                priority TEXT DEFAULT 'SECONDARY',
                mission_priority TEXT DEFAULT 'NORMAL'
            )
        """)
        curr.execute("""
            INSERT INTO raw_tles_new (id, sat_name, line1, line2, epoch, source, fetched_at, country, priority, mission_priority)
            SELECT id, sat_name, line1, line2, epoch, source, fetched_at,
                COALESCE(country, 'Global'), COALESCE(priority, 'SECONDARY'), COALESCE(mission_priority, 'NORMAL') FROM raw_tles
        """)
        curr.execute("DROP TABLE raw_tles")
        curr.execute("ALTER TABLE raw_tles_new RENAME TO raw_tles")
        curr.execute("COMMIT")
        curr.execute("PRAGMA foreign_keys=on")
        logging.info("Migration complete: raw_tles table recreated with all required columns.")

    # Ensure all rows have defaults
    curr.execute("UPDATE raw_tles SET country = 'Global' WHERE country IS NULL OR country = ''")
    curr.execute("UPDATE raw_tles SET priority = 'SECONDARY' WHERE priority IS NULL OR priority = ''")
    curr.execute("UPDATE raw_tles SET mission_priority = 'NORMAL' WHERE mission_priority IS NULL OR mission_priority = ''")

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
