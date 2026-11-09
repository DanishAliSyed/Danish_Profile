-- Query 1: contribution margin by category, at the order-line grain.
SELECT category, COUNT(*) AS order_lines, COUNT(DISTINCT order_id) AS orders,
       SUM(net_sales_cents) AS net_sales_cents, SUM(cost_cents) AS cost_cents,
       SUM(net_sales_cents - cost_cents) AS profit_cents,
       ROUND(100.0 * SUM(net_sales_cents - cost_cents) /
             NULLIF(SUM(net_sales_cents), 0), 2) AS margin_pct
FROM completed_lines
GROUP BY category
ORDER BY profit_cents, category;

-- Query 2: repeat customers, counted at the order-header grain.
WITH customer_orders AS (
    SELECT customer_id, COUNT(*) AS orders
    FROM orders
    WHERE status = 'complete'
    GROUP BY customer_id
)
SELECT COUNT(*) AS customers, SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END) AS repeat_customers,
       ROUND(100.0 * SUM(CASE WHEN orders > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_pct
FROM customer_orders;
