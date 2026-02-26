import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

st.set_page_config(layout="wide")

# =========================================
# HEADER SECTION
# =========================================

st.markdown(
    '<style>block-container{padding-top:1rem;}</style>',
    unsafe_allow_html=True
)

col_logo, col_title = st.columns([0.1, 0.9])

with col_logo:
    st.image("Logo.jpg", width=100)

with col_title:
    st.markdown("""
        <h1 style='color:white;background-color:#0E1117;
        padding:10px;border-radius:8px;'>
        🚀 Dashboard KPI BrandG1
        </h1>
    """, unsafe_allow_html=True)

st.write(f"Last Updated: {datetime.datetime.now().strftime('%d %B %Y')}")

# =========================================
# LOAD DATA
# =========================================

df = pd.read_csv("kpi_data.csv")

# Normalize column names
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Convert numeric columns
numeric_cols = ["traffic_gb", "availability", "prb", "lat", "lon"]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df["site"] = df["site"].fillna("UNKNOWN")
        
        # =========================================
# DATA CLEANING
# =========================================

# Bersihkan kolom string
df["site"] = df["site"].astype(str).str.strip()
df["sector"] = df["sector"].astype(str).str.strip()
df["cell"] = df["cell"].astype(str).str.strip() if "cell" in df.columns else "N/A"

# Buang baris site kosong / nan
df = df[df["site"].notna()]
df = df[df["site"] != "nan"]
df = df[df["site"] != ""]

# =========================================
# VALIDATION
# =========================================

required_cols = ["date", "site", "traffic_gb", "availability"]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Column '{col}' not found in CSV")
        st.stop()

# Optional columns
if "sector" not in df.columns:
    df["sector"] = "N/A"

if "cell" not in df.columns:
    df["cell"] = "N/A"


# =========================================
# DATE CLEANING (FOR MM/DD/YYYY FORMAT)
# =========================================

df["date"] = pd.to_datetime(
    df["date"],
    format="%m/%d/%Y",
    errors="coerce"
)

df = df.dropna(subset=["date"])

# =========================================
# SIDEBAR DATE FILTER
# =========================================

st.sidebar.header("📅 Date Filter")

min_date = df["date"].min().date()
max_date = df["date"].max().date()

start_date, end_date = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

df = df[
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
]

# =========================================
# DRILL FILTER (Site → Sector → Cell)
# =========================================

col1, col2, col3 = st.columns(3)

with col1:
    site_list = ["All"] + sorted(df["site"].dropna().astype(str).unique())
    selected_site = st.selectbox("Select Site", site_list)

if selected_site != "All":
    df = df[df["site"] == selected_site]

with col2:
    sector_list = ["All"] + sorted(df["sector"].unique())
    selected_sector = st.selectbox("Select Sector", sector_list)

if selected_sector != "All":
    df = df[df["sector"] == selected_sector]

with col3:
    cell_list = ["All"] + sorted(df["cell"].unique())
    selected_cell = st.selectbox("Select Cell", cell_list)

if selected_cell != "All":
    df = df[df["cell"] == selected_cell]

# =========================================
# KPI SELECT
# =========================================

kpi_dict = {
    "Traffic (GB)": "traffic_gb",
    "Availability (%)": "availability"
}

selected_kpi_label = st.selectbox("Select KPI", list(kpi_dict.keys()))
selected_kpi = kpi_dict[selected_kpi_label]

# =========================================
# AGGREGATION
# =========================================

trend_df = df.groupby("date")[selected_kpi].mean().reset_index()
trend_df["MA_7"] = trend_df[selected_kpi].rolling(7).mean()

# =========================================
# PLOT
# =========================================

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=trend_df["date"],
    y=trend_df[selected_kpi],
    mode="lines+markers",
    name="Actual"
))

fig.add_trace(go.Scatter(
    x=trend_df["date"],
    y=trend_df["MA_7"],
    mode="lines",
    name="7-Day Moving Avg"
))

# Threshold line
if selected_kpi == "availability":
    fig.add_hline(
        y=95,
        line_dash="dash",
        annotation_text="Threshold 95%",
        annotation_position="bottom right"
    )

fig.update_layout(
    template="plotly_dark",
    height=500,
    hovermode="x unified"
)

st.subheader("📈 KPI Trend (Click to Drill Date)")
selected_points = plotly_events(fig, click_event=True)

# =========================================
# CLICK DRILL DOWN
# =========================================

if selected_points:
    clicked_date = pd.to_datetime(selected_points[0]["x"])
    st.success(f"Detail for Date: {clicked_date.date()}")

    detail_df = df[df["date"] == clicked_date]
    st.dataframe(detail_df, use_container_width=True)
else:
    st.info("Click any point in chart to see detail data")

# =========================================
# SUMMARY KPI
# =========================================

st.subheader("📊 Summary")

colA, colB, colC = st.columns(3)

colA.metric("Average", f"{trend_df[selected_kpi].mean():.2f}")
colB.metric("Max", f"{trend_df[selected_kpi].max():.2f}")
colC.metric("Min", f"{trend_df[selected_kpi].min():.2f}")