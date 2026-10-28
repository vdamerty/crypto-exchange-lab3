select
    currency_id,
    symbol,
    currency_name,
    reference_price_usd
from {{ ref('stg_currencies') }}