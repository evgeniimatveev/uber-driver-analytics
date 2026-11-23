-- One row per month (Los Angeles local date) of completed trips.
select
    date_trunc('month', request_date_la)::date as month,
    count(*)                                   as completed_trips,
    round(sum(original_fare_usd), 2)           as gross_fare_usd,
    round(avg(original_fare_usd), 2)           as avg_fare_usd,
    round(100.0 * avg(is_surged::int), 1)      as surged_pct,
    round(100.0 * avg(is_airport_trip::int), 1) as airport_pct
from {{ ref('stg_trips') }}
where is_completed
group by 1
