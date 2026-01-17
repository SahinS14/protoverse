from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import Tuple, Callable
import numpy as np
from scipy.optimize import minimize
from astropy.time import Time
import astropy.units as u
from poliastro.bodies import Earth
from poliastro.twobody import Orbit

"""
If we fired the engines now and added X to the velocity vector,
how far would we be from the other satellite at TCA? This is the question we want to answer.
By calling the simulation function with scipy.optimize, we aim to find both the target distance and the vector that keeps deltaV (fuel) low.
"""


@dataclass
class ManeuverProposal:
    dv_km_s: np.ndarray  # 3 boyutlu deltaV vektörü (vx, vy, vz)
    dv_mag_km_s: float  # deltaV büyüklüğü km/s, yakıt maliyeti
    dv_mag_m_s: float  # deltaV büyüklüğü m/s
    burn_time: datetime  # manevranın yapılacağı zaman
    predicted_tca: datetime  # tahmini en yakın yaklaşım zamanı
    predicted_miss_km: float  # tahmini miss distance (km)
    predicted_rel_vel_km_s: float
    success: bool  # başarı durumu
    message: str  # açıklama


def rv_to_orbit(r_km: np.ndarray, v_km_s: np.ndarray, epoch_dt: datetime) -> Orbit:
    """
    Creates a 'poliastro.Orbit' object from position (r) and velocity (v) vectors.
    Used to solve the post-maneuver orbit as a two-body problem.
    """
    t = Time(epoch_dt.replace(tzinfo=None).strftime('%Y-%m-%dT%H:%M:%S.%f'), format="isot", scale="utc")
    # Vektörleri birimli hale getirip Dünya merkezli yörünge nesnesi oluştur
    return Orbit.from_vectors(Earth, r_km * u.km, v_km_s * u.km / u.s, epoch=t)


def propagate_orbit_to(orbit: Orbit, target_dt: datetime) -> np.ndarray:
    """
    Propagates a given orbit (Orbit object in our case)
    to the target time (target_dt) and returns the new position.
    """
    t_target = Time(target_dt.replace(tzinfo=None).strftime('%Y-%m-%dT%H:%M:%S.%f'), format="isot", scale="utc")
    tof = (t_target - orbit.epoch).to(u.s)  # time of flight
    new_orbit = orbit.propagate(tof)
    return np.array(new_orbit.r.to(u.km).value, dtype=float)


def compute_miss_distance_after_burn(
    satrec_target, satrec_our, burn_time: datetime,
    dv_km_s: np.ndarray, tca_time: datetime,
    propagate_func: Callable[[object, datetime], np.ndarray]
) -> Tuple[float, float]:
    """
    Simulation function that calculates the new miss distance at TCA
    when a specific DeltaV (dv_km_s) maneuver is performed.
    * Go to the burn time with SGP4.
    * Add deltav to the velocity vector (impulsive maneuver)
    * Propagate the new orbit to TCA using Keplerian (poliastro).
    """

    # Find current position and velocity at burn time
    # To find the velocity vector, take two positions 1 second apart and subtract (simple derivative)
    # Note: SGP4's own velocity output can also be used, but this method is more general.
    r_b = np.array(propagate_func(satrec_our, burn_time), dtype=float)
    r_b1 = np.array(propagate_func(satrec_our, burn_time + timedelta(seconds=1)), dtype=float)
    v_b = (r_b1 - r_b) / 1.0

    # Maneuver v' = v + deltav operation
    v_new = v_b + np.array(dv_km_s, dtype=float)
    orbit_new = rv_to_orbit(r_b, v_new, burn_time)
    r_our_tca = propagate_orbit_to(orbit_new, tca_time)
    # Find the position of the other (risk) satellite at TCA
    # The other satellite does not maneuver, so use the original SGP4 propagator
    r_other_tca = np.array(propagate_func(satrec_target, tca_time), dtype=float)

    # Calculate the Euclidean distance (miss distance) between the two positions
    miss = float(np.linalg.norm(r_other_tca - r_our_tca))

    # Relative velocity calculation
    # Estimate velocity vectors by looking 1 second after TCA
    dt = 1.0
    r_our_tca_f = propagate_orbit_to(orbit_new, tca_time + timedelta(seconds=dt))
    r_other_tca_f = np.array(propagate_func(satrec_target, tca_time + timedelta(seconds=dt)), dtype=float)
    rel_vel = float(np.linalg.norm((r_other_tca_f - r_other_tca) - (r_our_tca_f - r_our_tca)) / dt)

    return miss, rel_vel


