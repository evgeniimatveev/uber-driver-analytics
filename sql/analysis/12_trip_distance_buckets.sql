-- Trip distance distribution: which distance range is most profitable?
-- Helps answer: are short or long trips better per hour?

SELECT
    CASE
        WHEN trip_distance_miles < 2   THEN '0-2 mi (short)'
        WHEN trip_distance_miles < 5   THEN '2-5 mi'
        WHEN trip_distance_miles < 10  THEN '5-10 mi'
        WHEN trip_distance_miles < 20  THEN '10-20 mi'
        ELSE '20+ mi (long)'
    END                                                             AS distance_bucket,
    COUNT(*)                                                        AS trips,
    ROUND(AVG(original_fare_usd), 2)                               AS avg_fare_usd,
    ROUND(AVG(trip_duration_sec / 60.0), 1)                        AS avg_duration_min,
    ROUND(AVG(original_fare_usd
              / NULLIF(trip_duration_sec / 3600.0, 0)), 2)         AS earnings_per_hour
FROM trips
WHERE is_completed = true
  AND trip_distance_miles > 0
  AND trip_duration_sec > 0
GROUP BY 1
ORDER BY AVG(trip_distance_miles);
