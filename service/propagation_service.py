from datetime import datetime, timedelta
from typing import List, Dict, Any
from service.tle_service import tle_service
from processing.propagator import propagate_satrec
from processing.coord_utils import teme_pos_to_latlon


class PropagationService:
    """
    This service simulates the movement of a satellite (Lat/Lon/Alt) over a specified time interval.
    Unlike collision analysis, the purpose here is 'Visualization'.
    Used to plot the satellite's orbit on the frontend.
    """

    def propagate_satellite(self, sat_id: int, start_time: datetime, end_time: datetime, step_seconds: int = 60) -> \
            List[Dict[str, Any]]:
        """
        Propagates the specified satellite between start and end times in 'step_seconds' increments.
        Args:
            sat_id: Satellite database ID.
            start_time: Simulation start.
            end_time: Simulation end.
            step_seconds: Precision setting. (e.g., 60s = one point per minute).
                Lower value = Smoother line but higher CPU load.
        """

        # Get the satellite's sgp4 model from the TLE service
        satrec = tle_service.get_satrec_by_id(sat_id)
        if not satrec:
            raise ValueError(f"Satellite not found with this id. ID: {sat_id}")

        # Create time steps
        # SGP4 libraries are usually written for batch (vectorized) processing
        # So we first fill a list with all the time points to be calculated
        times = []
        current = start_time
        while current <= end_time:
            times.append(current)
            current += timedelta(seconds=step_seconds)

        # Orbit Propagation - TEME Coordinates
        # The processing.propagator module uses the SGP4 algorithm to
        # calculate the satellite's X, Y, Z positions (Earth-Centered Inertial - TEME) at these times
        states = propagate_satrec(satrec, times)

        results = []
        for state in states:
            # SGP4 output is raw space coordinates
            r_km = state["r_km"]
            t_utc = state["time"]

            # Coordinate Transformation (TEME -> Lat/Lon/Alt)
            # Converts to latitude and longitude values understandable on Earth's surface
            # This function takes Earth's rotation (GST - Greenwich Sidereal Time) into account
            # and projects the fixed point in space onto the rotating Earth's map
            lat, lon, alt = teme_pos_to_latlon(r_km, t_utc)

            results.append({
                "time": t_utc.isoformat(),
                # SGP4 or numpy sometimes returns 'tuple' or 'numpy array'
                # JSON serializer does not recognize these, so we convert to standard Python list
                "position_km": list(r_km),
                "velocity_km_s": list(state["v_km_s"]),
                "lat": lat,
                "lon": lon,
                "alt_km": alt
            })

        return results


# Singleton instance
propagation_service = PropagationService()
