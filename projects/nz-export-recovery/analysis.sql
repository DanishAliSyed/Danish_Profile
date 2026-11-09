-- Daily NZD goods exports. Never add overlapping published rollups.
WITH periods AS (
    SELECT yr, country, commodity, SUM(nzd) AS value_nzd, COUNT(*) AS days
    FROM daily
    WHERE yr IN (2019, 2020, 2021)
      AND month_day BETWEEN '01-01' AND '08-31'
      AND month_day <> '02-29'
      AND mode = 'All'
      AND (country = 'All' OR commodity = 'All')
      AND country <> 'Total (excluding China)'
    GROUP BY yr, country, commodity
)
SELECT CASE WHEN country = 'All' AND commodity = 'All' THEN 'Total'
            WHEN country = 'All' THEN 'Commodity' ELSE 'Partner' END AS series,
       CASE WHEN country = 'All' THEN commodity ELSE country END AS label,
       yr, value_nzd, days
FROM periods
ORDER BY series, label, yr;
