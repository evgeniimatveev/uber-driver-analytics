-- Singular test: any row returned is a failure.
select trip_id from {{ ref('stg_trips') }}
where is_completed and dropoff_at is null
