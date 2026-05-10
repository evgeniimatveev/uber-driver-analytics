-- Real hourly rate by year
-- Key metric: earnings per hour of actual drive time (not including wait)
-- Trend: $68/hr (2022) → $105/hr (2025)

SELECT
    EXTRACT(YEAR FROM request_at AT TIME ZONE 'America/Los_Angeles')           AS year,
    COUNT(*)                                                                    AS trips,
    ROUND(AVG(original_fare_usd), 2)                                           AS avg_fare_usd,
    ROUND(AVG(trip_distance_miles), 2)                                         AS avg_miles,
    ROUND(AVG(trip_duration_sec / 60.0), 1)                                    AS avg_duration_min,
    ROUND(AVG(original_fare_usd / NULLIF(trip_duration_sec / 3600.0, 0)), 2)   AS earnings_per_hour
FROM trips
WHERE is_completed = true
  AND trip_duration_sec > 0
GROUP BY 1
ORDER BY 1;
