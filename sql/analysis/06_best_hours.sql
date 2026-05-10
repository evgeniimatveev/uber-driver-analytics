-- Best hours of the day by average fare and total earnings
-- Use for deciding when to go online

SELECT
    EXTRACT(HOUR FROM request_at AT TIME ZONE 'America/Los_Angeles')  AS hour_of_day,
    COUNT(*)                              AS trips,
    ROUND(AVG(original_fare_usd), 2)      AS avg_fare_usd,
    ROUND(SUM(original_fare_usd), 2)      AS total_earned_usd
FROM trips
WHERE is_completed = true
GROUP BY 1
ORDER BY avg_fare_usd DESC;
