-- One eligible, randomized subscriber per row after the follow-up window ends.
-- Use assigned arm even if the reminder was not delivered (intention-to-treat).
SELECT arm,
       COUNT(*) AS assigned_subscribers,
       SUM(renewed_30d) AS renewals_30d,
       1.0 * SUM(renewed_30d) / COUNT(*) AS renewal_rate
FROM experiment
GROUP BY arm
ORDER BY arm;
