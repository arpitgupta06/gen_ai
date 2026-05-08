from __future__ import annotations

import argparse
import os
import random
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import psycopg
from faker import Faker


PROJECT_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_DIR / ".env"
INIT_SQL_FILE = Path(__file__).resolve().parent / "init" / "01_seed.sql"

SEGMENTS = ("retail", "wholesale", "premium")
ORDER_STATUSES = ("pending", "completed", "refunded", "cancelled")
REGIONS = ("North", "South", "East", "West")
CATEGORIES = (
    ("Laptops", "Electronics"),
    ("Phones", "Electronics"),
    ("Accessories", "Electronics"),
    ("Furniture", "Home"),
    ("Kitchen", "Home"),
    ("Fitness", "Sports"),
    ("Books", "Media"),
)


def load_env_file(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def connect() -> psycopg.Connection:
    load_env_file(ENV_FILE)

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB", "datatalk"),
        user=os.getenv("POSTGRES_USER", "datatalk"),
        password=os.getenv("POSTGRES_PASSWORD", "datatalk"),
    )


def money(min_value: int, max_value: int) -> Decimal:
    return Decimal(str(round(random.uniform(min_value, max_value), 2)))


def random_date(days_back: int = 365) -> date:
    return date.today() - timedelta(days=random.randint(0, days_back))


def reset_tables(cur: psycopg.Cursor) -> None:
    cur.execute(
        """
        truncate table order_items, orders, products, categories, customers
        restart identity cascade
        """
    )


def create_schema(cur: psycopg.Cursor) -> None:
    cur.execute(INIT_SQL_FILE.read_text())


def seed_categories(cur: psycopg.Cursor) -> list[int]:
    category_ids = []

    for name, parent_category in CATEGORIES:
        cur.execute(
            """
            insert into categories (name, parent_category)
            values (%s, %s)
            returning category_id
            """,
            (name, parent_category),
        )
        category_ids.append(cur.fetchone()[0])

    return category_ids


def seed_customers(cur: psycopg.Cursor, fake: Faker, count: int) -> list[int]:
    customer_ids = []

    for _ in range(count):
        cur.execute(
            """
            insert into customers (name, email, city, region, signup_date, segment)
            values (%s, %s, %s, %s, %s, %s)
            returning customer_id
            """,
            (
                fake.name(),
                fake.unique.email(),
                fake.city(),
                random.choice(REGIONS),
                random_date(),
                random.choice(SEGMENTS),
            ),
        )
        customer_ids.append(cur.fetchone()[0])

    return customer_ids


def seed_products(
    cur: psycopg.Cursor,
    fake: Faker,
    count: int,
    category_ids: list[int],
) -> list[tuple[int, Decimal]]:
    products = []

    for _ in range(count):
        price = money(100, 5000)
        cost = (price * Decimal(str(random.uniform(0.45, 0.8)))).quantize(Decimal("0.01"))

        cur.execute(
            """
            insert into products (name, category_id, price, cost, sku, is_active)
            values (%s, %s, %s, %s, %s, %s)
            returning product_id, price
            """,
            (
                fake.catch_phrase()[:255],
                random.choice(category_ids),
                price,
                cost,
                fake.unique.bothify(text="SKU-####-????").upper(),
                random.choices((True, False), weights=(90, 10), k=1)[0],
            ),
        )
        products.append(cur.fetchone())

    return products


def seed_orders(
    cur: psycopg.Cursor,
    fake: Faker,
    count: int,
    customer_ids: list[int],
    products: list[tuple[int, Decimal]],
) -> list[int]:
    order_ids = []

    for _ in range(count):
        cur.execute(
            """
            insert into orders (
                customer_id,
                order_date,
                status,
                shipping_city,
                shipping_region
            )
            values (%s, %s, %s, %s, %s)
            returning order_id
            """,
            (
                random.choice(customer_ids),
                random_date(180),
                random.choices(ORDER_STATUSES, weights=(15, 65, 10, 10), k=1)[0],
                fake.city(),
                random.choice(REGIONS),
            ),
        )
        order_id = cur.fetchone()[0]
        order_ids.append(order_id)

        item_count = random.randint(1, min(4, len(products)))
        for product_id, unit_price in random.sample(products, item_count):
            cur.execute(
                """
                insert into order_items (
                    order_id,
                    product_id,
                    quantity,
                    unit_price,
                    discount
                )
                values (%s, %s, %s, %s, %s)
                """,
                (
                    order_id,
                    product_id,
                    random.randint(1, 5),
                    unit_price,
                    random.choice((Decimal("0.00"), Decimal("5.00"), Decimal("10.00"))),
                ),
            )

    return order_ids


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate fake seed data for Datatalk.")
    parser.add_argument("--customers", type=int, default=100)
    parser.add_argument("--products", type=int, default=50)
    parser.add_argument("--orders", type=int, default=250)
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append data instead of truncating existing rows first.",
    )
    parser.add_argument(
        "--skip-schema",
        action="store_true",
        help="Skip creating tables from data/init/01_seed.sql before seeding.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.customers < 1:
        raise ValueError("--customers must be at least 1")
    if args.products < 1:
        raise ValueError("--products must be at least 1")
    if args.orders < 0:
        raise ValueError("--orders cannot be negative")

    fake = Faker("en_IN")
    Faker.seed(42)
    random.seed(42)

    with connect() as conn:
        with conn.cursor() as cur:
            if not args.skip_schema:
                create_schema(cur)

            if not args.append:
                reset_tables(cur)

            category_ids = seed_categories(cur)
            customer_ids = seed_customers(cur, fake, args.customers)
            products = seed_products(cur, fake, args.products, category_ids)
            order_ids = seed_orders(cur, fake, args.orders, customer_ids, products)

    print(f"Seeded {len(category_ids)} categories")
    print(f"Seeded {len(customer_ids)} customers")
    print(f"Seeded {len(products)} products")
    print(f"Seeded {len(order_ids)} orders")


if __name__ == "__main__":
    main()
