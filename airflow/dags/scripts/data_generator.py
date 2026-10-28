import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal


def generate_data():
    rng = random.Random(9)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    # 100 трейдерів.
    traders = [
        (
            trader_id,
            f"Trader {trader_id}",
            f"trader{trader_id}@example.com",
            start,
        )
        for trader_id in range(1, 101)
    ]

    # 5 криптовалют. Ціни штучні, для навчального прикладу.
    currencies = [
        (1, "BTC", "Bitcoin", Decimal("68000.00")),
        (2, "ETH", "Ethereum", Decimal("3500.00")),
        (3, "USDT", "Tether", Decimal("1.00")),
        (4, "SOL", "Solana", Decimal("150.00")),
        (5, "ADA", "Cardano", Decimal("0.50")),
    ]

    # Для кожного трейдера створюємо по одному гаманцю
    # для кожної з п'яти валют. Разом 500 гаманців.
    wallets = []
    wallet_id = 1

    for trader in traders:
        for currency in currencies:
            wallets.append(
                (
                    wallet_id,
                    trader[0],
                    currency[0],
                    f"demo_wallet_{wallet_id}",
                )
            )
            wallet_id += 1

    # 2000 угод. Трейдер і валюта відповідають гаманцю.
    trades = []

    for trade_id in range(1, 2001):
        wallet = rng.choice(wallets)
        wallet_id, trader_id, currency_id, address = wallet

        quantity = Decimal(rng.randint(1, 10000)) / Decimal("1000")
        price_usd = currencies[currency_id - 1][3]

        trades.append(
            (
                trade_id,
                trader_id,
                currency_id,
                wallet_id,
                rng.choice(["buy", "sell"]),
                quantity,
                price_usd,
                start + timedelta(minutes=trade_id * 10),
            )
        )

    # 1000 операцій введення або виведення коштів.
    deposits_withdrawals = []

    for movement_id in range(1, 1001):
        wallet = rng.choice(wallets)
        wallet_id, trader_id, currency_id, address = wallet

        amount = Decimal(rng.randint(1, 50000)) / Decimal("1000")

        deposits_withdrawals.append(
            (
                movement_id,
                trader_id,
                currency_id,
                wallet_id,
                rng.choice(["deposit", "withdrawal"]),
                amount,
                start + timedelta(minutes=movement_id * 17),
            )
        )

    return {
        "traders": traders,
        "currencies": currencies,
        "wallets": wallets,
        "trades": trades,
        "deposits_withdrawals": deposits_withdrawals,
    }


def load_data_to_dwh():
    import os
    import psycopg2
    from psycopg2.extras import execute_values

    data = generate_data()

    connection = psycopg2.connect(
        host=os.environ["DWH_HOST"],
        port=int(os.environ["DWH_PORT"]),
        dbname=os.environ["DWH_DB"],
        user=os.environ["DWH_USER"],
        password=os.environ["DWH_PASSWORD"],
        connect_timeout=10,
    )

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE SCHEMA IF NOT EXISTS raw;

                    CREATE TABLE IF NOT EXISTS raw.traders (
                        trader_id BIGINT,
                        full_name TEXT,
                        email TEXT,
                        registered_at TIMESTAMPTZ
                    );

                    CREATE TABLE IF NOT EXISTS raw.currencies (
                        currency_id BIGINT,
                        symbol TEXT,
                        currency_name TEXT,
                        reference_price_usd NUMERIC(20, 8)
                    );

                    CREATE TABLE IF NOT EXISTS raw.wallets (
                        wallet_id BIGINT,
                        trader_id BIGINT,
                        currency_id BIGINT,
                        address TEXT
                    );

                    CREATE TABLE IF NOT EXISTS raw.trades (
                        trade_id BIGINT,
                        trader_id BIGINT,
                        currency_id BIGINT,
                        wallet_id BIGINT,
                        side TEXT,
                        quantity NUMERIC(20, 8),
                        price_usd NUMERIC(20, 8),
                        executed_at TIMESTAMPTZ
                    );

                    CREATE TABLE IF NOT EXISTS raw.deposits_withdrawals (
                        movement_id BIGINT,
                        trader_id BIGINT,
                        currency_id BIGINT,
                        wallet_id BIGINT,
                        movement_type TEXT,
                        amount NUMERIC(20, 8),
                        created_at TIMESTAMPTZ
                    );
                """)

                cursor.execute("""
                    TRUNCATE TABLE
                        raw.trades,
                        raw.deposits_withdrawals,
                        raw.wallets,
                        raw.currencies,
                        raw.traders;
                """)

                for table_name, rows in data.items():
                    execute_values(
                        cursor,
                        f"INSERT INTO raw.{table_name} VALUES %s",
                        rows,
                    )

        # Виводимо результат лише після успішного commit.
        for table_name, rows in data.items():
            print(f"Завантажено raw.{table_name}: {len(rows)}")

    finally:
        connection.close()


if __name__ == "__main__":
    load_data_to_dwh()