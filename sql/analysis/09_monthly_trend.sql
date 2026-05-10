-- Monthly earnings trend (for time series chart in dashboard)

SELECT
    DATE_TRUNC('month', request_at AT TIME ZONE 'America/Los_Angeles') AS month,
    COUNT(*)                                                            AS trips,
    ROUND(SUM(original_fare_usd)::numeric, 2)                          AS gross_usd,
    ROUND(AVG(original_fare_usd), 2)                                   AS avg_fare_usd,
    ROUND(AVG(trip_distance_miles), 2)                                 AS avg_miles
FROM trips
WHERE is_completed = true
GROUP BY 1
ORDER BY 1;
