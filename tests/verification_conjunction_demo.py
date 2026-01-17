from skyfield.api import load, EarthSatellite
from skyfield.timelib import Time
import numpy as np
from datetime import datetime, timezone, timedelta

 # TLEs to be tested ---
 # sat1 = 25544 (ISS ZARYA)
 # sat2 = 49044 (ISS NAUKA)
tca_str = "2025-12-02T05:44:53.98501Z"
tle_iss_zarya = [
    'ISS (ZARYA)',
    '1 25544U 98067A   25335.57620886  .00008648  00000+0  16366-3 0  9990',
    '2 25544  51.6309 197.7449 0003647 190.9481 169.1428 15.49226524541123'
]
tle_iss_nauka = [
    'ISS (NAUKA)',
    '1 49044U 21066A   25335.57620886  .00008648  00000+0  16366-3 0  9996',
    '2 49044  51.6309 197.7449 0003647 190.9481 169.1428 15.49226524230444'
]


def verify_conjunction(tle1, tle2, tca_utc_str):
    """
    Propagates orbits around the given TLEs and estimated TCA time,
    and calculates the minimum distance (miss distance).
    """
    ts = load.timescale()

    # Convert TLEs to EarthSatellite objects
    sat1 = EarthSatellite(tle1[1], tle1[2], tle1[0], ts)
    sat2 = EarthSatellite(tle2[1], tle2[2], tle2[0], ts)

    # Create time steps (1-second intervals)
    # Create Skyfield time object
    # Define TCA time and surrounding time interval
    tca_dt = datetime.strptime(tca_utc_str, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)

    # Calculate every second from 5 minutes before to 5 minutes after TCA
    start_dt = tca_dt - timedelta(minutes=5)
    end_dt = tca_dt + timedelta(minutes=5)

    # Create all time points at 1-second intervals
    times_dt = []
    current_time = start_dt
    while current_time <= end_dt:
        times_dt.append(current_time)
        current_time += timedelta(seconds=1)

    if not times_dt:
        print("Error: Time interval could not be created.")
        return

    # Convert all created datetime objects to a single Skyfield time object
    times = ts.utc(times_dt)

    # Calculate positions
    # Geocentric positions (in km)
    p1 = sat1.at(times).position.km
    p2 = sat2.at(times).position.km

    # Find the vector difference between them
    difference = p1 - p2

    # Calculate the distance for each moment
    distances_km = np.sqrt(np.sum(difference ** 2, axis=0))

    # Find the minimum distance and time index
    min_distance_km = np.min(distances_km)
    min_index = np.argmin(distances_km)

    # Find the time when the minimum distance occurs
    tca_recalculated = times[min_index]

    print(f"--- Verification Results ({tle1[0]} vs {tle2[0]}) ---")
    print(f"Original TCA (Output): {tca_str}")
    print(f"Original Miss Distance:   {0.005401871371767645:.6f} km")
    print("-" * 50)
    print(f"Calculated Minimum Distance (SGP4): {min_distance_km:.6f} km")
    print(f"Calculated TCA (UTC):           {tca_recalculated.utc_strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} UTC")

    # Comparison
    tolerance = 0.01  # 10 meter tolerance
    if np.abs(min_distance_km - 0.00540187) < tolerance:
        print("\nResults appear CONSISTENT. The calculated distance is very close to the original output value.")
    else:
        print("\nResults are INCONSISTENT. The calculated distance is different from the original output value.")


# Script'i çalıştır
verify_conjunction(tle_iss_zarya, tle_iss_nauka, tca_str)