select
    trader_id,
    full_name,
    email,
    registered_at
from {{ ref('stg_traders') }}