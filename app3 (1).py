"""
app.py
------
Streamlit dashboard for the Data Cleaning & Reporting Automation project.

Run with:
    streamlit run app.py
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Make sure sibling modules are importable when launched from any directory ─
sys.path.insert(0, os.path.dirname(__file__))

import generate_data   # noqa: E402  – produces raw_data.csv
import cleaner         # noqa: E402  – runs the cleaning pipeline

# ─────────────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Data Cleaning Dashboard",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# Custom CSS – dark-accent theme, clean cards, readable typography
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* ── Header banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
    border-radius: 14px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.8rem;
    color: #fff;
}
.hero-banner h1 { margin: 0; font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; }
.hero-banner p  { margin: .4rem 0 0; font-size: 1rem; opacity: .75; }

/* ── KPI cards ── */
.kpi-card {
    background: #fff;
    border: 1px solid #e8ecf0;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
    text-align: center;
}
.kpi-label { font-size: .78rem; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: .06em; margin-bottom: .3rem; }
.kpi-value { font-size: 2.2rem; font-weight: 800; line-height: 1; }
.kpi-sub   { font-size: .78rem; color: #9ca3af; margin-top: .25rem; }
.kpi-blue   { color: #2563eb; }
.kpi-amber  { color: #d97706; }
.kpi-red    { color: #dc2626; }
.kpi-green  { color: #16a34a; }

/* ── Section headers ── */
.section-title {
    font-size: 1.1rem; font-weight: 700; color: #1e293b;
    border-left: 4px solid #2563eb; padding-left: .7rem;
    margin: 1.6rem 0 1rem;
}

/* ── Data-quality badge ── */
.quality-badge {
    display: inline-block;
    padding: .25rem .75rem;
    border-radius: 20px;
    font-size: .8rem;
    font-weight: 600;
}
.badge-good    { background: #dcfce7; color: #166534; }
.badge-warning { background: #fef3c7; color: #92400e; }
.badge-danger  { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=60)
    st.title("⚙️ Controls")
    st.markdown("---")

    run_btn = st.button("🔄  Re-generate & Re-clean Data", use_container_width=True)
    st.markdown("---")
    st.markdown("""
**Pipeline steps**
1. Generate `raw_data.csv`
2. Remove duplicates
3. Handle missing values
4. Standardise text
5. Drop invalid rows
6. Save `cleaned_data.csv`
7. Export `report.csv`
""")
    st.markdown("---")
    st.caption("Data Cleaning Automation v1.0")


# ─────────────────────────────────────────────────────────────────────────────
# Generate & clean (cached so re-runs are instant unless button pressed)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_data(_trigger: int):
    """
    Wrapped in a function so st.cache_data can be busted by the trigger counter.
    Runs generate_data then cleaner pipeline.
    """
    # Generate raw CSV
    import importlib
    importlib.reload(generate_data)      # honour re-generate request
    generate_data.random.seed(_trigger)  # different seed each re-run
    generate_data.np.random.seed(_trigger)

    first  = generate_data.FIRST_NAMES
    last   = generate_data.LAST_NAMES
    cities = generate_data.CITIES_MESSY

    records = []
    import random as _r
    _r.seed(_trigger)
    for i in range(1, 451):
        messy   = _r.random() < 0.25
        invalid = _r.random() < 0.08
        rec = {
            "Customer ID": f"CUST-{i:04d}",
            "Name":  generate_data.random_name(messy=messy),
            "Age":   generate_data.random_age(invalid=invalid),
            "City":  _r.choice(cities if messy else generate_data.CITIES_CLEAN),
            "Sales": generate_data.random_sales(invalid=invalid),
        }
        for col in ["Name", "Age", "City", "Sales"]:
            if _r.random() < 0.05:
                rec[col] = np.nan
        records.append(rec)

    df_raw = pd.DataFrame(records)
    dup_idx = _r.sample(range(len(df_raw)), 50)
    df_raw = pd.concat([df_raw, df_raw.iloc[dup_idx]], ignore_index=True)
    df_raw = df_raw.sample(frac=1, random_state=_trigger).reset_index(drop=True)
    df_raw.to_csv(os.path.join(os.path.dirname(__file__), "raw_data.csv"), index=False)

    stats = cleaner.run_pipeline()
    df_clean = pd.read_csv(os.path.join(os.path.dirname(__file__), "cleaned_data.csv"))
    report   = pd.read_csv(os.path.join(os.path.dirname(__file__), "report.csv"))
    return df_raw, df_clean, stats, report


# Initialise trigger counter in session state
if "trigger" not in st.session_state:
    st.session_state.trigger = 0
if run_btn:
    st.session_state.trigger += 1
    st.cache_data.clear()

with st.spinner("⚙️  Running pipeline…"):
    df_raw, df_clean, stats, report = get_data(st.session_state.trigger)


# ─────────────────────────────────────────────────────────────────────────────
# Hero banner
# ─────────────────────────────────────────────────────────────────────────────
quality_pct = round(stats["total_clean"] / stats["total_raw"] * 100, 1)
badge_cls   = "badge-good" if quality_pct >= 75 else "badge-warning" if quality_pct >= 50 else "badge-danger"

st.markdown(f"""
<div class="hero-banner">
  <h1>🧹 Data Cleaning & Reporting Automation</h1>
  <p>Automated pipeline · Pandas · Plotly · Streamlit &nbsp;|&nbsp;
     <span class="quality-badge {badge_cls}">Data Quality: {quality_pct}%</span>
  </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# KPI Cards
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📊 Pipeline Summary</div>', unsafe_allow_html=True)

k1, k2, k3, k4, k5 = st.columns(5)

def kpi(col, label, value, sub, css_cls):
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value {css_cls}">{value}</div>
      <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

