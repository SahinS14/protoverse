import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from typing import List, Tuple
import httpx
from backend.models.db import get_conn, init_db


# URL structure: gp.php?GROUP=<desired group>&FORMAT=tle

# Refactored URLs for Indian-priority and global scope
CELESTRAK_INDIA = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=TLE"
#CELESTRAK_INDIA = "https://celestrak.org/NORAD/elements/INDIA.txt"
CELESTRAK_ACTIVE = "https://celestrak.org/NORAD/elements/active.txt"
CELESTRAK_DEBRIS = "https://celestrak.org/NORAD/elements/debris.txt"


def fetch_tle_text(url: str) -> str:
    # Temporarily added because errors occurred after a certain number of requests (despite timeout)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 (AstroGuard-Platform/1.0)',
    }
    resp = httpx.get(url, headers=headers, timeout=20.0)
    resp.raise_for_status()
    return resp.text


def parse_tle_block(text: str) -> List[Tuple[str, str, str]]:
    """
    Each block consists of 3 lines: name, line1, line2.
    These blocks are parsed to make them processable.
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip() != ""]
    blocks = []
    i = 0
    while i + 2 < len(lines):
        name = lines[i]
        line1 = lines[i + 1]
        line2 = lines[i + 2]
        blocks.append((name, line1, line2))
        i += 3
    return blocks



def save_tles(blocks: List[Tuple[str, str, str]], source: str = "celestrak", country: str = "Global", priority: str = "SECONDARY"):
    # Persist data only inside the data/ directory
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    db_path = os.path.join(data_dir, 'sat_tles.db')
    conn = get_conn()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    for name, line1, line2 in blocks:
        cur.execute(
            "INSERT INTO raw_tles (sat_name, line1, line2, epoch, source, fetched_at, country, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, line1, line2, "", source, now, country, priority))
    conn.commit()
    conn.close()



def fetch_and_store():
    init_db()

    # Fetch Indian satellites (PRIMARY) - skip if not defined or not available
    india_blocks = []
    try:
        if 'CELESTRAK_INDIA' in globals():
            india_text = fetch_tle_text(CELESTRAK_INDIA)
            india_blocks = parse_tle_block(india_text)
            save_tles(india_blocks, source="celestrak_india", country="India", priority="PRIMARY")
    except Exception as e:
        print(f"Skipping India TLE fetch: {e}")

    active_text = fetch_tle_text(CELESTRAK_ACTIVE)
    active_blocks = parse_tle_block(active_text)
    save_tles(active_blocks, source="celestrak_active", country="Global", priority="SECONDARY")

    debris_text = fetch_tle_text(CELESTRAK_DEBRIS)
    debris_blocks = parse_tle_block(debris_text)
    save_tles(debris_blocks, source="celestrak_debris", country="Global", priority="SECONDARY")

    count = len(india_blocks) + len(active_blocks) + len(debris_blocks)
    return count


if __name__ == "__main__":
    n = fetch_and_store()
    print(f"{n} TLE records have been saved.")
