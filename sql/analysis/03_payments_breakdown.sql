-- Full breakdown of all payment categories (all years)
-- Key findings:
--   driver_payment_fares  = gross earned
--   commission            = Uber's cut (~32.3%)
--   existing_driver_incentive = bonuses ($6,362 total)
--   tip                   = rider tips ($3,049 total)

SELECT
    category,
    COUNT(*)                              AS transactions,
    ROUND(SUM(local_amount)::numeric, 2)  AS total_usd,
    ROUND(AVG(local_amount)::numeric, 2)  AS avg_per_transaction
FROM payments
GROUP BY category
ORDER BY ABS(SUM(local_amount)) DESC;
