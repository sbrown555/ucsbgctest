import pandas as pd
import requests
from io import StringIO
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from itertools import permutations

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

# Convert all other columns to float
for col in df.columns:
    if col != 'TIMESTAMP':
        df[col] = df[col].astype(float)

# 2. Calibration
def ToppEq(x):
    return (4.3e-6 * x**3 - 5.5e-4 * x**2 + 2.92e-2 * x - 5.3e-2)*100

cal = {"DateTime" : df["TIMESTAMP"],
  
    # T
    "HiC Wet PISA Upper Temp A-1-2-2": df["T(1)"],
    "HiC Wet PISA Lower Temp A-1-2-2": df["T(2)"],
    "HiC Dry QUWI Upper Temp A-3-3-2": df["T(3)"],
    "HiC Dry QUWI Lower Temp A-3-3-2": df["T(4)"],
    "HiC Dry PIPO Upper Temp A-5-3-2": df["T(5)"],
    "HiC Dry PIPO Lower Temp A-5-3-2": df["T(6)"],
    "HiC Wet QUCH Upper Temp A-11-2-2": df["T(7)"],
    "HiC Wet QUCH Lower Temp A-11-2-2": df["T(8)"],
    # Doesn't exist "HiC Wet QUCH Upper Temp A-7-3-2": df["T(9)"],
    "HiC Wet QUCH Lower Temp A-7-3-2": df["T(10)"],
    # Doesn't exist "HiC Dry PISA Upper Temp A-9-1-3": df["T(11)"],
    "HiC Dry PISA Lower Temp A-9-1-3": df["T(12)"],

       
    "LoC Wet PIPO Upper Temp B-1-1-3": df["T_2(1)"],
    "LoC Wet PIPO Lower Temp B-1-1-3": df["T_2(2)"],
    "LoC Dry PISA Upper Temp B-3-3-1": df["T_2(3)"],
    "LoC Dry PISA Lower Temp B-3-3-1": df["T_2(4)"],
    "LoC Wet QUWI Upper Temp B-5-1-1": df["T_2(5)"],
    "LoC Wet QUWI Lower Temp B-5-1-1": df["T_2(6)"],
    "LoC Wet QUWI Upper Temp B-10-3-3": df["T_2(7)"],
    "LoC Wet QUWI Lower Temp B-10-3-3": df["T_2(8)"],
    "LoC Wet QUCH Lower Temp B-7-4-3": df["T_2(9)"],
    "LoC Wet QUCH Upper Temp B-7-4-3": df["T_2(10)"],
    "LoC Dry PISA Upper Temp B-9-2-2": df["T_2(11)"],
    "LoC Dry PISA Lower Temp B-9-2-2": df["T_2(12)"],


    # VWC
    "HiC Wet PISA Upper VWC A-1-2-2": ToppEq(df["e(1)"]),
    "HiC Wet PISA Lower VWC A-1-2-2": ToppEq(df["e(2)"]),
    "HiC Dry QUWI Upper VWC A-3-3-2": ToppEq(df["e(3)"]),
    "HiC Dry QUWI Lower VWC A-3-3-2": ToppEq(df["e(4)"]),
    "HiC Dry PIPO Upper VWC A-5-3-2": ToppEq(df["e(5)"]),
    "HiC Dry PIPO Lower VWC A-5-3-2": ToppEq(df["e(6)"]),
    "HiC Wet QUCH Upper VWC A-11-2-2": ToppEq(df["e(7)"]),
    "HiC Wet QUCH Lower VWC A-11-2-2": ToppEq(df["e(8)"]),
    "HiC Wet QUCH Upper VWC A-7-3-2": df["VW_9"]*100, # Analog sensor
    "HiC Wet QUCH Lower VWC A-7-3-2": ToppEq(df["e(10)"]),
    "HiC Dry PISA Upper VWC A-9-1-3": df["VW_11"]*100, # Analog sensor
    "HiC Dry PISA Lower VWC A-9-1-3": ToppEq(df["e(12)"]),
    "LoC Wet PIPO Upper VWC B-1-1-3": ToppEq(df["e_2(1)"]),
    "LoC Wet PIPO Lower VWC B-1-1-3": ToppEq(df["e_2(2)"]),
    "LoC Dry PISA Upper VWC B-3-3-4": ToppEq(df["e_2(3)"]),
    "LoC Dry PISA Lower VWC B-3-3-4": ToppEq(df["e_2(4)"]),
    "LoC Wet QUWI Upper VWC B-5-1-1": ToppEq(df["e_2(5)"]),
    "LoC Wet QUWI Lower VWC B-5-1-1": ToppEq(df["e_2(6)"]),
    "LoC Wet QUWI Upper VWC B-10-3-3": ToppEq(df["e_2(7)"]),
    "LoC Wet QUWI Lower VWC B-10-3-3": ToppEq(df["e_2(8)"]),
    "LoC Wet QUCH Lower VWC B-7-4-3": ToppEq(df["e_2(9)"]),
    "LoC Wet QUCH Upper VWC B-7-4-3": ToppEq(df["e_2(10)"]),
    "LoC Dry PISA Upper VWC B-9-2-2": ToppEq(df["e_2(11)"]),
    "LoC Dry PISA Lower VWC B-9-2-2": ToppEq(df["e_2(12)"]),


}