kpi(k1, "Total Raw Records",    stats["total_raw"],     "before cleaning",          "kpi-blue")
kpi(k2, "Missing Values Found", stats["total_missing"], "across all columns",       "kpi-amber")
kpi(k3, "Duplicates Removed",   stats["duplicates"],    "exact-row matches",        "kpi-red")
kpi(k4, "Invalid Rows Dropped", stats["rows_dropped"],  "age / sales out of range", "kpi-red")
kpi(k5, "Final Clean Records",  stats["total_clean"],   f"{quality_pct}% retained", "kpi-green")


# ─────────────────────────────────────────────────────────────────────────────
# Visualisations
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 Visualisations</div>', unsafe_allow_html=True)

col_left, col_right = st.columns(2)

# ── Chart 1 · Missing Values by Column ───────────────────────────────────────
with col_left:
    mv = stats["missing_per_col"]
    cols_with_missing = {k: v for k, v in mv.items() if v > 0}

    if cols_with_missing:
        fig_mv = go.Figure(go.Bar(
            x=list(cols_with_missing.keys()),
            y=list(cols_with_missing.values()),
            marker_color=["#f59e0b", "#ef4444", "#8b5cf6", "#3b82f6", "#10b981"][: len(cols_with_missing)],
            text=list(cols_with_missing.values()),
            textposition="outside",
        ))
        fig_mv.update_layout(
            title="Missing Values by Column",
            xaxis_title="Column",
            yaxis_title="Missing Count",
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(family="Inter, Segoe UI, sans-serif", size=13),
            height=380,
            margin=dict(t=50, b=40, l=50, r=20),
        )
        fig_mv.update_yaxes(gridcolor="#f1f5f9")
    else:
        fig_mv = go.Figure()
        fig_mv.add_annotation(text="No missing values found", xref="paper", yref="paper",
                               x=0.5, y=0.5, showarrow=False, font=dict(size=16))
        fig_mv.update_layout(height=380, plot_bgcolor="white", paper_bgcolor="white")

    st.plotly_chart(fig_mv, use_container_width=True)

# ── Chart 2 · Records Before vs After Cleaning ────────────────────────────────
with col_right:
    stages = ["Raw Records", "After Dedup", "After Invalid Drop", "Final Clean"]
    values = [
        stats["total_raw"],
        stats["total_raw"] - stats["duplicates"],
        stats["total_raw"] - stats["duplicates"] - stats["rows_dropped"],
        stats["total_clean"],
    ]
    colours = ["#64748b", "#3b82f6", "#f59e0b", "#16a34a"]

    fig_funnel = go.Figure(go.Funnel(
        y=stages,
        x=values,
        textinfo="value+percent initial",
        marker_color=colours,
        connector={"line": {"color": "#e2e8f0", "width": 2}},
    ))
    fig_funnel.update_layout(
        title="Records Through Cleaning Pipeline",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13),
        height=380,
        margin=dict(t=50, b=40, l=10, r=20),
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

# ── Chart 3 · Sales Distribution (clean data) ────────────────────────────────
col_a, col_b = st.columns(2)

with col_a:
    fig_hist = px.histogram(
        df_clean, x="Sales", nbins=40,
        title="Sales Distribution (Cleaned Data)",
        color_discrete_sequence=["#3b82f6"],
        labels={"Sales": "Sales (₹/$ value)"},
    )
    fig_hist.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13),
        height=360, margin=dict(t=50, b=40, l=50, r=20),
        yaxis=dict(gridcolor="#f1f5f9"),
    )
    st.plotly_chart(fig_hist, use_container_width=True)

# ── Chart 4 · Top 10 Cities by Total Sales ───────────────────────────────────
with col_b:
    city_sales = (
        df_clean.groupby("City")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig_city = px.bar(
        city_sales, x="Sales", y="City", orientation="h",
        title="Top 10 Cities by Total Sales",
        color="Sales",
        color_continuous_scale="Blues",
        labels={"Sales": "Total Sales", "City": ""},
    )
    fig_city.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter, Segoe UI, sans-serif", size=13),
        height=360, margin=dict(t=50, b=40, l=10, r=20),
        yaxis=dict(autorange="reversed"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_city, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# Data preview tabs
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🗂️ Data Preview</div>', unsafe_allow_html=True)

tab_raw, tab_clean, tab_report = st.tabs(["📂 Raw Data", "✅ Cleaned Data", "📋 Summary Report"])

with tab_raw:
    st.caption(f"{len(df_raw):,} rows  ·  {df_raw.shape[1]} columns")
    st.dataframe(df_raw.head(100), use_container_width=True, height=320)

with tab_clean:
    st.caption(f"{len(df_clean):,} rows  ·  {df_clean.shape[1]} columns")
    st.dataframe(df_clean.head(100), use_container_width=True, height=320)

with tab_report:
    st.dataframe(report, use_container_width=True, height=380)


# ─────────────────────────────────────────────────────────────────────────────
# Download buttons
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">⬇️ Download Files</div>', unsafe_allow_html=True)

d1, d2, d3 = st.columns(3)

def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()

base = os.path.dirname(__file__)

with d1:
    st.download_button(
        "📥  raw_data.csv",
        data=read_bytes(os.path.join(base, "raw_data.csv")),
        file_name="raw_data.csv",
        mime="text/csv",
        use_container_width=True,
    )
with d2:
    st.download_button(
        "📥  cleaned_data.csv",
        data=read_bytes(os.path.join(base, "cleaned_data.csv")),
        file_name="cleaned_data.csv",
        mime="text/csv",
        use_container_width=True,
    )
with d3:
    st.download_button(
        "📥  report.csv",
        data=read_bytes(os.path.join(base, "report.csv")),
        file_name="report.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("Built with Python · Pandas · Plotly · Streamlit")
