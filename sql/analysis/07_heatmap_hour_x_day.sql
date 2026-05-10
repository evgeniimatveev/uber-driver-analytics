-- Earnings heatmap: hour of day × day of week
-- This feeds the main dashboard heatmap visualization
-- dow: 0=Sunday, 1=Monday, ..., 6=Saturday

SELECT
    EXTRACT(DOW  FROM request_at AT TIME ZONE 'America/Los_Angeles')  AS day_of_week,
    EXTRACT(HOUR FROM request_at AT TIME ZONE 'America/Los_Angeles')  AS hour_of_day,
    COUNT(*)                              AS trips,
    ROUND(AVG(original_fare_usd), 2)      AS avg_fare_usd,
    ROUND(SUM(original_fare_usd), 2)      AS total_earned_usd
FROM trips
WHERE is_completed = true
GROUP BY 1, 2
ORDER BY 1, 2;
