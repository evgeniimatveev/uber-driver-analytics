"""
Uber Driver Analytics — Data Ingestion
Loads 3 CSVs into PostgreSQL via SQLAlchemy.

Run: python ingestion/load_data.py
"""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ── Config ────────────────────────────────────────────────────────────────────

load_dotenv()

DB_URL = (
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

DATA_DIR = Path(__file__).parent.parent / "data"
SCHEMA_FILE = Path(__file__).parent.parent / "sql" / "schema.sql"


# ── Helpers ───────────────────────────────────────────────────────────────────

def to_bool(series: pd.Series) -> pd.Series:
    """Convert Uber's 'true'/'false' strings to Python bool."""
    return series.map({"true": True, "false": False, True: True, False: False})


def print_stats(name: str, df: pd.DataFrame) -> None:
    print(f"  [{name}] {len(df):,} rows  |  {df.shape[1]} columns")


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_trips(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)

    bool_cols = [
        "is_surged", "has_destination", "is_pool_matched", "is_completed",
        "is_flat_rate", "is_cash_trip", "has_driver_upfront_fare",
        "is_multidestination", "is_scheduled_trip", "is_airport_trip",
        "is_directed_dispatch_trip",
    ]
    for col in bool_cols:
        df[col] = to_bool(df[col])

    ts_cols = {
        "request_timestamp_utc": "request_at",
        "begintrip_timestamp_utc": "begintrip_at",
        "dropoff_timestamp_utc": "dropoff_at",
    }
    for raw, clean in ts_cols.items():
        df[clean] = pd.to_datetime(df[raw], utc=True, errors="coerce")

    rename = {
        "trip_duration_seconds": "trip_duration_sec",
        "fare_duration_minutes": "fare_duration_min",
        "wait_duration_minutes": "wait_duration_min",
        "eta": "eta_seconds",
    }
    df = df.rename(columns=rename)

    keep = [
        "city_name", "currency_code", "timezone", "flow_type",
        "product_type_name", "global_product_name", "license_plate",
        "driver_trip_number", "vehicle_trip_number",
        "request_at", "begintrip_at", "dropoff_at",
        "eta_seconds", "trip_distance_miles", "trip_duration_sec",
        "fare_distance_miles", "fare_duration_min", "wait_duration_min",
        "status", "is_completed", "is_flat_rate", "is_cash_trip",
        "is_surged", "is_pool_matched", "has_destination",
        "has_driver_upfront_fare", "is_multidestination",
        "is_scheduled_trip", "is_airport_trip", "is_directed_dispatch_trip",
        "surge_multiplier", "driver_surge_multiplier", "guaranteed_surge_multiplier",
        "original_fare_usd", "base_fare_usd", "surge_fare_usd",
        "per_mile_fare_usd", "per_minute_fare_usd",
        "minimum_fare_roundup_usd", "wait_time_fare_usd",
        "long_distance_surcharge_usd", "toll_amount_usd",
        "booking_fee_usd", "service_fee_usd", "cancellation_fee_usd",
        "driver_upfront_fare_usd", "promotion_usd", "credits_usd",
        "driver_cancellation_reason", "cancellation_type",
        "ufp_type", "concierge_source_type",
    ]
    return df[keep]


def load_payments(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)

    df = df.rename(columns={
        "City Name":       "city_name",
        "Trip UUID":       "trip_uuid",
        "Local Amount":    "local_amount",
        "Currency Code":   "currency_code",
        "Classification":  "classification",
        "Category":        "category",
        "Local Timestamp": "paid_at",
    })

    df["paid_at"] = pd.to_datetime(df["paid_at"], errors="coerce")
    return df


def load_ratings(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={"five_star_rating": "five_star_rating"})
    df["five_star_rating"] = pd.to_numeric(df["five_star_rating"], errors="coerce")
    return df.dropna(subset=["five_star_rating"]).astype({"five_star_rating": int})


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    engine = create_engine(DB_URL)

    print("=== Uber Analytics — Data Ingestion ===\n")

    # 1. Run schema DDL
    print("→ Running schema.sql ...")
    with engine.begin() as conn:
        conn.execute(text(SCHEMA_FILE.read_text()))
    print("  Schema created.\n")

    # 2. Load CSVs
    trips_path    = DATA_DIR / "driver_lifetime_trips.csv"
    payments_path = DATA_DIR / "driver_payments.csv"
    ratings_path  = DATA_DIR / "driver_lifetime_ratings_received.csv"

    print("→ Reading CSVs ...")
    trips    = load_trips(trips_path)
    payments = load_payments(payments_path)
    ratings  = load_ratings(ratings_path)

    print_stats("trips",    trips)
    print_stats("payments", payments)
    print_stats("ratings",  ratings)
    print()

    # 3. Insert into PostgreSQL
    print("→ Loading into PostgreSQL ...")

    trips.to_sql("trips", engine, if_exists="append", index=False, chunksize=500)
    print("  ✓ trips loaded")

    payments.to_sql("payments", engine, if_exists="append", index=False, chunksize=1000)
    print("  ✓ payments loaded")

    ratings.to_sql("ratings", engine, if_exists="append", index=False, chunksize=500)
    print("  ✓ ratings loaded")

    # 4. Quick sanity check
    print("\n→ Row counts in DB:")
    with engine.connect() as conn:
        for table in ("trips", "payments", "ratings"):
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table}: {count:,} rows")

    print("\n=== Done! ===")


if __name__ == "__main__":
    main()
