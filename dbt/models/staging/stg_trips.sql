select
    trip_id,
    status,
    is_completed,
    request_at,
    dropoff_at,
    (request_at at time zone 'America/Los_Angeles')::date as request_date_la,
    trip_distance_miles,
    trip_duration_sec,
    original_fare_usd,
    surge_multiplier,
    is_surged,
    is_airport_trip
from {{ source('raw', 'trips') }}