def find_minimal_dv(
    satrec_target,
    satrec_our,
    burn_time: datetime,
    tca_time: datetime,
    propagate_func: Callable[[object, datetime], np.ndarray],
    target_miss_km: float = 2.0,  # target safe distance (e.g., 2 km)
    dv_bound_km_s: float = 0.001,  # allowed max deltav
    penalty_lambda: float = 1e6,  # penalty coefficient
    verbose: bool = False
) -> ManeuverProposal:
    """
    Finds the minimum DeltaV vector required to achieve the target 'miss distance'.
    Applies unconstrained optimization method.
    """

    # Objective Function
    # The optimizer will try to bring the value returned by this function close to zero
    def obj_func(dv_flat):
        dv = np.array(dv_flat)  # anlık deltav değeri
        # Run the simulation, check what the new distance will be if maneuver is performed
        miss, _ = compute_miss_distance_after_burn(
            satrec_target, satrec_our, burn_time, dv, tca_time, propagate_func
        )
        # Cost
        norm = float(np.linalg.norm(dv))

        # Penalty
        # If below the target distance, apply a huge penalty
        # Penalty = λ * max(0, Target - Miss) ^ 2
        # If miss > target (safe), max(0, negative) -> 0, no penalty added.
        # Only fuel cost (norm) is minimized.
        penalty = penalty_lambda * max(0.0, (target_miss_km - miss)) ** 2
        return norm + penalty

    # Initial guess (0,0,0) - No maneuver
    x0 = np.zeros(3, dtype=float)
    # Search bounds: Delta-V can be max 'dv_bound_km_s' in each axis.
    bounds = [(-dv_bound_km_s, dv_bound_km_s)] * 3

    # OPTIMIZATION:
    try:
        # L-BFGS-B: Box-constrained optimization algorithm
        res = minimize(
            obj_func,
            x0,
            bounds=bounds,
            method="L-BFGS-B",
            # ftol: Function tolerance. Balance between precision and speed.
            options={"ftol": 1e-9, "maxiter": 1000}
        )
    except Exception as e:
        return ManeuverProposal(
            dv_km_s=x0, dv_mag_km_s=0.0, dv_mag_m_s=0.0,
            burn_time=burn_time, predicted_tca=tca_time, predicted_miss_km=0.0,
            predicted_rel_vel_km_s=0.0, success=False, message=f"Optimizer Error: {str(e)}"
        )

    # Optimization completed, get the best result
    dv_opt = np.array(res.x, dtype=float)
    # With this best result, run the simulation one last time to get final values
    miss_opt, relv_opt = compute_miss_distance_after_burn(
        satrec_target, satrec_our, burn_time, dv_opt, tca_time, propagate_func
    )

    # Did the found distance reach the target (within tolerance)?
    is_success = miss_opt >= (target_miss_km - 0.001)

    return ManeuverProposal(
        dv_km_s=dv_opt,
        dv_mag_km_s=float(np.linalg.norm(dv_opt)),
        dv_mag_m_s=float(np.linalg.norm(dv_opt) * 1000.0),
        burn_time=burn_time,
        predicted_tca=tca_time,
        predicted_miss_km=miss_opt,
        predicted_rel_vel_km_s=relv_opt,
        success=is_success,
        message="Optimization finished" if res.success else str(res.message)
    )
