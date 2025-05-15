import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import datetime as dt
from io import StringIO

url = 'https://raw.githubusercontent.com/sbrown555/ucsbgctest/refs/heads/main/small_data_14May25.csv'

data = pd.read_csv(url, low_memory = False, index_col = 0)

data['datetime'] = pd.to_datetime(data['datetime'], errors = 'coerce')
for col in data.columns:
  if col not in ['datetime','site']:
    data.loc[:,col] = pd.to_numeric(data.loc[:,col], errors="coerce")

df = data

# Adding date, week, day, and hour columns and making sure site is interpreted correctly
df['date'] = df['datetime'].dt.strftime('%m/%d/%Y')
df['date'] = pd.to_datetime(df['date'])
df['hour'] = df['datetime'].dt.strftime('%H')
df['day_of_year'] = (df['date'].dt.strftime('%j').astype(int) - 1)
df['week_of_year'] = df['day_of_year'] // 7
df['site']=df['site'].astype(str)

# Add filtering by indicator columns

# Update indicator columns
variables = ['T_HMP_(C)', 'RH_(%)', 'PAR_IN_(umol_photons/m2/s)', 'soil_moisture_10cm_(m^3/m^3)','soil_moisture_30cm_(m^3/m^3)', 'soil_moisture_60cm_(m^3/m^3)', 'soil_moisture_90cm_(m^3/m^3)']
indicator_columns = [col for col in df.columns if col not in variables]

filter_variables = st.multiselect(label = "Choose variables to filter by:", options = indicator_columns, default = 'site', key = 'filter_variables')
st.write(indicator_columns)
st.write(filter_variables)

filter_values = {}
if filter_variables != []:
  for var in filter_variables:
    value_options = list(set(df[var]))
    filter_values[var] = st.multiselect(label = f"Choose values to filter {var} by:", options = value_options, key = f"filter_values_{var}_mutliselect")
  
# # filter_values = { 'site' : 'sjer', "week_of_year" : float("6")}

# mask = pd.Series(True, index = df.index)
# for var, val in filter_values.items():
#   mask &= df[var] == val
  
# df = df[mask]


# # Add filtering by time

# time_start = st.text_input(label = 'Choose a datetime to start or leave blank', default = '')
# time_end = st.text_input(label = 'Choose a datetime to end or leave blank', default = '')
# # time_start = ''
# # time_end = ''

# if time_start == '':
#   time_start = df['datetime'].min()

# if time_end == '':
#   time_end = df['datetime'].max()

# st.write('Start time is ', time_start)
# st.write('End time is ', time_end)

  
# df = df[df['datetime'] >= time_start]
# df = df[df['datetime'] <= time_end]


# # Grouping

# interval = st.text_input(label = 'Provide a subdaily intervals in hours:', value = '1')
# interval = int(interval)
# interval_name = f"{interval}_hour_interval"

# df[interval_name] = df['datetime'].apply(lambda x: (float(x.hour//interval)))

# df_interval = df.groupby(['site', 'date', interval_name]).agg({col : 'mean' for col in variables})
# df_interval.reset_index(inplace = True)
# df_interval['day_of_year'] = (df_interval['date'].dt.strftime('%j').astype(int) - 1)
# df_day = df_interval.groupby(['site', 'day_of_year', interval_name]).agg({col : 'mean' for col in variables})
# df_day.reset_index(inplace = True)
# df_day['week_of_year'] = df_day['day_of_year']//7
# df_week = df_day.groupby(['site', 'week_of_year', interval_name]).agg({col : 'mean' for col in variables})


# # When graphing:
# # df is the filtered data with only rows and columns selected through drop-down sheet (or default)
# # df_interval is df grouped by site, date, and sub-daily interval in hours
# # df_day is df_interval grouped by site, day of the year, and sub-daily interval in hours
# # df_week is df_day grouped by site, week of the year, and sub-daily interval in hours

# grouping_dict = {'datetime' : df, interval_name : df_interval, 'day_of_the_year' : df_day, 'week_of_the_year' : df_week}

# xaxis = st.multiselect(label = 'Choose grouping level:', options = grouping_dict.keys(), default = 'week_of_the_year')
# df_grouped = grouping_dict[xaxis]

# yaxis = st.multiselect(label = 'Choose variable to graph:', options = variables, default = 'T_HMP_(C)')

# if grouping_level:
#   fig = px.line(df_grouped, x = xaxis, y = yaxis, color = 'site')
#   fig.update_layout(xaxis_title = 'Time', yaxis_title = yaxis, height = 600)
#   st.plotly_chart(fig)
# else:
#   st.write('Please choose grouping level')
  


