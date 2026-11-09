"""Aggregate the bundled block window in Spark and redraw the dashboard."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession

ROOT = Path(__file__).resolve().parent


def analyse():
    spark = (SparkSession.builder.master("local[2]").appName("bitcoin-fee-spike")
             .config("spark.ui.enabled", "false")
             .config("spark.sql.session.timeZone", "UTC")
             .config("spark.sql.shuffle.partitions", "2").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    try:
        schema = """height INT, block_hash STRING, timestamp_utc TIMESTAMP, tx_count INT,
                    weight_wu LONG, total_fee_sat LONG, mempool_median_fee_sat_vb DOUBLE"""
        blocks = (spark.read.option("header", True).option("mode", "FAILFAST").schema(schema)
                  .csv(str(ROOT / "blocks.csv")))
        blocks.createOrReplaceTempView("blocks")
        n = blocks.count()
        assert n == blocks.select("height").distinct().count() == blocks.select("block_hash").distinct().count()
        assert blocks.where("timestamp_utc IS NULL OR tx_count IS NULL OR weight_wu IS NULL OR "
                            "total_fee_sat IS NULL OR mempool_median_fee_sat_vb IS NULL OR "
                            "tx_count < 1 OR weight_wu <= 0 OR total_fee_sat < 0 OR mempool_median_fee_sat_vb < 0").count() == 0
        daily = spark.sql((ROOT / "analysis.sql").read_text())
        rows = daily.collect()
        assert len(rows) == 5 and sum(row.blocks for row in rows) == n
        assert sum(row.total_fee_sat for row in rows) == blocks.groupBy().sum("total_fee_sat").first()[0]
        return daily.columns, rows
    finally:
        spark.stop()


def draw(rows):
    days = [r.day_utc.strftime("%b %d") for r in rows]
    peak = max(range(len(rows)), key=lambda i: rows[i].total_fee_sat)
    figs = [
        ("Confirmed transactions", [r.confirmed_transactions / 1000 for r in rows], "thousand"),
        ("Total transaction fees", [float(r.total_fee_btc) for r in rows], "BTC"),
        ("Fees per block vbyte", [float(r.fees_per_block_vbyte) for r in rows], "sat/vB of block footprint"),
    ]
    fig = plt.figure(figsize=(11, 6.1), facecolor="#edf4f7")
    fig.text(.055, .925, "Bitcoin Network Activity | PySpark", fontsize=26, weight="bold", color="#142f43")
    fig.text(.055, .865, "April 18–22, 2024  /  Confirmed blocks grouped by UTC day", fontsize=13, color="#47657a")
    for i, (name, series, unit) in enumerate(figs):
        ax = fig.add_axes([.055 + .313*i, .31, .267, .43], facecolor="#ffffff")
        ax.bar(days, series, color=["#dc8154" if j == peak else "#177e74" for j in range(5)])
        ax.set_title(name, loc="left", pad=19, fontsize=13, fontweight="bold", color="#142f43")
        ax.set_ylim(0, max(series) * 1.21)
        ax.set_xticks(range(5), [d[-2:] for d in days], fontsize=9)
        ax.set_xlabel("April day (UTC)", fontsize=9)
        ax.set_yticks([])
        ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
        for j, v in enumerate(series):
            ax.text(j, v + max(series)*.025, f"{v:,.0f}", ha="center", fontsize=9, color="#142f43")
        ax.text(0, 1.015, unit, transform=ax.transAxes, fontsize=8, color="#47657a", va="bottom")
    r = rows[peak]
    fig.text(.055, .175, f"{days[peak]}: {r.confirmed_transactions:,} confirmed transactions, "
             f"{float(r.total_fee_btc):,.1f} BTC in fees.", fontsize=15, weight="bold", color="#142f43")
    fig.text(.055, .116, "Confirmed volume measures what fit in blocks. It does not measure all waiting demand.",
             fontsize=12, color="#47657a")
    fig.text(.055, .049, "Danish Syed  /  Source: Mempool public Bitcoin block API  /  No price or investment analysis",
             fontsize=10, color="#47657a")
    fig.savefig(ROOT / "dashboard.png", dpi=125, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    columns, rows = analyse()
    with (ROOT / "daily_results.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)
    draw(rows)
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
