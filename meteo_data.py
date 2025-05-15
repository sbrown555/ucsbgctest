https://drive.google.com/file/d/1EGaJpuCmiFPibTBdEaT3rspsf6SpZqcX/view?usp=drive_link



import pandas as pd
import requests
from io import StringIO
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta

st.set_page_config(layout='wide')

# 1. Download and read CSV
file_id = "11-jkVA5wUq3KYP6hKvVyQcwL0e0-4j_0"
download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
response = requests.get(download_url)

if response.status_code != 200:
    st.error("Failed to download file.")
    st.stop()

content = StringIO(response.text)
df = pd.read_csv(content, skiprows=1).iloc[2:]
df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'])
