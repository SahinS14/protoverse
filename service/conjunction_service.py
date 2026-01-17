import sqlite3
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any
from backend.models.db import get_conn
from service.tle_service import tle_service
from processing.propagator import tle_to_satrec
from processing.propagate_wrapper import propagate_satrec_single
from processing.pruner import prune_pairs
from processing.conjunction import compute_conjunction_for_pair


class ConjunctionService:
    """
    This service manages the entire Conjunction Assessment process.
    It receives, processes, filters the data, and writes the result to the database.
    """

    def run_conjunction_screening(self, analysis_start_time: datetime = None, duration_hours: int = 2) -> Dict[
        str, int]:
        """
        Main Screening Function (Screening Loop).
            1. Fetches active satellites.
            2. Finds candidate pairs using KD-Tree (Broad Phase).
            3. Performs detailed analysis with SGP4 and Optimization (Narrow Phase).
            4. Saves risky situations to the database.
        """

        if analysis_start_time is None:
            # If analysis start time is not specified, use current UTC time
            analysis_start_time = datetime.now(timezone.utc)

        # Get active satellites
        satellites = tle_service.get_all_satellites(limit=5000)
        if len(satellites) < 2:
            return {"status": "Not enough satellites", "processed_pairs": 0, "alerts_saved": 0}

        satrecs = {}  # Will hold SGP4 objects
        states_map = {}  # Will hold position/velocity data of satellites at t0

        # Calculate Initial States
        # To build the KD-Tree, we need the positions of all satellites at t0
        for sat in satellites:
            sid = sat["id"]
            try:
                st = tle_to_satrec(sat["line1"], sat["line2"])
                satrecs[sid] = st
                r = propagate_satrec_single(st, analysis_start_time)
                r_f = propagate_satrec_single(st, analysis_start_time + timedelta(seconds=1))
                v = (r_f - r) / 1.0
                states_map[sid] = (r, v)
            except Exception:
                continue

        if len(states_map) < 2:
            return {"status": "Insufficient data", "processed_pairs": 0, "alerts_saved": 0}

        # Pruning Phase - Broad Phase Detection
        # KD-Tree will be used
        ANALYTIC_WINDOW = 7200.0  # We will look at a 2-hour window
        RADIUS_KM = 300.0  # Only those within 300km of each other will be considered
        COLLISION_SAVE_THRESHOLD_KM = 150.0  # If farther than 150km, will not be saved to DB

        # Only position data (r) is given to the KD-Tree
        positions_map = {k: v[0] for k, v in states_map.items()}

        # prune_pairs function returns only potentially risky pairs (id1, id2)
        # For example: Instead of 12.5 million pairs for 5000 satellites, only about 500 pairs are returned.
        candidate_pairs = prune_pairs(positions_map, radius_km=RADIUS_KM)

        conn = get_conn()
        cur = conn.cursor()

        # For demo purposes, we clear old alerts on each scan
        # In a real application, this should be moved to an 'archive' table
        cur.execute("DELETE FROM conjunction_alerts")
        conn.commit()
        saved_count = 0


        # Detailed analysis on candidate pairs, Narrow Phase
        # SGP4 and Optimization will only be run on filtered candidate pairs
        for id1, id2 in candidate_pairs:
            if id1 not in satrecs or id2 not in satrecs:
                continue

            sat1 = satrecs[id1]
            sat2 = satrecs[id2]
            r1, v1 = states_map[id1]
            r2, v2 = states_map[id2]

            try:
                # Analytical Prediction -> SGP4 Refinement -> Docking Check
                conj = compute_conjunction_for_pair(
                    sat1, sat2,
                    analysis_start_time,
                    r1, v1, r2, v2,
                    propagate_satrec_single,
                    analytic_window_sec=ANALYTIC_WINDOW
                )
            except Exception as e:
                print(f"Error computing pair {id1}-{id2}: {e}")
                continue

            if conj is None:
                continue

            # Save Results (Persistence)
            should_save = False
            # DOCKING: Save docking maneuvers (since there is a separate section in the interface)
            if conj.event_type == "DOCKING":
                should_save = True
            elif conj.event_type == "COLLISION":
                # Score > 0 means there is a certain risk
                # Also, distance must be below the threshold (150 km)
                if conj.score > 0 and conj.miss_distance_km < COLLISION_SAVE_THRESHOLD_KM:
                    should_save = True

            if should_save:
                cur.execute("""
                    INSERT INTO conjunction_alerts 
                    (sat1_id, sat2_id, tca, miss_distance_km, rel_velocity_km_s, score, event_type, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    id1, id2,
                    conj.tca.isoformat(),
                    conj.miss_distance_km,
                    conj.rel_velocity_km_s,
                    conj.score,
                    conj.event_type,
                    datetime.now(timezone.utc).isoformat()
                ))
                saved_count += 1

        conn.commit()
        conn.close()

        # Summary report to be returned to the API
        return {"processed_pairs": len(candidate_pairs), "alerts_saved": saved_count}

    def get_alerts(self, limit: int = 20, event_type: str = "COLLISION", country: str = None, priority: str = None) -> List[Dict[str, Any]]:
        """
        Fetches alerts from the database.
        Uses SQL JOIN to also get satellite names and metadata from the Satellite table.
        Filters by country and priority if provided.
        """
        conn = get_conn()
        cur = conn.cursor()
        query = """
            SELECT 
                a.id, a.sat1_id, a.sat2_id, a.tca, a.miss_distance_km, a.rel_velocity_km_s, a.score, a.event_type, a.created_at,
                s1.sat_name as sat1_name, s2.sat_name as sat2_name,
                s1.country as sat1_country, s2.country as sat2_country,
                s1.priority as sat1_priority, s2.priority as sat2_priority
            FROM conjunction_alerts a
            JOIN raw_tles s1 ON a.sat1_id = s1.id
            JOIN raw_tles s2 ON a.sat2_id = s2.id
            WHERE a.event_type = ?
        """
        params = [event_type]
        if country:
            query += " AND (s1.country = ? OR s2.country = ?)"
            params.extend([country, country])
        if priority:
            query += " AND (s1.priority = ? OR s2.priority = ?)"
            params.extend([priority, priority])
        query += " ORDER BY a.score DESC, a.tca ASC LIMIT ?"
        params.append(limit)
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        conn.close()
        # Convert row objects to dictionary for JSON compatibility
        return [dict(row) for row in rows]


# Singleton instance (Service is started as a single instance)
conjunction_service = ConjunctionService()
