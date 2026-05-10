-- Airport vs regular trips comparison
-- Finding: airport trips pay 72% more per ride ($35 vs $20)
-- but only 18 out of 3,451 completed trips were airport trips

SELECT
    is_airport_trip,
    COUNT(*)                                      AS trips,
    ROUND(AVG(original_fare_usd), 2)              AS avg_fare_usd,
    ROUND(AVG(trip_distance_miles), 2)            AS avg_miles,
    ROUND(AVG(trip_duration_sec / 60.0), 1)       AS avg_duration_min,
    ROUND(AVG(original_fare_usd
              / NULLIF(trip_duration_sec / 3600.0, 0)), 2) AS earnings_per_hour
FROM trips
WHERE is_completed = true
GROUP BY is_airport_trip;
