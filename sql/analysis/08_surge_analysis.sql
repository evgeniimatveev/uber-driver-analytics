-- Surge pricing impact
-- Finding: 231 surge trips (6.7%) earned $1,531 in extra surge pay
-- Surge avg fare $27.27 vs $20.04 regular (+36%)

SELECT
    is_surged,
    COUNT(*)                                          AS trips,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_total,
    ROUND(AVG(surge_multiplier), 3)                   AS avg_multiplier,
    ROUND(AVG(original_fare_usd), 2)                  AS avg_fare_usd,
    ROUND(SUM(surge_fare_usd)::numeric, 2)            AS total_surge_bonus_usd
FROM trips
WHERE is_completed = true
GROUP BY is_surged;
