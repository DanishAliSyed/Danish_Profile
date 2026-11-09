"""Fetch a fixed historical block window from Mempool's public Bitcoin API."""
import csv
import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
START = datetime(2024, 4, 18, tzinfo=timezone.utc)
END = datetime(2024, 4, 23, tzinfo=timezone.utc)
LOW, HIGH = 839670, 840452  # Padding on both sides of the UTC window.


def fetch(height):
    url = f"https://mempool.space/api/v1/blocks/{height}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=18) as response:
                return json.load(response)
        except (TimeoutError, urllib.error.URLError) as exc:
            if isinstance(exc, urllib.error.HTTPError):
                if exc.code == 429:
                    raise SystemExit("Mempool rate limit reached. Wait before re-running.") from exc
                if exc.code not in (500, 502, 503, 504):
                    raise
            if attempt == 2:
                raise
            time.sleep(2 ** (attempt + 1))


def main():
    blocks = {}
    for height in range(HIGH, LOW - 1, -15):
        batch = fetch(height)
        assert [b["height"] for b in batch] == list(range(height, height - 15, -1))
        for b in batch:
            blocks[b["height"]] = b
        time.sleep(1.1)
    ordered = [blocks[i] for i in range(LOW, HIGH + 1)]
    assert all(b["previousblockhash"] == a["id"] for a, b in zip(ordered, ordered[1:]))
    ts = lambda b: datetime.fromtimestamp(b["timestamp"], timezone.utc)
    assert all(ts(b) < START for b in ordered[:15])
    assert all(ts(b) >= END for b in ordered[-15:])
    selected = [b for b in ordered if START <= ts(b) < END]
    assert len({b["id"] for b in selected}) == len(selected)
    path = ROOT / "blocks.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["height", "block_hash", "timestamp_utc", "tx_count", "weight_wu",
                    "total_fee_sat", "mempool_median_fee_sat_vb"])
        for b in selected:
            w.writerow([b["height"], b["id"], ts(b).isoformat(), b["tx_count"], b["weight"],
                        b["extras"]["totalFees"], b["extras"]["medianFee"]])
    print(f"Wrote {len(selected)} blocks to {path.name}")


if __name__ == "__main__":
    main()
