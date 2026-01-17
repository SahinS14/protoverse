from sgp4.api import Satrec, jday
from datetime import datetime
import numpy as np


"""
Converts the given datetime to Julian Date.
Propagates the satellite at that moment using the SGP4 model.
Returns the satellite's position vector (x, y, z – km) as a numpy array.
"""


def propagate_satrec_single(satrec: Satrec, dt: datetime) -> np.ndarray:
    jd, fr = jday(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second + dt.microsecond * 1e-6)
    err, r, v = satrec.sgp4(jd, fr)
    if err != 0:
        raise RuntimeError(f"SGP4 error: {err}")
    return np.array(r, dtype=float)
