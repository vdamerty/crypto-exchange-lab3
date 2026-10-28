select
    trader_id,
    trim(full_name) as full_name,
    lower(trim(email)) as email,
    registered_at
from {{ source('raw_crypto', 'traders') }}