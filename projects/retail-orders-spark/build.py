"""Run the synthetic retail case study in local Apache Spark."""
import csv
from pathlib import Path

from pyspark.sql import SparkSession

ROOT = Path(__file__).resolve().parent


def save(name, df):
    rows = df.collect()
    with (ROOT / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(df.columns)
        writer.writerows(rows)
    return rows


def main():
    spark = (SparkSession.builder.master("local[2]").appName("retail-order-analytics")
             .config("spark.ui.enabled", "false")
             .config("spark.sql.shuffle.partitions", "2").getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    try:
        schemas = {
            "orders": "order_id INT, customer_id STRING, status STRING",
            "products": "product_id STRING, category STRING",
            "lines": "order_id INT, line_id INT, product_id STRING, quantity INT, unit_price_cents INT, unit_cost_cents INT, discount_pct INT",
        }
        for table, schema in schemas.items():
            (spark.read.option("header", True).schema(schema).option("mode", "FAILFAST")
             .csv(str(ROOT / (table + ".csv"))).createOrReplaceTempView(table))
        # Assert unique dimension keys and one row per order-line before joining.
        for table, keys in (("orders", ["order_id"]), ("products", ["product_id"]),
                            ("lines", ["order_id", "line_id"])):
            frame = spark.table(table)
            assert frame.count() == frame.select(*keys).distinct().count(), table
        spark.sql("""
            SELECT o.order_id, l.line_id, p.category,
                   CAST(ROUND(l.quantity * l.unit_price_cents * (100-l.discount_pct) / 100.0) AS BIGINT) AS net_sales_cents,
                   CAST(l.quantity * l.unit_cost_cents AS BIGINT) AS cost_cents
            FROM lines l JOIN orders o ON o.order_id = l.order_id
                         JOIN products p ON p.product_id = l.product_id
            WHERE o.status = 'complete'
        """).createOrReplaceTempView("completed_lines")
        assert spark.table("completed_lines").count() == 10
        queries = [q.strip() for q in (ROOT / "analysis.sql").read_text().split(";") if q.strip()]
        category = save("category_results.csv", spark.sql(queries[0]))
        repeat = save("customer_results.csv", spark.sql(queries[1]))
        assert sum(row.net_sales_cents for row in category) == 109750
        assert repeat[0].customers == 5 and repeat[0].repeat_customers == 3
        print(category, repeat)
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
