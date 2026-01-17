from typing import List, Tuple, Dict
import numpy as np
from scipy.spatial import cKDTree
from datetime import datetime, timedelta, timezone

Vec3 = Tuple[float, float, float]  # 3D Vector Type (x, y, z)


def build_kdtree(states: Dict[int, Vec3]) -> cKDTree:
    """
    Builds a KD-Tree data structure from the given list of positions.
    KD-Tree enables fast search by partitioning space with hyperplanes.
    """
    positions = np.array(list(states.values()))
    tree = cKDTree(positions)
    return tree


def prune_pairs(states: Dict[int, Vec3], radius_km: float = 100.0) -> List[Tuple[int, int]]:
    """
    Pruning operation.
    Instead of brute-forcing all satellites against each other,
    this function finds only pairs that are within 'radius_km' of each other.
    Runs in O(N logN). Returns only close pairs.
    Args:
        states: Current positions of satellites in {sat_id: (x, y, z)} format.
        radius_km: Search radius (e.g., 100km)

    Returns:
        List[Tuple[int, int]]: List of candidate pairs with collision risk.
        Example: [(25544, 49044), (12345, 67890)]
    """

    if len(states) < 2:  # If there are fewer than 2 satellites, cannot compare, return empty list.
        return []

    # Convert dictionary structure to numpy arrays for scipy
    # sat_ids list and positions array indices must map one-to-one
    sat_ids = list(states.keys())
    positions = np.array([states[s] for s in sat_ids])

    # Check data shape, n satellites in 3D space
    if positions.ndim != 2 or positions.shape[0] < 2:
        return []

    # Indexing (KD-Tree Construction)
    # We arrange points in space into a tree structure for fast queries
    # For one epoch, the position map of all satellites is (sat_id → (x,y,z)).
    # TEME or ECEF can be used for positions, but ensure the same frame is used for each epoch

    tree = cKDTree(positions)
    pairs = set()  # pairs within radius, use set to avoid duplicates

    # For each satellite, ask "Give me neighbors within x km"
    for i, pos in enumerate(positions):
        idxs = tree.query_ball_point(pos, r=radius_km)
        for j in idxs:
            if j <= i:
                # j == i is the satellite itself, no need to check
                # j < i means if we found A,B pair, no need to check B,A again
                # Bu sayede işlem sayısı yarıya inecektir ve gereksiz kopayalar olmayacaktır
                continue
            # # İndeksleri gerçek uydu idlerine (NORAD ID) çevirip listeye ekle
            pairs.add((sat_ids[i], sat_ids[j]))
    # Set yapısını listeye çevirip döndür. Artık elimizde sadece
    # gerçekten birbirine yakın olan, SGP4 ile incelenmeye değer adaylar var.
    return list(pairs)

