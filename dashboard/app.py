"""
Uber Driver Analytics Dashboard
Run: streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
from dashboard import db

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Uber Driver Analytics",
    page_icon="🚗",
    layout="wide",
)

# ── Theme colors ──────────────────────────────────────────────────────────────

UBER_BLACK  = "#000000"
GREEN       = "#00C853"
YELLOW      = "#FFD600"
RED         = "#FF3D00"
GRAY        = "#9E9E9E"
BG_CARD     = "#1E1E1E"

# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.image(
    "https://upload.wikimedia.org/wikipedia/commons/c/cc/Uber_logo_2018.png",
    width=120,
)
st.sidebar.title("Driver Analytics")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["Overview", "Earnings", "Trips", "Ratings & Tips"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.caption("Data: Uber export 2022–2025 · Los Angeles")


# ── Helpers ───────────────────────────────────────────────────────────────────

def metric_card(label: str, value: str, delta: str = "", color: str = GREEN):
    st.markdown(
        f"""
        <div style="background:{BG_CARD};border-radius:10px;padding:20px;text-align:center;
                    border-left:4px solid {color};">
            <div style="color:{GRAY};font-size:13px;margin-bottom:6px;">{label}</div>
            <div style="color:white;font-size:28px;font-weight:700;">{value}</div>
            {"" if not delta else f'<div style="color:{GRAY};font-size:12px;margin-top:4px;">{delta}</div>'}
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 1 — OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────

if page == "Overview":
    st.title("Uber Driver — Performance Overview")
    st.caption("Los Angeles · May 2022 – May 2025 · 3,451 completed trips")
    st.markdown("---")

    kpis = db.get_kpis()

    # Row 1: Money KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Gross Earned (all years)", f"${kpis['gross_usd']:,.0f}", "before Uber commission")
    with c2:
        metric_card("Net Earned", f"${kpis['net_usd']:,.0f}", "after commission + incentives + tips")
    with c3:
        metric_card("Uber Commission Paid", f"${kpis['commission_usd']:,.0f}",
                    f"{kpis['commission_pct']}% of gross", color=RED)
    with c4:
        metric_card("Incentives + Tips", f"${kpis['incentives_usd'] + kpis['tips_usd']:,.0f}",
                    f"bonuses ${kpis['incentives_usd']:,.0f} · tips ${kpis['tips_usd']:,.0f}", color=YELLOW)

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 2: Activity KPIs
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Trips", f"{kpis['total_trips']:,}", "completed")
    with c2:
        metric_card("Avg Fare / Trip", f"${kpis['avg_fare']}", f"avg {kpis['avg_miles']} miles")
    with c3:
        metric_card("Avg Earnings / Hour", f"${kpis['avg_earnings_per_hour']}", "gross, per drive time")
    with c4:
        metric_card("Surge Trips", f"{kpis['surge_trips']:,}",
                    f"{kpis['surge_trips']/kpis['total_trips']*100:.1f}% of all trips", color=YELLOW)

    st.markdown("---")

    # Year-over-year table
    st.subheader("Year-over-Year Summary")
    yearly = db.get_yearly_summary()
    yearly.columns = ["Year", "Trips", "Gross ($)", "Avg Fare ($)", "$/Hour"]
    st.dataframe(
        yearly.style.format({
            "Gross ($)": "${:,.2f}",
            "Avg Fare ($)": "${:.2f}",
            "$/Hour": "${:.2f}",
        }).background_gradient(subset=["$/Hour"], cmap="Greens"),
        use_container_width=True,
        hide_index=True,
    )

    # Payments waterfall
    st.subheader("Where the Money Goes")
    pay = db.get_payments_by_year()
    net_col = pay["gross_fares"] - pay["commission"] + pay["incentives"] + pay["tips"]

    fig = go.Figure()
    fig.add_bar(name="Gross Fares",  x=pay["year"].astype(str), y=pay["gross_fares"],  marker_color=GREEN)
    fig.add_bar(name="Commission",   x=pay["year"].astype(str), y=-pay["commission"],  marker_color=RED)
    fig.add_bar(name="Incentives",   x=pay["year"].astype(str), y=pay["incentives"],   marker_color=YELLOW)
    fig.add_bar(name="Tips",         x=pay["year"].astype(str), y=pay["tips"],         marker_color="#40C4FF")
    fig.update_layout(
        barmode="relative", template="plotly_dark",
        yaxis_title="USD", xaxis_title="Year",
        legend=dict(orientation="h", y=1.1),
        height=380,
    )
    st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 2 — EARNINGS
