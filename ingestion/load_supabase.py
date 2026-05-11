"""
Load data to Supabase via REST API (PostgREST).
No supabase-py needed — uses requests over HTTPS.

Run: python ingestion/load_supabase.py
"""

import json
import math
from pathlib import Path

import pandas as pd
import requests

# ── Config ────────────────────────────────────────────────────────────────────

SUPABASE_URL = "https://imjlinhmmollceoxaxuc.supabase.co"
SERVICE_KEY  = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImltamxpbmhtbW9sbGNlb3hheHVjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODQ0ODk2OSwiZXhwIjoyMDk0MDI0OTY5fQ.uQVMp8v8syQwRebzlBJKaa6ug-OuuNJ-Cn1rCjtMAA0"

HEADERS = {
    "apikey":        SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type":  "application/json",
    "Prefer":        "return=minimal",
}

DATA_DIR = Path(__file__).parent.parent / "data"

# ── Helpers ───────────────────────────────────────────────────────────────────

def insert_batch(table: str, rows: list) -> None:
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    r = requests.post(url, headers=HEADERS, data=json.dumps(rows, default=str))
    if r.status_code not in (200, 201):
        raise RuntimeError(f"{table} insert failed {r.status_code}: {r.text[:300]}")


def load_table(table: str, df: pd.DataFrame, chunk: int = 500) -> None:
    rows = json.loads(df.to_json(orient="records", date_format="iso", default_handler=str))
    total = len(rows)
    batches = math.ceil(total / chunk)
    for i in range(batches):
        batch = rows[i * chunk : (i + 1) * chunk]
        insert_batch(table, batch)
        pct = round((i + 1) / batches * 100)
        print(f"  {table}: {min((i+1)*chunk, total)}/{total} rows ({pct}%)", end="\r")
    print(f"  {table}: {total} rows loaded.          ")


def row_count(table: str) -> int:
    url = f"{SUPABASE_URL}/rest/v1/{table}?select=count"
    r = requests.head(url, headers={**HEADERS, "Prefer": "count=exact"})
    return int(r.headers.get("content-range", "0/0").split("/")[-1])


# ── Data prep (same logic as load_data.py) ────────────────────────────────────

def to_bool(series):
    return series.map({"true": True, "false": False, True: True, False: False})


def prep_trips() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "driver_lifetime_trips.csv", low_memory=False)
    for col in ["is_surged","has_destination","is_pool_matched","is_completed",
                "is_flat_rate","is_cash_trip","has_driver_upfront_fare",
                "is_multidestination","is_scheduled_trip","is_airport_trip",
                "is_directed_dispatch_trip"]:
        df[col] = to_bool(df[col])
    for raw, clean in [("request_timestamp_utc","request_at"),
                       ("begintrip_timestamp_utc","begintrip_at"),
                       ("dropoff_timestamp_utc","dropoff_at")]:
        df[clean] = pd.to_datetime(df[raw], utc=True, errors="coerce")
    df = df.rename(columns={"trip_duration_seconds":"trip_duration_sec",
                             "fare_duration_minutes":"fare_duration_min",
                             "wait_duration_minutes":"wait_duration_min",
                             "eta":"eta_seconds"})
    for col in ["eta_seconds", "trip_duration_sec", "driver_trip_number", "vehicle_trip_number"]:
        if col in df.columns:
            s = pd.to_numeric(df[col], errors="coerce")
            df[col] = pd.array([int(v) if pd.notna(v) else pd.NA for v in s], dtype="Int64")
    keep = ["city_name","currency_code","timezone","flow_type","product_type_name",
            "global_product_name","license_plate","driver_trip_number","vehicle_trip_number",
            "request_at","begintrip_at","dropoff_at","eta_seconds","trip_distance_miles",
            "trip_duration_sec","fare_distance_miles","fare_duration_min","wait_duration_min",
            "status","is_completed","is_flat_rate","is_cash_trip","is_surged","is_pool_matched",
            "has_destination","has_driver_upfront_fare","is_multidestination","is_scheduled_trip",
            "is_airport_trip","is_directed_dispatch_trip","surge_multiplier",
            "driver_surge_multiplier","guaranteed_surge_multiplier","original_fare_usd",
            "base_fare_usd","surge_fare_usd","per_mile_fare_usd","per_minute_fare_usd",
            "minimum_fare_roundup_usd","wait_time_fare_usd","long_distance_surcharge_usd",
            "toll_amount_usd","booking_fee_usd","service_fee_usd","cancellation_fee_usd",
            "driver_upfront_fare_usd","promotion_usd","credits_usd",
            "driver_cancellation_reason","cancellation_type","ufp_type","concierge_source_type"]
    return df[[c for c in keep if c in df.columns]]


def prep_payments() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "driver_payments.csv", low_memory=False)
    return df.rename(columns={"City Name":"city_name","Trip UUID":"trip_uuid",
                               "Local Amount":"local_amount","Currency Code":"currency_code",
                               "Classification":"classification","Category":"category",
                               "Local Timestamp":"paid_at"})


def prep_ratings() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "driver_lifetime_ratings_received.csv")
    df["five_star_rating"] = pd.to_numeric(df["five_star_rating"], errors="coerce")
    return df.dropna(subset=["five_star_rating"]).astype({"five_star_rating": int})


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=== Uber Analytics -> Supabase ===\n")
    print("NOTE: Make sure schema.sql was already run in Supabase SQL Editor!\n")

    print("Reading CSVs...")
    trips    = prep_trips()
    payments = prep_payments()
    ratings  = prep_ratings()
    print(f"  trips:    {len(trips):,} rows")
    print(f"  payments: {len(payments):,} rows")
    print(f"  ratings:  {len(ratings):,} rows\n")

    print("Loading to Supabase...")
    load_table("trips",    trips,    chunk=200)
    load_table("payments", payments, chunk=500)
    load_table("ratings",  ratings,  chunk=500)

    print("\nVerifying row counts in Supabase:")
    for t in ("trips", "payments", "ratings"):
        print(f"  {t}: {row_count(t):,} rows")

    print("\n=== Done! ===")


if __name__ == "__main__":
    main()
