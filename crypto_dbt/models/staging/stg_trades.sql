select
    trade_id,
    trader_id,
    currency_id,
    wallet_id,
    lower(trim(side)) as side,
    quantity,
    price_usd,
    executed_at
from {{ source('raw_crypto', 'trades') }}