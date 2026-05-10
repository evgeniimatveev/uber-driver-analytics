-- Top 20 single best earning days
-- Great for spotting what made those days special (events, holidays, surge)

SELECT
    DATE(request_at AT TIME ZONE 'America/Los_Angeles')  AS trip_date,
    TO_CHAR(request_at AT TIME ZONE 'America/Los_Angeles', 'Day')  AS day_name,
    COUNT(*)                              AS trips,
    ROUND(SUM(original_fare_usd)::numeric, 2)   AS total_earned_usd,
    ROUND(AVG(original_fare_usd), 2)            AS avg_fare_usd,
    SUM(CASE WHEN is_surged THEN 1 ELSE 0 END)  AS surge_trips
FROM trips
WHERE is_completed = true
GROUP BY 1, 2
ORDER BY total_earned_usd DESC
LIMIT 20;
