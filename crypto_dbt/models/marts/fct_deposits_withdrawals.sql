select
    movement_id,
    trader_id,
    currency_id,
    wallet_id,
    movement_type,
    amount,
    case
        when movement_type = 'deposit' then amount
        when movement_type = 'withdrawal' then -amount
    end as signed_amount,
    created_at
from {{ ref('stg_deposits_withdrawals') }}