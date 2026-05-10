-- Ratings distribution
-- Note: ratings file has no trip_id link — aggregate stats only

SELECT
    five_star_rating                         AS rating,
    COUNT(*)                                 AS count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS pct
FROM ratings
GROUP BY 1
ORDER BY 1 DESC;
