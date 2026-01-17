from typing import Tuple, Optional
from datetime import datetime, timedelta
import numpy as np
from scipy.optimize import minimize_scalar
from dataclasses import dataclass


@dataclass
class Conjunction:
    """
    Summary data of a detected close approach event.
    DTO to be sent to other parts of the system (Database, API).
    """
    sat1: int  # 1st satellite NORAD id
    sat2: int  # 2nd satellite NORAD id
    tca: datetime  # time of closest approach
    miss_distance_km: float  # expected minimum distance between 2 objects in km
    rel_velocity_km_s: float  # relative velocity at closest approach in km/s
    score: float  # risk score between 0.0 and 1.0
    event_type: str = "COLLISION"  # 'COLLISION' or 'DOCKING'


def analytic_tca_and_miss(r1, v1, r2, v2, epoch) -> Tuple[float, float]:
    """
    TCA estimation with linear assumption.
    Assuming satellites move linearly for a short period,
    the time of closest approach (t*) is calculated analytically.
    This method is very fast but only used for initial filtering.
    Input:
        r1, v1: Position and velocity vectors of satellite 1
        r2, v2: Position and velocity vectors of satellite 2
    Output:
        tstar: How many seconds after the reference time (epoch) will the closest approach occur?
        miss: Estimated distance at that moment (km)
    """
    r = r2 - r1
    v = v2 - v1
    vv = np.dot(v, v)


    if vv < 1e-12:  # If relative velocity is 0 (satellites are parallel and moving at the same speed)
        return 0.0, float(np.linalg.norm(r))

    # t* = - (r . v) / (v . v)
    # This formula gives the time when the minimum distance occurs (by taking the derivative).
    tstar = - np.dot(r, v) / vv

    # Estimated position difference at that moment: r(t) = r0 + v * t
    r_t = r + v * tstar
    miss = np.linalg.norm(r_t)  # Euclidean distance
    return float(tstar), float(miss)



# Refinement Phase
def refine_tca_with_propagator(satrec1, satrec2, epoch, t_est_seconds, propagate_func, search_radius=600.0):
    """
    Precise search with SGP4 to correct the linear assumption.
    Around the t* time found by the analytic method,
    searches for the minimum distance using real orbital mechanics (SGP4).

    Why is it necessary?
    Orbits are not straight lines, but ellipses. The linear method can have 5-10 second errors.
    Part of the 5-minute difference mentioned in the report comes from here.
    """


    # Cost function to be minimized
    def dist_sq_offset(dt_offset):
        try:
            t = epoch + timedelta(seconds=(t_est_seconds + dt_offset))
            # SGP4 is called
            r1 = propagate_func(satrec1, t)
            r2 = propagate_func(satrec2, t)
            # Return the squared distance
            # Square root is costly, so use square in optimization
            return float(np.sum((r2 - r1) ** 2))
        except Exception:
            return 1e9  # In case of error, return a very large distance so it won't be selected

    # Usage of minimize_scalar optimization technique
    # Search range: +/- 600 seconds (10 min) around the estimated time
    res = minimize_scalar(dist_sq_offset, bounds=(-search_radius, search_radius), method='bounded',
                          options={'xatol': 0.01})  # 0.01 second precision

    tca = epoch + timedelta(seconds=(t_est_seconds + res.x))

    # Propagation
    try:
        # Recalculate positions for the best tca
        r1 = propagate_func(satrec1, tca)
        r2 = propagate_func(satrec2, tca)
        miss = float(np.linalg.norm(r2 - r1))  # final precise distance

        # Relative velocity calculation
        dt = 0.1
        r1_f = propagate_func(satrec1, tca + timedelta(seconds=dt))
        r2_f = propagate_func(satrec2, tca + timedelta(seconds=dt))
        rel_vel = float(np.linalg.norm((r2_f - r1_f - (r2 - r1)) / dt))
    except Exception:
        # If propagation fails, return safe values
        return tca, 99999.9, 0.0

    return tca, miss, rel_vel


    
# Workflow
def compute_conjunction_for_pair(satrec1, satrec2, ref_epoch, r1, v1, r2, v2, propagate_func,
                                 analytic_window_sec=7200.0) -> Optional[Conjunction]:
    """
    Main function that analyzes the collision risk between two satellites.
    Algorithm:
        1. Fast Analytic Filter: If the linear calculation finds the satellites too far apart, stop processing.
        2. Precise Refinement: If close, use SGP4 and optimization to find the exact time/distance.
        3. Scoring: Assign a risk score based on distance.
        4. Classification: Is it a collision or docking?
    """
    try:
        # First step: linear estimation
        tstar, miss = analytic_tca_and_miss(r1, v1, r2, v2, ref_epoch)
        MONITORING_THRESHOLD_KM = 75.0  # Below this distance is worth monitoring
        CRITICAL_DISTANCE_KM = 10.0  # This distance is "Red Alert"

        # Analytic filtering, optimization, pruning
        # If the closest approach is too far in the future (>2 hours) or the distance is too large (>150km)
        # do not process in detail, avoid wasting resources
        if abs(tstar) > analytic_window_sec or miss > (MONITORING_THRESHOLD_KM * 2):
            return Conjunction(
                sat1=getattr(satrec1, 'satnum', -1),
                sat2=getattr(satrec2, 'satnum', -1),
                tca=ref_epoch + timedelta(seconds=tstar),
                miss_distance_km=float(miss),
                rel_velocity_km_s=float(np.linalg.norm(v2 - v1)),
                score=0.0,
                event_type="COLLISION"
            )

        # If there is potential risk, do precise calculation (refinement)
        tca, miss_refined, rel_vel = refine_tca_with_propagator(
            satrec1, satrec2, ref_epoch, tstar, propagate_func, search_radius=600.0
        )

        # Score the risk
        if miss_refined > MONITORING_THRESHOLD_KM:
            normalized_score = 0.0
        elif miss_refined <= CRITICAL_DISTANCE_KM:
            normalized_score = 1.0
        else:
            normalized_score = (MONITORING_THRESHOLD_KM - miss_refined) / (
                        MONITORING_THRESHOLD_KM - CRITICAL_DISTANCE_KM)
            normalized_score = max(0.0, min(1.0, normalized_score))

        # DOCKING analysis
        # In the report, ISS modules were seen to approach each other as close as 5 meters (0.005 km).
        # This is not a collision, but formation flying. To distinguish this:
        # Criteria: Distance < 1 km AND Relative Velocity < 10 m/s (0.01 km/s)
        is_docking = (miss_refined < 1.0) and (rel_vel < 0.01)
        final_event_type = "DOCKING" if is_docking else "COLLISION"

        # If docking, the risk score is technically high (very close)
        # but since the type is different, alarms can be disabled.
        if is_docking:
            normalized_score = 1.0

        return Conjunction(
            sat1=getattr(satrec1, 'satnum', -1),
            sat2=getattr(satrec2, 'satnum', -1),
            tca=tca,
            miss_distance_km=miss_refined,
            rel_velocity_km_s=rel_vel,
            score=normalized_score,
            event_type=final_event_type
        )
    except Exception as e:
        # In case of any unexpected error, return None; the service layer will log this
        print(f"Calculation error: {e}")
        return None