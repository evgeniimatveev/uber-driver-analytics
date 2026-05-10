-- Uber effective commission rate by year
-- Shows how much % Uber takes from gross fares each year

SELECT
    EXTRACT(YEAR FROM paid_at)                          AS year,
    ROUND(SUM(CASE WHEN category = 'driver_payment_fares'
                   THEN local_amount ELSE 0 END)::numeric, 2)  AS gross_fares,
    ROUND(ABS(SUM(CASE WHEN category = 'commission'
                       THEN local_amount ELSE 0 END))::numeric, 2) AS commission_paid,
    ROUND(
        ABS(SUM(CASE WHEN category = 'commission' THEN local_amount ELSE 0 END))
        / NULLIF(SUM(CASE WHEN category = 'driver_payment_fares' THEN local_amount ELSE 0 END), 0)
        * 100, 1
    )                                                   AS commission_pct,
    ROUND(SUM(CASE WHEN category = 'existing_driver_incentive'
                   THEN local_amount ELSE 0 END)::numeric, 2)  AS incentives,
    ROUND(SUM(CASE WHEN category = 'tip'
                   THEN local_amount ELSE 0 END)::numeric, 2)  AS tips
FROM payments
WHERE paid_at IS NOT NULL
GROUP BY 1
ORDER BY 1;
