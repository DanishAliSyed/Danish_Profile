-- One observation per row in UCI bank-full.csv.
-- The same client may appear more than once; there is no client ID.
WITH segments AS (
    SELECT 'Prior campaign outcome' AS dimension, poutcome AS segment, subscribed
    FROM campaign
    UNION ALL
    SELECT 'Current campaign contacts',
           CASE WHEN campaign = 1 THEN '1'
                WHEN campaign <= 3 THEN '2–3'
                WHEN campaign <= 6 THEN '4–6' ELSE '7+' END,
           subscribed
    FROM campaign
)
SELECT dimension, segment, COUNT(*) AS observations,
       SUM(subscribed) AS subscriptions,
       ROUND(100.0 * SUM(subscribed) / COUNT(*), 2) AS subscription_rate_pct
FROM segments
GROUP BY dimension, segment
ORDER BY dimension, subscription_rate_pct DESC, segment;
