"""Reconcile the Spark output against an independent standard-library calculation."""
import csv
import math
from collections import defaultdict
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parent

with (ROOT / "blocks.csv").open(newline="", encoding="utf-8") as f:
    grouped = defaultdict(list)
    for row in csv.DictReader(f):
        grouped[row["timestamp_utc"][:10]].append(row)

with (ROOT / "daily_results.csv").open(newline="", encoding="utf-8") as f:
    result = {row["day_utc"]: row for row in csv.DictReader(f)}

assert set(grouped) == set(result) == {f"2024-04-{d:02d}" for d in range(18, 23)}
for day, rows in grouped.items():
    actual = result[day]
    fees = sum(int(r["total_fee_sat"]) for r in rows)
    weight = sum(int(r["weight_wu"]) for r in rows)
    tx = sum(int(r["tx_count"]) - 1 for r in rows)
    assert (int(actual["blocks"]), int(actual["confirmed_transactions"]), int(actual["total_fee_sat"])) == (len(rows), tx, fees)
    assert math.isclose(float(actual["fees_per_block_vbyte"]), 4 * fees / weight, abs_tol=0.00051)
    assert math.isclose(float(actual["median_block_fee_rate_sat_vb"]),
                        median(float(r["mempool_median_fee_sat_vb"]) for r in rows), abs_tol=0.00051)
print("All five UTC days reconcile with the source rows.")
