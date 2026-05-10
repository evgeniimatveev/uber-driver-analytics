-- =============================================================
-- Uber Driver Analytics — PostgreSQL Schema
-- Source data: Uber Data Export (Driver folder)
-- =============================================================

-- Drop existing tables (safe re-run)
DROP TABLE IF EXISTS ratings CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS trips CASCADE;

-- =============================================================
-- TRIPS — main fact table
-- Source: driver_lifetime_trips-0.csv (3,745 rows, 73 columns)
-- Note: Uber export has no UUID in this file; driver_trip_number
--       is a sequential integer (1, 2, 3...) used as natural key.
--       Payments link via trip_uuid which is NOT in this file.
-- =============================================================
CREATE TABLE trips (
    trip_id              SERIAL PRIMARY KEY,

    -- Identity
    city_name            TEXT,
    currency_code        CHAR(3),
    timezone             TEXT,
    flow_type            TEXT,
    product_type_name    TEXT,
    global_product_name  TEXT,
    license_plate        TEXT,
    driver_trip_number   INTEGER,
    vehicle_trip_number  INTEGER,

    -- Timestamps (UTC stored, local derived in queries)
    request_at           TIMESTAMPTZ,
    begintrip_at         TIMESTAMPTZ,
    dropoff_at           TIMESTAMPTZ,

    -- Trip metrics
    eta_seconds          INTEGER,
    trip_distance_miles  NUMERIC(8, 3),
    trip_duration_sec    INTEGER,
    fare_distance_miles  NUMERIC(8, 3),
    fare_duration_min    NUMERIC(8, 2),
    wait_duration_min    NUMERIC(8, 2),

    -- Flags
    status                       TEXT,
    is_completed                 BOOLEAN,
    is_flat_rate                 BOOLEAN,
    is_cash_trip                 BOOLEAN,
    is_surged                    BOOLEAN,
    is_pool_matched              BOOLEAN,
    has_destination              BOOLEAN,
    has_driver_upfront_fare      BOOLEAN,
    is_multidestination          BOOLEAN,
    is_scheduled_trip            BOOLEAN,
    is_airport_trip              BOOLEAN,
    is_directed_dispatch_trip    BOOLEAN,

    -- Surge
    surge_multiplier             NUMERIC(6, 3),
    driver_surge_multiplier      NUMERIC(6, 3),
    guaranteed_surge_multiplier  NUMERIC(6, 3),

    -- Fare breakdown (USD)
    original_fare_usd            NUMERIC(10, 2),
    base_fare_usd                NUMERIC(10, 2),
    surge_fare_usd               NUMERIC(10, 2),
    per_mile_fare_usd            NUMERIC(10, 4),
    per_minute_fare_usd          NUMERIC(10, 4),
    minimum_fare_roundup_usd     NUMERIC(10, 2),
    wait_time_fare_usd           NUMERIC(10, 2),
    long_distance_surcharge_usd  NUMERIC(10, 2),
    toll_amount_usd              NUMERIC(10, 2),
    booking_fee_usd              NUMERIC(10, 2),
    service_fee_usd              NUMERIC(10, 2),
    cancellation_fee_usd         NUMERIC(10, 2),
    driver_upfront_fare_usd      NUMERIC(10, 2),
    promotion_usd                NUMERIC(10, 2),
    credits_usd                  NUMERIC(10, 2),

    -- Misc
    driver_cancellation_reason   TEXT,
    cancellation_type            TEXT,
    ufp_type                     TEXT,
    concierge_source_type        TEXT
);

-- Indexes for time-series and filter queries
CREATE INDEX idx_trips_request_at     ON trips (request_at);
CREATE INDEX idx_trips_dropoff_at     ON trips (dropoff_at);
CREATE INDEX idx_trips_status         ON trips (status);
CREATE INDEX idx_trips_is_completed   ON trips (is_completed);
CREATE INDEX idx_trips_is_airport     ON trips (is_airport_trip);
CREATE INDEX idx_trips_is_surged      ON trips (is_surged);
CREATE INDEX idx_trips_product        ON trips (product_type_name);


-- =============================================================
-- PAYMENTS — per-trip payment line items
-- Source: driver_payments-0.csv (21,112 rows)
-- Multiple rows per trip. Categories: driver_payment_fares,
--   commission, existing_driver_incentive, etc.
-- Note: trip_uuid exists here but NOT in trips table.
--       Cannot FK-link without Uber providing the mapping.
-- =============================================================
CREATE TABLE payments (
    payment_id      SERIAL PRIMARY KEY,
    city_name       TEXT,
    trip_uuid       UUID,
    local_amount    NUMERIC(10, 2),
    currency_code   CHAR(3),
    classification  TEXT,
    category        TEXT,
    paid_at         TIMESTAMP
);

CREATE INDEX idx_payments_trip_uuid  ON payments (trip_uuid);
CREATE INDEX idx_payments_category   ON payments (category);
CREATE INDEX idx_payments_paid_at    ON payments (paid_at);


-- =============================================================
-- RATINGS — 5-star ratings received
-- Source: driver_lifetime_ratings_received-0.csv (1,669 rows)
-- Only one column in export: five_star_rating.
-- No trip reference — Uber does not expose which trip = which rating.
-- Use for aggregate stats only (% 5-star, distribution).
-- =============================================================
CREATE TABLE ratings (
    rating_id        SERIAL PRIMARY KEY,
    five_star_rating SMALLINT CHECK (five_star_rating BETWEEN 1 AND 5)
);
