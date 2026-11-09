"""Build the dashboard and aggregate CSV from UCI's original bank-full.csv."""
import argparse
import csv
import html
import io
import sqlite3
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UCI = "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip"


def source(path):
    if path:
        return Path(path).read_text(encoding="utf-8-sig")
    with urllib.request.urlopen(UCI, timeout=30) as response:
        with zipfile.ZipFile(io.BytesIO(response.read())) as outer:
            with zipfile.ZipFile(io.BytesIO(outer.read("bank.zip"))) as inner:
                return inner.read("bank-full.csv").decode("utf-8-sig")


def analyse(raw):
    reader = csv.DictReader(io.StringIO(raw), delimiter=";")
    with sqlite3.connect(":memory:") as db:
        db.execute("""CREATE TABLE campaign (
            campaign INTEGER CHECK(campaign >= 1), poutcome TEXT,
            subscribed INTEGER CHECK(subscribed IN (0, 1)))""")
        db.executemany("INSERT INTO campaign VALUES (?, ?, ?)", (
            (int(row["campaign"]), row["poutcome"], {"yes": 1, "no": 0}[row["y"]])
            for row in reader
        ))
        total, successes = db.execute("SELECT COUNT(*), SUM(subscribed) FROM campaign").fetchone()
        result = db.execute((ROOT / "analysis.sql").read_text()).fetchall()
    return total, successes, result


def dashboard(total, successes, rows):
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 630" role="img" aria-labelledby="title desc">',
           '<title id="title">Bank Campaign Analytics</title>',
           '<desc id="desc">Term deposit subscription rates by prior campaign outcome and current campaign contact count, with segment sizes.</desc>']

    def rect(x, y, w, h, fill, rx=0):
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"/>')

    def text(x, y, value, size=14, fill="#183247", weight=400):
        svg.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,Arial,sans-serif" font-size="{size}" fill="{fill}" font-weight="{weight}">{html.escape(str(value))}</text>')

    rect(0, 0, 1000, 630, "#edf3f7")
    rect(0, 0, 1000, 151, "#122b40")
    text(36, 33, "PORTFOLIO CASE STUDY  /  RETAIL BANKING", 13, "#88e0d3", 700)
    text(36, 79, "Bank Campaign Analytics", 37, "#ffffff", 700)
    text(36, 118, "How does term deposit subscription vary with contact history?", 17, "#d4e6f3")
    for i, (label, value) in enumerate([
        ("Campaign observations", f"{total:,}"),
        ("Subscriptions", f"{successes:,}"),
        ("Overall subscription rate", f"{successes / total:.1%}"),
    ]):
        x = 36 + i * 314
        rect(x, 169, 300, 79, "#ffffff", 10)
        text(x + 15, 194, label, 13, "#405a70", 700)
        text(x + 15, 228, value, 27, weight=700)

    specs = [
        (36, "Prior campaign outcome", ["success", "failure", "other", "unknown"]),
        (507, "Current campaign contacts", ["1", "2–3", "4–6", "7+"]),
    ]
    for x, dimension, order in specs:
        rect(x, 267, 457, 230, "#ffffff", 10)
        text(x + 15, 296, dimension, 19, weight=700)
        text(x + 15, 318, "Subscription rate  •  same 0–70% scale", 12, "#486277")
        found = {s: (n, k, p) for d, s, n, k, p in rows if d == dimension}
        for i, segment in enumerate(order):
            if segment not in found:
                continue
            n, k, p = found[segment]
            y = 350 + 36 * i
            text(x + 15, y + 8, segment.capitalize(), 13, weight=700)
            rect(x + 110, y - 5, 192, 13, "#e7eef3", 4)
            rect(x + 110, y - 5, round(192 * p / 70, 1), 13, "#177f77", 4)
            text(x + 312, y + 8, f"{p:.1f}%  ·  n={n:,}", 12)

    rect(36, 513, 928, 75, "#dbecef", 10)
    text(51, 539, "How to use this", 15, weight=700)
    text(51, 561, "Use prior outcomes to define audiences for a test. Contact counts are retrospective;", 14)
    text(51, 579, "these rates do not show that more calls caused lower conversion.", 14)
    text(36, 614, "Danish Syed  /  Data: UCI Bank Marketing, Moro, Rita & Cortez (CC BY 4.0)", 12, "#486277")
    svg.append("</svg>")
    return "\n".join(svg) + "\n"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", help="Optional local copy of the original UCI bank-full.csv")
    args = parser.parse_args()
    total, successes, rows = analyse(source(args.csv))
    for dimension in {row[0] for row in rows}:
        segment_rows = [r for r in rows if r[0] == dimension]
        assert sum(r[2] for r in segment_rows) == total
        assert sum(r[3] for r in segment_rows) == successes
    with (ROOT / "campaign_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["dimension", "segment", "observations", "subscriptions", "subscription_rate_pct"])
        writer.writerows(rows)
    (ROOT / "dashboard.svg").write_text(dashboard(total, successes, rows), encoding="utf-8")
    print(f"{total:,} observations, {successes:,} subscriptions ({successes/total:.2%})")


if __name__ == "__main__":
    main()