df2 = df.assign(**cal)[list(cal.keys())]

cutoff = pd.Timestamp("2025-04-30 17:00")
df2 = df2[df2['DateTime'] > cutoff]


# 3. Error Log Section

def error_log(df, time_col='TIMESTAMP', threshold_min=40):
    df = df.copy()
    df[time_col] = pd.to_datetime(df[time_col])
    
    # Find most recent timestamp
    recent_ts = df[time_col].max()
    now = datetime.now() - timedelta(hours=8) 
    delta = now - recent_ts
    
    # Display status (QUCH if recent)
    warning = delta > timedelta(minutes=threshold_min)
    msg = (f"Last data point at {recent_ts + timedelta(hours=1)} — "
           f"{int(delta.total_seconds()//60)} min {int(delta.total_seconds()%60)} s ago")
    
    if warning:
        return f"**<span style='color:red'>⚠️  STALE DATA: {msg}</span>**", warning
    else:
        return f"**<span style='color:green'>✅ Recent data: {msg}</span>**", warning

# Error message and download button
error_msg, warning = error_log(df, time_col='TIMESTAMP', threshold_min=40)

# Display the error message and CSV download button at the top
col1, col2 = st.columns([4, 1])

with col1:
    st.markdown(error_msg, unsafe_allow_html=True)

with col2:
    # 4. Download CSV Button
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df2)

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name='sensor_data.csv',
        mime='text/csv',
    )


# ——— Plot Section ———


# ——— Temperature Chart ———
temp_cols = [c for c in df2.columns if "Temp" in c]
df_temp = df2.melt(id_vars=["DateTime"],
                   value_vars=temp_cols,
                   var_name="Sensor",
                   value_name="Temperature")

# Split the Sensor column by space into separate columns
split_cols = df_temp['Sensor'].str.split(' ', expand = True)
df_temp['CO2_Treatment'] = split_cols[0]
df_temp['Moisture_Treatment'] = split_cols[1]
df_temp['Species'] = split_cols[2]
df_temp['Sensor_Position'] = split_cols[3]

filter_options_temp = ['All', 'Upper', 'Lower', 'HiC', 'LowC', 'Wet', 'Dry', 'QUCH', 'QUWI', 'PIPO', 'PISA']
filter_temp = st.multiselect(label = "Filter temperature lines by:", options = filter_options_temp, default = 'All', key="temp_filter")

if 'All' in filter_temp:
    filter_temp = []

filter_temp = [x for x in filter_temp if x != 'All']

if ['HiC', 'LowC'] in filter_temp or ['Upper', 'Lower'] in filter_temp or ['Wet', 'Dry'] in filter_temp or ['QUCH', 'QUWI', 'PIPO', 'PISA'] in filter_temp:
    st.warning("Filter warning: Don't choose all options from a particular field at once")

