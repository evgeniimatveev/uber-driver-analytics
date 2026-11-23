-- Payment line items rolled up by category (fares, commission, tips, incentives...).
select
    category,
    count(*)                    as line_items,
    round(sum(amount_usd), 2)   as total_usd
from {{ ref('stg_payments') }}
group by 1
