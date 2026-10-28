select
    wallet_id,
    trader_id,
    currency_id,
    address
from {{ ref('stg_wallets') }}