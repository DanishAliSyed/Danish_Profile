-- Synthetic inputs; no source data or personal information.
WITH district AS (
    SELECT 'North' AS region, 'Cedar' AS district_name, 400 AS covered, 1000 AS eligible,
           200 AS farmer_premium, 300 AS state_premium, 500 AS central_premium
    UNION ALL SELECT 'North', 'Maple', 300, 500, 150, 200, 350
    UNION ALL SELECT 'South', 'Oak', 450, 750, 180, 300, 420
    UNION ALL SELECT 'South', 'Pine', 150, 250, 60, 90, 150
)
SELECT region, SUM(covered) AS covered_farmers, SUM(eligible) AS eligible_farmers,
       ROUND(100.0 * SUM(covered) / NULLIF(SUM(eligible), 0), 2) AS coverage_pct,
       SUM(farmer_premium + state_premium + central_premium) AS total_premium,
       ROUND(100.0 * SUM(state_premium + central_premium) /
             NULLIF(SUM(farmer_premium + state_premium + central_premium), 0), 2)
           AS public_premium_share_pct
FROM district
GROUP BY region
ORDER BY coverage_pct DESC, region;
