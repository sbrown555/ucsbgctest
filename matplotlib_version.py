import pandas as pd
import requests
import streamlit as st
import plotly.express as px
import datetime as dt

url = 'https://raw.githubusercontent.com/sbrown555/ucsbgctest/refs/heads/main/small_data_14May25.csv'

data = pd.read_csv(url, low_memory = False, index_col = 0)

data['datetime'] = pd.to_datetime(data['datetime'], errors = 'coerce')
for col in data.columns:
  if col not in ['datetime','site']:
    data.loc[:,col] = pd.to_numeric(data.loc[:,col], errors="coerce")

df = data

df.columns = [col.replace("/", ".") for col in df.columns]
df.columns = [col.replace("^","") for col in df.columns]
df.columns = [col.replace("(","") for col in df.columns]
df.columns = [col.replace(")","") for col in df.columns]

df.columns

# Adding date, week, day, and hour columns and making sure site is interpreted correctly
df['date'] = df['datetime'].dt.strftime('%m/%d/%Y')
df['date'] = pd.to_datetime(df['date'])
df['hour'] = df['datetime'].dt.strftime('%H')
df['day_of_year'] = (df['date'].dt.strftime('%j').astype(int) - 1)
df['week_of_year'] = df['day_of_year'] // 7
df['site']=df['site'].astype(str)

# Add filtering by indicator columns

# Update indicator columns
variables = ['T_HMP_C', 'RH_%', 'PAR_IN_umol_photons.m2.s', 'soil_moisture_10cm_m3.m3', 'soil_moisture_30cm_m3.m3','soil_moisture_60cm_m3.m3', 'soil_moisture_90cm_m3.m3']
indicator_columns = [col for col in df.columns if col not in variables]

# Choose variables to filter by or leave blank
# filter_variables = []
# 
# if filter_variables != []:
#   for var in filter_variables:
#     value_options = list(set(df[var]))
#     print(value_options)  
    
# Choose values to filter by or leave blank

# values_chosen = {}
# filter_values = dict(zip(filter_variables, values_chosen))

filter_values = {}
# filter_values = { 'site' : 'sjer', "week_of_year" : float("6")}

mask = pd.Series(True, index = df.index)
for var, val in filter_values.items():
  mask &= df[var] == val
  
df = df[mask]

# Add filtering by time

# time_start = input(label = 'Choose a datetime to start or leave blank')
# time_end = st.text_input(label = 'Choose a datetime to end or leave blank')
time_start = ''
time_end = ''

if time_start == '':
  time_start = df['datetime'].min()

if time_end == '':
  time_end = df['datetime'].max()

print('Start time is ', time_start)
print('End time is ', time_end)

  
df = df[df['datetime'] >= time_start]
df = df[df['datetime'] <= time_end]


import matplotlib.pyplot as plt

# os.chdir("/Users/sean/Documents/Sean/Lara Research/Experimental Design/Meteorological data/SJER CZ1 and Soaproot CZ2 Sites")

# input a subdaily interval in hours
# interval = '4'
interval = st.text_input("Input a subdaily interval in hours")

if interval != '':
  st.warning("Input a suitable subdaily interval in hours")
  st.stop()
elif interval >= 24:
  st.warning("Input a suitable subdaily interval in hours")
  st.stop()
  
  
interval = int(interval)
interval_name = f"{interval}_hour_interval"

df[interval_name] = df['datetime'].apply(lambda x: (float(x.hour//interval)))
df_interval = df.groupby(['site', 'date', interval_name]).agg({col : 'mean' for col in variables})
df_interval.reset_index(inplace = True)
df_interval['day_of_year'] = (df_interval['date'].dt.strftime('%j').astype(int) - 1)
df_day = df_interval.groupby(['site', 'day_of_year', interval_name]).agg({col : 'mean' for col in variables})
df_day.reset_index(inplace = True)
df_day['week_of_year'] = df_day['day_of_year']//7
df_week = df_day.groupby(['site', 'week_of_year', interval_name]).agg({col : 'mean' for col in variables})
df_week.reset_index(inplace = True)

grouping_dict = {'datetime' : df, interval_name : df_interval, 'day_of_year' : df_day, 'week_of_year' : df_week}


# Grouping and graphing all relevant variables based on either day and interval or week and interval
indicator_subset = ['day_of_year', 'week_of_year']
variable_subset = variables

xaxis = st.selectbox(label = "Choose an independent variable: ", options = indicator_subset)
yaxis = st.selectbox(label = "Choose a dependent variable: ", options = variable_susbet)

dataframe = grouping_dict[xaxis]
label = f"{xaxis}_and_{interval_name}"
dataframe[label] = dataframe[xaxis] + interval*dataframe[interval_name]/24
dataframe[label] = pd.to_numeric(dataframe[label], errors = 'coerce')
csv_name = label + '_15May2025.csv'
# dataframe.to_csv(csv_name)
plt.clf()
for site, group in dataframe.groupby("site"):
  plt.plot(group[label], group[yaxis], label = site)
plt.title(yaxis)
plt.xlabel(label)
plt.grid(True)
plt.legend(title='Site')
plt.tight_layout()
# plt.show()
st.pyplot()
# fig_name = f"{yaxis}_{xaxis}_{interval_name}_14May25.png"
# plt.savefig(fig_name)


# Commented out below because already saved graphs and going to run again with different value for subdaily interval
# # Grouping and graphing all relevant variables based on either day of year or week of year and site
# variable_subset = variables
# indicator_subset = ['day_of_year', 'week_of_year']
# for yaxis in variable_subset:
#   for xaxis in indicator_subset:
#     dataframe = grouping_dict[xaxis].groupby([xaxis, 'site']).agg({col : 'mean' for col in variable_subset})
#     dataframe.reset_index(inplace = True)
#     plt.clf()
#     for site, group in dataframe.groupby("site"):
#       plt.plot(group[xaxis], group[yaxis], label = site)
#     plt.title(yaxis)
#     plt.xlabel(xaxis)
#     plt.grid(True)
#     plt.legend(title='Site')
#     plt.tight_layout()
#     plt.show()
#     csv_name = f"{yaxis}_{xaxis}_14May25.png"
#     plt.savefig(csv_name)
      
