from datetime import datetime, timedelta
from typing import Dict, Any
from service.tle_service import tle_service
from planner.optimizer import find_minimal_dv
from processing.propagate_wrapper import propagate_satrec_single


class ManeuverService:
    """
    This service calculates the optimal avoidance maneuver for a detected collision risk.
    It uses the mathematical optimization engine (find_minimal_dv) and presents the results
    in a format understandable by the API.
    """
    def calculate_avoidance_maneuver(self,
                                     sat_id_primary: int,
                                     sat_id_secondary: int,
                                     tca: datetime,
                                     target_miss_km: float = 2.0) -> Dict[str, Any]:
        """
        Creates the required burn plan to prevent a collision between two satellites.
        Args:
            sat_id_primary: Our satellite that will perform the maneuver.
            sat_id_secondary: The other object at collision risk (debris or satellite).
            tca: Time of Closest Approach.
            target_miss_km: Target safe distance (Default: 2 km).
        """
        # Get the mathematical models (SGP4 objects) of the satellites
        sat1 = tle_service.get_satrec_by_id(sat_id_primary)
        sat2 = tle_service.get_satrec_by_id(sat_id_secondary)

        if not sat1 or not sat2:
            raise ValueError("Satellites not found")

        # Fetch metadata for stricter safety margins
        sat1_meta = tle_service.get_satellite_by_id(sat_id_primary)
        sat2_meta = tle_service.get_satellite_by_id(sat_id_secondary)
        # Default safety margin
        margin_km = target_miss_km
        # Apply stricter margin for CRITICAL satellites
        if (sat1_meta and sat1_meta.get("mission_priority") == "CRITICAL") or (sat2_meta and sat2_meta.get("mission_priority") == "CRITICAL"):
            margin_km = max(target_miss_km, target_miss_km * 1.5)
            print(f"[Critical Mission Mode] Stricter maneuver margin applied: {margin_km} km for pair {sat_id_primary}-{sat_id_secondary}")
        # Apply stricter margin for PRIMARY (Indian) satellites (legacy logic)
        elif sat1_meta and sat1_meta.get("country") == "India" and sat1_meta.get("priority") == "PRIMARY":
            margin_km = max(target_miss_km, 5.0)  # Stricter: at least 5 km

        burn_time = tca - timedelta(seconds=3600)

        proposal = find_minimal_dv(
            satrec_target=sat2,
            satrec_our=sat1,
            burn_time=burn_time,
            tca_time=tca,
            propagate_func=propagate_satrec_single,
            target_miss_km=margin_km,
            dv_bound_km_s=0.002,
            penalty_lambda=100000.0,
            verbose=False
        )

        return {
            "success": proposal.success,
            "burn_time": proposal.burn_time.isoformat(),
            "tca_original": tca.isoformat(),
            "predicted_miss_km": proposal.predicted_miss_km,
            "dv_vector_m_s": (proposal.dv_km_s * 1000).tolist(),
            "dv_magnitude_m_s": proposal.dv_mag_m_s,
            "message": proposal.message
        }


# Singleton instance
maneuver_service = ManeuverService()
