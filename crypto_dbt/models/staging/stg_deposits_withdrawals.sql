select
    movement_id,
    trader_id,
    currency_id,
    wallet_id,
    lower(trim(movement_type)) as movement_type,
    amount,
    created_at
from {{ source('raw_crypto', 'deposits_withdrawals') }}