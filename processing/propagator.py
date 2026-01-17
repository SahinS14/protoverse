from sgp4.api import Satrec
from sgp4.api import jday
from datetime import datetime, timezone
from typing import List, Tuple


def tle_to_satrec(line1: str, line2: str) -> Satrec:
    """
    Converts the given TLE (Two-Line Element) lines 1 and 2
    into a sgp4 Satrec (Satellite Record) object.
    This object contains all orbital parameters required for propagation.
    """
    return Satrec.twoline2rv(line1, line2)


def utc_dt_to_jd(dt: datetime) -> Tuple[float, float]:
    """
    SGP4 algorithm expects time in Julian Date format.
    Therefore, UTC -> JD conversion is performed.
    """
    jd, fr = jday(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second + dt.microsecond * 1e-6  # Add microseconds converted to seconds
    )
    return jd, fr


def propagate_satrec(sat: Satrec, times_utc: List[datetime]):
    """
    Propagates the given Satrec object for each UTC time point in the list
    using the SGP4 algorithm.

    :param sat: Satrec object created by tle_to_satrec
    :param times_utc: List of UTC datetimes for position/velocity calculation
    :return: List of dictionaries containing position (r, in km, TEME) and
             velocity (v, in km/s, TEME) for each time point.
    """
    results = []
    for t in times_utc:
        # Convert UTC time to Julian Date
        jd, fr = utc_dt_to_jd(t)

        # Run SGP4 algorithm
        # e: Error code (0 = Success)
        # r: Position vector [Rx, Ry, Rz] (km, TEME coordinate system)
        # v: Velocity vector [Vx, Vy, Vz] (km/s, TEME coordinate system)
        e, r, v = sat.sgp4(jd, fr)

        if e != 0:
            # If SGP4 returns an error code (e.g., -1 = satellite decayed, -2 = satellite raised)
            # raise a RuntimeError.
            raise RuntimeError(f"SGP4 error code {e}")

        # Sonuçları listeye ekle
        # r, v değerleri TEME (True Equator, Mean Equinox) koordinat sistemindedir.
        results.append({
            "time": t,
            "r_km": r,  # Konum (km)
            "v_km_s": v  # Hız (km/s)
        })
    return results