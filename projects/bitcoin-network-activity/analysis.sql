-- One row per mined block. Exclude the coinbase from transaction counts.
-- Block vbytes use weight / 4, which includes block overhead and the coinbase.
SELECT TO_DATE(timestamp_utc) AS day_utc,
       COUNT(*) AS blocks,
       SUM(tx_count - 1) AS confirmed_transactions,
       SUM(weight_wu) AS block_weight_wu,
       SUM(total_fee_sat) AS total_fee_sat,
       ROUND(SUM(total_fee_sat) / 100000000.0, 8) AS total_fee_btc,
       ROUND(4.0 * SUM(total_fee_sat) / SUM(weight_wu), 3) AS fees_per_block_vbyte,
       ROUND(MEDIAN(mempool_median_fee_sat_vb), 3) AS median_block_fee_rate_sat_vb,
       ROUND(SUM(total_fee_sat) / NULLIF(SUM(tx_count - 1), 0), 2) AS mean_fee_per_transaction_sat
FROM blocks
GROUP BY TO_DATE(timestamp_utc)
ORDER BY day_utc;
