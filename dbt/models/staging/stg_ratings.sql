select
    rating_id,
    five_star_rating as stars
from {{ source('raw', 'ratings') }}