# ─────────────────────────────────────────────────────────────────────────────

elif page == "Earnings":
    st.title("Earnings Timeline")
    st.markdown("---")

    monthly = db.get_monthly_trend()
    monthly["month"] = pd.to_datetime(monthly["month"])

    # Monthly earnings line chart
    st.subheader("Monthly Gross Earnings")
    fig = px.area(
        monthly, x="month", y="gross_usd",
        template="plotly_dark", color_discrete_sequence=[GREEN],
        labels={"month": "", "gross_usd": "Gross USD"},
    )
    fig.update_traces(fill="tozeroy", line_width=2)
    fig.update_layout(height=360)
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Trips per month bar
        st.subheader("Trips per Month")
        fig2 = px.bar(
            monthly, x="month", y="trips",
            template="plotly_dark", color_discrete_sequence=["#40C4FF"],
            labels={"month": "", "trips": "Trips"},
        )
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Avg fare per month
        st.subheader("Avg Fare per Month")
        fig3 = px.line(
            monthly, x="month", y="avg_fare_usd",
            template="plotly_dark", color_discrete_sequence=[YELLOW],
            labels={"month": "", "avg_fare_usd": "Avg Fare $"},
            markers=True,
        )
        fig3.update_layout(height=300)
        st.plotly_chart(fig3, use_container_width=True)

    # Commission breakdown by year
    st.subheader("Gross vs Net by Year (Uber Commission Breakdown)")
    pay = db.get_payments_by_year()
    pay["net"] = pay["gross_fares"] - pay["commission"] + pay["incentives"] + pay["tips"]
    pay["commission_pct"] = (pay["commission"] / pay["gross_fares"] * 100).round(1)

    col1, col2 = st.columns([2, 1])
    with col1:
        fig4 = go.Figure()
        fig4.add_bar(name="Net to Driver", x=pay["year"].astype(str), y=pay["net"], marker_color=GREEN)
        fig4.add_bar(name="Commission (Uber)", x=pay["year"].astype(str), y=pay["commission"], marker_color=RED)
        fig4.update_layout(
            barmode="stack", template="plotly_dark",
            yaxis_title="USD", height=320,
            legend=dict(orientation="h", y=1.1),
        )
        st.plotly_chart(fig4, use_container_width=True)

    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.dataframe(
            pay[["year", "gross_fares", "commission", "commission_pct", "incentives", "tips", "net"]]
            .rename(columns={
                "year": "Year", "gross_fares": "Gross", "commission": "Commission",
                "commission_pct": "Comm %", "incentives": "Incentives",
                "tips": "Tips", "net": "Net",
            })
            .style.format({
                "Gross": "${:.0f}", "Commission": "${:.0f}",
                "Comm %": "{:.1f}%", "Incentives": "${:.0f}",
                "Tips": "${:.0f}", "Net": "${:.0f}",
            }),
            hide_index=True,
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 3 — TRIPS
# ─────────────────────────────────────────────────────────────────────────────

elif page == "Trips":
    st.title("Trip Analytics")
    st.markdown("---")

    # Heatmap
    st.subheader("Earnings Heatmap — Hour of Day × Day of Week")
    hm = db.get_heatmap()
    pivot = hm.pivot_table(index="day_of_week", columns="hour_of_day",
                           values="avg_fare_usd", fill_value=0)
    day_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    pivot.index = [day_labels[i] for i in pivot.index]

    fig = px.imshow(
        pivot,
        color_continuous_scale=[[0, "#1a1a1a"], [0.5, "#004D40"], [1, GREEN]],
        labels={"x": "Hour of Day", "y": "", "color": "Avg Fare $"},
        aspect="auto", template="plotly_dark",
    )
    fig.update_layout(height=320, coloraxis_colorbar=dict(title="Avg $"))
    st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        # Distance buckets
        st.subheader("Earnings per Hour by Distance")
        buckets = db.get_distance_buckets()
        fig2 = px.bar(
            buckets, x="bucket", y="earnings_per_hour",
            text="earnings_per_hour",
            template="plotly_dark", color_discrete_sequence=[GREEN],
            labels={"bucket": "Trip Distance", "earnings_per_hour": "$/hour"},
        )
        fig2.update_traces(texttemplate="$%{text}", textposition="outside")
        fig2.update_layout(height=340, yaxis_title="Earnings per Hour ($)")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Surge
        st.subheader("Surge vs Regular Trips")
        surge = db.get_surge_stats()
        surge["label"] = surge["is_surged"].map({True: "Surged", False: "Regular"})
        fig3 = px.pie(
            surge, names="label", values="trips",
            template="plotly_dark",
            color="label",
            color_discrete_map={"Surged": YELLOW, "Regular": GRAY},
            hole=0.5,
        )
        fig3.update_traces(textinfo="label+percent")
        fig3.update_layout(height=340, showlegend=False)
        st.plotly_chart(fig3, use_container_width=True)

        surge_row = surge[surge["is_surged"] == True]
        if not surge_row.empty:
            r = surge_row.iloc[0]
            st.markdown(
                f"**Surge bonus earned: ${r['total_surge_bonus']:,.2f}**  \n"
                f"Avg multiplier: {r['avg_multiplier']}x · Avg fare: ${r['avg_fare_usd']}"
            )

    # Airport vs regular
    st.subheader("Airport vs Regular Trips")
    airport = db.get_airport_comparison()
    airport["label"] = airport["is_airport_trip"].map({True: "Airport (LAX)", False: "Regular"})

    col1, col2, col3 = st.columns(3)
    for col, metric, title in zip(
        [col1, col2, col3],
        ["avg_fare_usd", "avg_miles", "avg_min"],
        ["Avg Fare ($)", "Avg Miles", "Avg Duration (min)"],
    ):
        with col:
            fig = px.bar(
                airport, x="label", y=metric,
                text=metric, template="plotly_dark",
                color="label",
                color_discrete_map={"Airport (LAX)": YELLOW, "Regular": GREEN},
                labels={"label": "", metric: title},
            )
            fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
            fig.update_layout(height=280, showlegend=False, title=title)
            st.plotly_chart(fig, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE 4 — RATINGS & TIPS
# ─────────────────────────────────────────────────────────────────────────────

elif page == "Ratings & Tips":
    st.title("Ratings & Tips")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Rating Distribution")
        ratings = db.get_ratings_distribution()
        total = ratings["count"].sum()
        five_star = ratings[ratings["rating"] == 5]["count"].sum() if 5 in ratings["rating"].values else 0

        metric_card(
            "5-Star Rate",
            f"{five_star/total*100:.1f}%",
            f"{five_star:,} out of {total:,} ratings",
        )
        st.markdown("<br>", unsafe_allow_html=True)

        fig = px.bar(
            ratings, x="rating", y="count",
            text="pct", template="plotly_dark",
            color_discrete_sequence=[GREEN],
            labels={"rating": "Rating", "count": "Count"},
        )
        fig.update_traces(texttemplate="%{text}%", textposition="outside")
        fig.update_layout(height=300, xaxis=dict(tickmode="linear"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Tips Summary")
        kpis = db.get_kpis()

        metric_card(
            "Total Tips Earned",
            f"${kpis['tips_usd']:,.2f}",
            "across all years",
            color=YELLOW,
        )
        st.markdown("<br>", unsafe_allow_html=True)

        # Tips from payments table by year
        pay = db.get_payments_by_year()
        fig2 = px.bar(
            pay, x=pay["year"].astype(str), y="tips",
            text="tips", template="plotly_dark",
            color_discrete_sequence=[YELLOW],
            labels={"x": "Year", "tips": "Tips ($)"},
        )
        fig2.update_traces(texttemplate="$%{text:.0f}", textposition="outside")
        fig2.update_layout(height=300, xaxis_title="Year", yaxis_title="Tips ($)")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")
    st.caption(
        "Note: Ratings file contains 1,669 entries without trip-level linkage. "
        "Tips are sourced from the payments table (`tip` category)."
    )
