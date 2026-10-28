select
    trade_id,
    trader_id,
    currency_id,
    wallet_id,
    side,
    quantity,
    price_usd,
    quantity * price_usd as total_usd,
    executed_at
from {{ ref('stg_trades') }}