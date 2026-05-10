"""
Database query layer — all SQL lives here, app.py just calls functions.
"""

import os
from functools import lru_cache

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

_engine = None


def get_engine():
    global _engine
    if _engine is None:
        url = (
            f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        _engine = create_engine(url)
    return _engine


def query(sql: str, params: dict = None) -> pd.DataFrame:
    with get_engine().connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


# ── Overview KPIs ─────────────────────────────────────────────────────────────

def get_kpis() -> dict:
    df = query("""
        SELECT
            COUNT(*)                                       AS total_trips,
            ROUND(SUM(original_fare_usd)::numeric, 2)     AS gross_usd,
            ROUND(AVG(original_fare_usd), 2)              AS avg_fare,
            ROUND(AVG(original_fare_usd
                / NULLIF(trip_duration_sec / 3600.0, 0)), 2) AS avg_earnings_per_hour,
            ROUND(AVG(trip_distance_miles), 2)            AS avg_miles,
            SUM(CASE WHEN is_surged THEN 1 ELSE 0 END)   AS surge_trips,
            SUM(CASE WHEN is_airport_trip THEN 1 ELSE 0 END) AS airport_trips
        FROM trips
        WHERE is_completed = true
          AND trip_duration_sec > 0
    """)
    row = df.iloc[0]

    pay = query("""
        SELECT
            ROUND(SUM(CASE WHEN category = 'driver_payment_fares'
                          THEN local_amount ELSE 0 END)::numeric, 2) AS gross_fares,
            ROUND(ABS(SUM(CASE WHEN category = 'commission'
                              THEN local_amount ELSE 0 END))::numeric, 2) AS commission,
            ROUND(SUM(CASE WHEN category = 'existing_driver_incentive'
                          THEN local_amount ELSE 0 END)::numeric, 2) AS incentives,
            ROUND(SUM(CASE WHEN category = 'tip'
                          THEN local_amount ELSE 0 END)::numeric, 2) AS tips
        FROM payments
    """)
    p = pay.iloc[0]

    net = float(p["gross_fares"]) - float(p["commission"]) + float(p["incentives"]) + float(p["tips"])
    commission_pct = float(p["commission"]) / float(p["gross_fares"]) * 100 if p["gross_fares"] else 0

    return {
        "total_trips":        int(row["total_trips"]),
        "gross_usd":          float(row["gross_usd"]),
        "net_usd":            round(net, 2),
        "avg_fare":           float(row["avg_fare"]),
        "avg_earnings_per_hour": float(row["avg_earnings_per_hour"]),
        "avg_miles":          float(row["avg_miles"]),
        "surge_trips":        int(row["surge_trips"]),
        "airport_trips":      int(row["airport_trips"]),
        "commission_usd":     float(p["commission"]),
        "commission_pct":     round(commission_pct, 1),
        "incentives_usd":     float(p["incentives"]),
        "tips_usd":           float(p["tips"]),
    }


# ── Earnings ──────────────────────────────────────────────────────────────────

def get_monthly_trend() -> pd.DataFrame:
    return query("""
        SELECT
            DATE_TRUNC('month', request_at AT TIME ZONE 'America/Los_Angeles')::date AS month,
            COUNT(*)                                          AS trips,
            ROUND(SUM(original_fare_usd)::numeric, 2)        AS gross_usd,
            ROUND(AVG(original_fare_usd), 2)                 AS avg_fare_usd
        FROM trips
        WHERE is_completed = true
        GROUP BY 1
        ORDER BY 1
    """)


def get_yearly_summary() -> pd.DataFrame:
    return query("""
        SELECT
            EXTRACT(YEAR FROM request_at AT TIME ZONE 'America/Los_Angeles')::int AS year,
            COUNT(*)                                                          AS trips,
            ROUND(SUM(original_fare_usd)::numeric, 2)                        AS gross_usd,
            ROUND(AVG(original_fare_usd), 2)                                 AS avg_fare,
            ROUND(AVG(original_fare_usd
                / NULLIF(trip_duration_sec / 3600.0, 0)), 2)                 AS earnings_per_hour
        FROM trips
        WHERE is_completed = true AND trip_duration_sec > 0
        GROUP BY 1
        ORDER BY 1
    """)


def get_payments_by_year() -> pd.DataFrame:
    return query("""
        SELECT
            EXTRACT(YEAR FROM paid_at)::int                                AS year,
            ROUND(SUM(CASE WHEN category = 'driver_payment_fares'
                          THEN local_amount ELSE 0 END)::numeric, 2)      AS gross_fares,
            ROUND(ABS(SUM(CASE WHEN category = 'commission'
                              THEN local_amount ELSE 0 END))::numeric, 2) AS commission,
            ROUND(SUM(CASE WHEN category = 'existing_driver_incentive'
                          THEN local_amount ELSE 0 END)::numeric, 2)      AS incentives,
            ROUND(SUM(CASE WHEN category = 'tip'
                          THEN local_amount ELSE 0 END)::numeric, 2)      AS tips
        FROM payments
        WHERE paid_at IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """)


# ── Trips ─────────────────────────────────────────────────────────────────────

def get_heatmap() -> pd.DataFrame:
    return query("""
        SELECT
            EXTRACT(DOW  FROM request_at AT TIME ZONE 'America/Los_Angeles')::int AS day_of_week,
            EXTRACT(HOUR FROM request_at AT TIME ZONE 'America/Los_Angeles')::int AS hour_of_day,
            COUNT(*)                              AS trips,
            ROUND(AVG(original_fare_usd), 2)      AS avg_fare_usd
        FROM trips
        WHERE is_completed = true
        GROUP BY 1, 2
        ORDER BY 1, 2
    """)


def get_surge_stats() -> pd.DataFrame:
    return query("""
        SELECT
            is_surged,
            COUNT(*)                                              AS trips,
            ROUND(AVG(surge_multiplier), 3)                      AS avg_multiplier,
            ROUND(AVG(original_fare_usd), 2)                     AS avg_fare_usd,
            ROUND(SUM(surge_fare_usd)::numeric, 2)               AS total_surge_bonus
        FROM trips
        WHERE is_completed = true
        GROUP BY is_surged
    """)


def get_distance_buckets() -> pd.DataFrame:
    return query("""
        SELECT
            CASE
                WHEN trip_distance_miles < 2   THEN '0–2 mi'
                WHEN trip_distance_miles < 5   THEN '2–5 mi'
                WHEN trip_distance_miles < 10  THEN '5–10 mi'
                WHEN trip_distance_miles < 20  THEN '10–20 mi'
                ELSE '20+ mi'
            END                                                         AS bucket,
            COUNT(*)                                                    AS trips,
            ROUND(AVG(original_fare_usd), 2)                           AS avg_fare_usd,
            ROUND(AVG(original_fare_usd
                / NULLIF(trip_duration_sec / 3600.0, 0)), 2)           AS earnings_per_hour
        FROM trips
        WHERE is_completed = true
          AND trip_distance_miles > 0
          AND trip_duration_sec > 0
        GROUP BY 1
        ORDER BY MIN(trip_distance_miles)
    """)


def get_airport_comparison() -> pd.DataFrame:
    return query("""
        SELECT
            is_airport_trip,
            COUNT(*)                                      AS trips,
            ROUND(AVG(original_fare_usd), 2)              AS avg_fare_usd,
            ROUND(AVG(trip_distance_miles), 2)            AS avg_miles,
            ROUND(AVG(trip_duration_sec / 60.0), 1)       AS avg_min
        FROM trips
        WHERE is_completed = true
        GROUP BY is_airport_trip
    """)


# ── Ratings & Tips ────────────────────────────────────────────────────────────

def get_ratings_distribution() -> pd.DataFrame:
    return query("""
        SELECT
            five_star_rating                                           AS rating,
            COUNT(*)                                                   AS count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1)        AS pct
        FROM ratings
        GROUP BY 1
        ORDER BY 1 DESC
    """)


def get_tips_by_hour() -> pd.DataFrame:
    return query("""
        SELECT
            EXTRACT(HOUR FROM request_at AT TIME ZONE 'America/Los_Angeles')::int AS hour_of_day,
            COUNT(CASE WHEN wait_time_fare_usd > 0 THEN 1 END)        AS tipped_trips,
            COUNT(*)                                                   AS total_trips,
            ROUND(AVG(CASE WHEN wait_time_fare_usd > 0
                          THEN wait_time_fare_usd END), 2)             AS avg_tip_usd
        FROM trips
        WHERE is_completed = true
        GROUP BY 1
        ORDER BY 1
    """)
