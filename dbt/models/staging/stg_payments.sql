select
    payment_id,
    trip_uuid,
    local_amount as amount_usd,
    category,
    classification,
    paid_at
from {{ source('raw', 'payments') }}
