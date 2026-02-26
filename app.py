import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go


# Reading the data from CSV file
df = pd.read_csv("kpi_data.csv")
st.set_page_config(layout="wide")
st.markdown('<style>block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
Image = Image.open('Logo.jpg')

# Insert Image
col1, col2 = st.columns([0.1,0.9])
with col1:
    st.image('Logo.jpg',width=100)

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
   