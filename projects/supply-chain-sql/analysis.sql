-- Synthetic orders and line items.
WITH orders AS (
    SELECT 1 AS order_id, 'East' AS region, 'Standard' AS shipping_mode, 3 AS promised_days, 5 AS actual_days
    UNION ALL SELECT 2, 'East', 'Standard', 3, 2
    UNION ALL SELECT 3, 'East', 'Express', 1, 1
    UNION ALL SELECT 4, 'West', 'Standard', 3, 3
    UNION ALL SELECT 5, 'West', 'Express', 1, 2
    UNION ALL SELECT 6, 'West', 'Express', 1, 1
), line_items AS (
    SELECT 1 AS order_id, 80 AS sales
    UNION ALL SELECT 1, 20
    UNION ALL SELECT 2, 50
    UNION ALL SELECT 3, 75
    UNION ALL SELECT 4, 60
    UNION ALL SELECT 5, 45
    UNION ALL SELECT 5, 15
    UNION ALL SELECT 6, 30
), order_sales AS (
    SELECT order_id, SUM(sales) AS total_sales
    FROM line_items
    GROUP BY order_id
), by_mode AS (
    SELECT o.region, o.shipping_mode, COUNT(*) AS orders,
           SUM(CASE WHEN o.actual_days > o.promised_days THEN 1 ELSE 0 END) AS late_orders,
           SUM(COALESCE(s.total_sales, 0)) AS total_sales
    FROM orders o LEFT JOIN order_sales s ON s.order_id = o.order_id
    GROUP BY o.region, o.shipping_mode
), rates AS (
    SELECT *, 100.0 * late_orders / NULLIF(orders, 0) AS late_rate
    FROM by_mode
)
SELECT region, shipping_mode, orders, late_orders, total_sales,
       ROUND(late_rate, 2) AS late_pct,
       DENSE_RANK() OVER (PARTITION BY region ORDER BY late_rate DESC) AS late_rate_rank
FROM rates
ORDER BY region, late_rate_rank, shipping_mode;
