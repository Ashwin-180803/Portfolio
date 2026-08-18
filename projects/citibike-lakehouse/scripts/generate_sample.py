"""Generate a small, slightly dirty Citi Bike sample so the pipeline has work to do."""

from __future__ import annotations

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "citibike_trips.csv"

STATIONS = [
    ("6140.05", "W 21 St & 6 Ave", 40.7418, -73.9945),
    ("5905.12", "Broadway & E 14 St", 40.7345, -73.9907),
    ("6753.08", "1 Ave & E 68 St", 40.7659, -73.9585),
    ("5470.10", "West St & Chambers St", 40.7175, -74.0134),
    ("6450.12", "8 Ave & W 31 St", 40.7502, -73.9978),
    ("5788.13", "Lafayette St & E 8 St", 40.7302, -73.9910),
    ("5905.14", "E 17 St & Broadway", 40.7370, -73.9901),
    ("6904.04", "Central Park S & 6 Ave", 40.7659, -73.9764),
    ("5573.05", "Pier 40 - Hudson River Park", 40.7276, -74.0115),
    ("4066.15", "Grand Army Plaza & Plaza St West", 40.6729, -73.9709),
    ("5453.07", "N 8 St & Driggs Ave", 40.7177, -73.9560),
    ("5525.04", "Bedford Ave & Nassau Ave", 40.7230, -73.9521),
    ("6717.06", "9 Ave & W 45 St", 40.7602, -73.9913),
    ("6551.09", "E 47 St & Park Ave", 40.7553, -73.9746),
    ("5303.06", "South End Ave & Liberty St", 40.7111, -74.0158),
]

TYPES = ["classic_bike", "electric_bike"]
MEMBERS = ["member", "casual"]


def main(n: int = 1200, seed: int = 42) -> None:
    rng = random.Random(seed)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    start_day = datetime(2024, 6, 1, 6, 0, 0)
    rows: list[dict[str, str]] = []

    for i in range(n):
        start_st = rng.choice(STATIONS)
        end_st = rng.choice(STATIONS)
        started = start_day + timedelta(
            days=rng.randint(0, 13),
            minutes=rng.randint(0, 16 * 60),
            seconds=rng.randint(0, 59),
        )
        duration = rng.randint(120, 2400)
        ended = started + timedelta(seconds=duration)
        ride_id = uuid.UUID(int=rng.getrandbits(128), version=4).hex[:16]
        rows.append(
            {
                "ride_id": ride_id,
                "rideable_type": rng.choice(TYPES),
                "started_at": started.strftime("%Y-%m-%d %H:%M:%S"),
                "ended_at": ended.strftime("%Y-%m-%d %H:%M:%S"),
                "start_station_name": start_st[1],
                "start_station_id": start_st[0],
                "end_station_name": end_st[1],
                "end_station_id": end_st[0],
                "start_lat": f"{start_st[2]:.4f}",
                "start_lng": f"{start_st[3]:.4f}",
                "end_lat": f"{end_st[2]:.4f}",
                "end_lng": f"{end_st[3]:.4f}",
                "member_casual": rng.choice(MEMBERS),
            }
        )

    # Inject the mess silver is supposed to catch.
    for row in rows[:15]:
        rows.append(row.copy())
    for row in rows[20:28]:
        row["end_station_id"] = ""
        row["end_station_name"] = ""
    for row in rows[30:36]:
        row["ended_at"] = row["started_at"]
    for row in rows[40:43]:
        started = datetime.strptime(row["started_at"], "%Y-%m-%d %H:%M:%S")
        row["ended_at"] = (started + timedelta(hours=30)).strftime("%Y-%m-%d %H:%M:%S")
    rows[50]["member_casual"] = "Member"
    rows[51]["rideable_type"] = "CLASSIC_BIKE"

    fieldnames = list(rows[0].keys())
    with OUT.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {len(rows)} rows → {OUT}")


if __name__ == "__main__":
    main()
