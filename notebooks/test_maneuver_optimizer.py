import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ingest.tle_fetcher import fetch_and_store
from backend.models.db import get_conn
from processing.propagator import tle_to_satrec
from processing.propagate_wrapper import propagate_satrec_single
from planner.optimizer import find_minimal_dv
from datetime import datetime, timedelta, timezone

fetch_and_store()
conn = get_conn()
cur = conn.cursor()
# Test için daha önce kullandığım uydu çiftini alalım
# sat1 id 25544 (ISS), sat2 49044
cur.execute("SELECT id, sat_name, line1, line2 FROM raw_tles WHERE sat_name LIKE '%ISS%' OR sat_name LIKE '%ZARYA%' LIMIT 2")
rows = cur.fetchall()
if len(rows) < 2:
    print("En az 2 uydu bulunmalı, seçiminizi değiştirebilirsiniz")
    exit(1)

row1 = rows[0]
row2 = rows[1]
satrec1 = tle_to_satrec(row1["line1"], row1["line2"])
satrec2 = tle_to_satrec(row2["line1"], row2["line2"])
now = datetime.now(timezone.utc)

# Propagate işlemi yapılacak "now" anına kadar
r1 = propagate_satrec_single(satrec1, now)
r2 = propagate_satrec_single(satrec2, now)
r1_f = propagate_satrec_single(satrec1, now + timedelta(seconds=1))
r2_f = propagate_satrec_single(satrec2, now + timedelta(seconds=1))
v1 = (r1_f - r1) / 1.0
v2 = (r2_f - r2) / 1.0

# t* hesabı
# burada sadece etst yaptığımız için analitik yöntem kullandık
# sonrasında gerçek aşamada conjunction.py de yazdığımız refine edilmiş metot kullanılacak
r = r2 - r1
v = v2 - v1
tstar = - (r.dot(v)) / (v.dot(v))
tca_est = now + timedelta(seconds=tstar)

print("Estimated TCA (calculated by analytic method):", tca_est.isoformat())
# burn_time should be chosen a bit before TCA, e.g., 600 seconds before
burn_time = tca_est - timedelta(seconds=600)
print("Burn time:", burn_time.isoformat())
# optimizer for target_miss_km=1.0
proposal = find_minimal_dv(satrec2, satrec1, burn_time, tca_est, propagate_satrec_single, target_miss_km=1.0, dv_bound_km_s=0.005, penalty_lambda=500.0, verbose=True)
print("Proposal:", proposal)

"""
The correctness of the results obtained here has been tested with verification_conjunction_demo.py.
The results have been found to be consistent. The accuracy of the data has been tested and reported using the SGP4 model and an independent library 'skyfield'.
"""