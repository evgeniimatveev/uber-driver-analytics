select
    payment_id,
    trip_uuid,
    local_amount as amount_usd,
    -- Uber export leaves category empty for 26 rows (2022 fuel surcharge etc.); keep them
    coalesce(category, 'uncategorized') as category,
    classification,
    paid_at
from {{ source('raw', 'payments') }}
