select trip_id from {{ ref('stg_trips') }}
where original_fare_usd < 0 or trip_distance_miles < 0
