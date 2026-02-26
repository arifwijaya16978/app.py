import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(layout="wide")
st.markdown('<style>block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# =========================================
# OPTIONAL LOGO
# =========================================

try:
    logo = Image.open("Logo.jpg")
except:
    logo = None

col1, col2 = st.columns([0.1, 0.9])

with col1:
    if logo:
        st.image(logo, width=100)

html_title = """
<style>
.title-test {
    font-weight: 700;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    background-color: #0E1117;
    color: white;
}
</style>

<h1 class="title-test">🚀 Dashboard KPI BrandG1</h1>
"""

st.markdown(html_title, unsafe_allow_html=True)

# =========================================
# FILE UPLOAD (NO MORE LOCAL CSV)
# =========================================

uploaded_file = st.file_uploader("Upload KPI CSV File", type=["csv"])

if uploaded_file is None:
    st.info("Please upload your KPI CSV file to start.")
    st.stop()

df = pd.read_csv(uploaded_file)
df.columns = df.columns.str.strip().str.lower()

# =========================================
# BASIC VALIDATION
# =========================================

required_cols = ["date", "site", "traffic_gb", "availability", "lat", "lon"]

for col in required_cols:
    if col not in df.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])

# =========================================
# SIMPLE KPI
# =========================================

col1, col2, col3 = st.columns(3)

col1.metric("Total Sites", df["site"].nunique())
col2.metric("Avg Availability", f"{df['availability'].mean():.2f}%")
col3.metric("Total Traffic (GB)", f"{df['traffic_gb'].sum():,.0f}")

# =========================================
# TRAFFIC TREND
# =========================================

st.subheader("Traffic Trend")

traffic_df = df.groupby("date")["traffic_gb"].mean().reset_index()

fig = px.line(traffic_df, x="date", y="traffic_gb", markers=True)

st.plotly_chart(fig, use_container_width=True)

# =========================================
# MAP
# =========================================

st.subheader("Site Location Map")

map_df = df.dropna(subset=["lat", "lon"])

if not map_df.empty:
    fig_map = px.scatter_mapbox(
        map_df,
        lat="lat",
        lon="lon",
        color="availability",
        hover_name="site",
        zoom=6,
        height=600
    )

    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
