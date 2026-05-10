-- Gross earnings and trip count by year
-- Shows overall business growth over time

SELECT
    EXTRACT(YEAR FROM request_at AT TIME ZONE 'America/Los_Angeles')  AS year,
    COUNT(*)                                                           AS total_trips,
    ROUND(SUM(original_fare_usd)::numeric, 2)                         AS gross_earnings_usd
FROM trips
WHERE is_completed = true
GROUP BY 1
ORDER BY 1;
