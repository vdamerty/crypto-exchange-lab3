select
    currency_id,
    upper(trim(symbol)) as symbol,
    trim(currency_name) as currency_name,
    reference_price_usd
from {{ source('raw_crypto', 'currencies') }}