for term in filter_temp:
    df_temp = df_temp[df_temp.isin([term]).any(axis=1)]

options_temp = [col for col in df_temp.columns if col not in ['DateTime', 'Temperature']]
group_temp = st.multiselect(label = "Group temperature lines by:", options = options_temp, default = "Sensor", key="temp_multiselect")

if group_temp:
    df_temp['group'] = df_temp[group_temp].agg(' - '.join, axis=1)
    df_temp_grouped = df_temp.groupby(by = ['DateTime', 'group'], axis = 0, as_index = False, dropna = True)['Temperature'].mean()
    fig_temp = px.line(df_temp_grouped, x = "DateTime", y = "Temperature", color = 'group', title = 'Soil Temperature Sensors')
    fig_temp.update_layout(xaxis_title = 'Time', yaxis_title = 'Temperature_(C)', height = 600)
    st.plotly_chart(fig_temp)
else:
    st.write('Please select at least one column.')
    

# ——— VWC Chart ———
vwc_cols = [c for c in df2.columns if "VWC" in c]
df_vwc = df2.melt(id_vars=["DateTime"],
                  value_vars=vwc_cols,
                  var_name="Sensor",
                  value_name="VWC")

# Split the Sensor column by space into separate columns
split_cols = df_vwc['Sensor'].str.split(' ', expand=True)
df_vwc['CO2_Treatment'] = split_cols[0]          
df_vwc['Moisture_Treatment'] = split_cols[1]  
df_vwc['Species'] = split_cols[2]
df_vwc['Sensor_Position'] = split_cols[3]     

filter_options_vwc = ['All', 'Upper', 'Lower', 'HiC', 'LowC', 'Wet', 'Dry', 'QUCH', 'QUWI', 'PIPO', 'PISA']
filter_vwc = st.multiselect(label = "Filter soil moisture lines by:", options = filter_options_vwc, default = 'All', key="vwc_filter")

if 'All' in filter_vwc:
    filter_vwc = []

filter_vwc = [x for x in filter_vwc if x != 'All']

for term in filter_vwc:
    df_vwc = df_vwc[df_vwc.isin([term]).any(axis=1)]

options_vwc = [col for col in df_vwc.columns if col not in ['DateTime', 'VWC']]
group_vwc = st.multiselect(label = "Group soil moisture lines by:", options = options_vwc, default = "Sensor", key="vwc_grouping")

if group_vwc:
    df_vwc['group'] = df_vwc[group_vwc].agg(' - '.join, axis=1)
    df_vwc_grouped = df_vwc.groupby(by = ['DateTime', 'group'], axis = 0, as_index = False, dropna = True)['VWC'].mean()
    fig_vwc = px.line(df_vwc_grouped, x="DateTime", y="VWC", color='group', title="Soil Moisture Sensors")
    fig_vwc.update_layout(xaxis_title="Time", yaxis_title="Volumetric Water Content (%)", height=600)
    st.plotly_chart(fig_vwc)
else:
    st.write("Please select at least one column.")

# 4. Error List Section (Columns with NaN or 0 Values)
def find_errors(df):
    errors = []
    exclude_cols = ['e(9)', 'e(11)', 'e(12)', 'T(9)', 'T(11)', 'T(12)','RECORD']  # Columns to exclude
    for col in df.columns:
        if col in exclude_cols:
            continue  # Skip excluded columns
        if df[col].isna().any() or (df[col] == 0).any():
            error_rows = df[df[col].isna() | (df[col] == 0)]
            for _, row in error_rows.iterrows():
                errors.append({'column': col, 'timestamp': row['TIMESTAMP']})
    return errors

errors = find_errors(df)

if errors:
    # Sort errors by timestamp (latest first)
    error_df = pd.DataFrame(errors)
    error_df = error_df.sort_values(by='timestamp', ascending=False)
    
    st.write("### Columns with NaN or 0 Values:")
    st.dataframe(error_df)  # Display the errors in a dataframe
else:
    st.write("### No NaN or Zero Values detected.")
