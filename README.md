# Uber Driver Analytics Dashboard

Real-world analytics built on **3 years of personal Uber driver data** — 3,451 trips across Los Angeles (2022–2025). PostgreSQL + Streamlit + Plotly.

> "I analyzed my own business to find where the real money was."

**[Live Demo →](https://uber-driver-analytics.streamlit.app)**

---

## Key Findings

| Metric | Value |
|--------|-------|
| Total gross earned | **$70,768** |
| Net after Uber commission | **$39,445** |
| Uber commission rate | **32.3%** |
| Avg earnings per hour | **$87/hr** |
| 5-star rating rate | **98.9%** |
| Best trip type ($/hr) | Short trips 0–2 mi → **$118/hr** |
| Best single day | Oct 28 2023 (Halloween eve) → **$418** |
| Surge bonus earned | **$1,531** across 231 surge trips |

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Data source | Uber driver CSV export (personal) |
| Database | PostgreSQL (local) / Supabase (cloud) |
| Ingestion | Python + pandas + SQLAlchemy |
| Dashboard | Streamlit + Plotly |
| Deployment | Streamlit Cloud |

---

## Project Structure

```
uber-driver-analytics/
├── data/                  # CSVs here (gitignored — personal data)
├── sql/
│   ├── schema.sql         # PostgreSQL table definitions
│   └── analysis/          # 12 analytical SQL scripts
│       ├── 01_earnings_by_year.sql
│       ├── 02_earnings_per_hour.sql
│       ├── 03_payments_breakdown.sql
│       ├── 04_uber_commission_rate.sql
│       ├── 05_airport_vs_regular.sql
│       ├── 06_best_hours.sql
│       ├── 07_heatmap_hour_x_day.sql
│       ├── 08_surge_analysis.sql
│       ├── 09_monthly_trend.sql
│       ├── 10_ratings_distribution.sql
│       ├── 11_best_earning_days.sql
│       └── 12_trip_distance_buckets.sql
├── ingestion/
│   └── load_data.py       # CSV → PostgreSQL pipeline
├── dashboard/
│   ├── app.py             # Streamlit app (4 pages)
│   └── db.py              # SQL query layer
├── .streamlit/
│   └── secrets.toml.example
├── requirements.txt
└── .env.example
```

---

## Dashboard Pages

**Overview** — 8 KPI cards + year-over-year table + "Where the Money Goes" stacked bar

**Earnings** — Monthly timeline · Trips per month · Avg fare trend · Commission breakdown by year

**Trips** — Hour × day heatmap · Distance bucket analysis · Surge vs regular · Airport vs regular

**Ratings & Tips** — 5-star distribution · Tips by year

---

## Run Locally

```bash
# 1. Clone
git clone https://github.com/evgenii-matveev/uber-driver-analytics.git
cd uber-driver-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure database
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 4. Add your Uber CSV export to data/
# Request at: https://help.uber.com/driving-and-delivering/article/request-your-data

# 5. Create DB schema and load data
python ingestion/load_data.py

# 6. Run dashboard
python -m streamlit run dashboard/app.py
```

---

## Data Schema

Three tables loaded from Uber's CSV export:

| Table | Rows | Description |
|-------|------|-------------|
| `trips` | 3,745 | Every trip — timestamps, fares, distance, flags |
| `payments` | 21,112 | Per-trip payment breakdown by category |
| `ratings` | 1,669 | 5-star ratings received |

---

## Insights That Surprised Me

**Short trips pay more per hour** — 0–2 mile trips earn $118/hr vs $80/hr for 20+ mile trips. Uber's minimum fare kicks in, and you fit more trips per hour.

**Halloween weekend > New Year's** — Oct 28 2023 was the single best day ($418, 10 surge trips). Jan 1 had the highest avg fare ($45/trip) but fewer trips.

**Incentives recovered 44% of commission** — Uber took $14,303 in commission but paid back $6,362 in driver incentives. Net commission burden: ~18%.

**$/hr grew 54% in 3 years** — from $68/hr in 2022 to $105/hr in 2025, while avg trip distance dropped (shorter trips, smarter routing).

---

## Skills Demonstrated

- **SQL** — window functions, CTEs, date/timezone handling, aggregations
- **Data Engineering** — CSV ingestion pipeline, schema design, indexing strategy
- **Analytics** — cohort analysis (year-over-year), segmentation (distance buckets, surge/regular)
- **Visualization** — Streamlit multi-page app, Plotly heatmaps, area charts, donut charts
- **Deployment** — Streamlit Cloud, Supabase (PostgreSQL as a service), environment secrets

---

*Data: personal Uber driver export · Los Angeles, CA · May 2022 – May 2025*
