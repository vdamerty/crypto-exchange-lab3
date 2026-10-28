select
    wallet_id,
    trader_id,
    currency_id,
    trim(address) as address
from {{ source('raw_crypto', 'wallets') }}