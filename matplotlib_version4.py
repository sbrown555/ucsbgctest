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

# Adding date, week, day, and hour columns and making sure site is interpreted correctly
df['date'] = df['datetime'].dt.strftime('%m/%d/%Y')
df['date'] = pd.to_datetime(df['date'])
df['hour'] = df['datetime'].dt.strftime('%H')
df['day_of_year'] = (df['date'].dt.strftime('%j').astype(int) - 1)

# long_int = st.text_input('Input a greater-than-daily interval in days')

# if long_int == '':
#   st.warning("Input a suitable subdaily interval in hours")
#   st.stop()
# else:
#   long_int = int(long_int)

# if long_int != '':
  # long_int = float(long_int)

# long_int_name = f"{long_int}_day_intervals_of_year"
# df[long_int_name] = df['day_of_year'] // long_int
# df['site']=df['site'].astype(str)

# Add filtering by indicator columns

# Update indicator columns
variables = ['T_HMP_C', 'RH_%', 'PAR_IN_umol_photons.m2.s', 'soil_moisture_10cm_m3.m3', 'soil_moisture_30cm_m3.m3','soil_moisture_60cm_m3.m3', 'soil_moisture_90cm_m3.m3']
indicator_columns = [col for col in df.columns if col not in variables]

import matplotlib.pyplot as plt

# interval = st.text_input("Input a subdaily interval in hours")

# if interval == '':
#   st.warning("Input a suitable subdaily interval in hours")
#   st.stop()
# else:
#   interval = float(interval)

# if interval >= 24:
#   st.warning("Input a suitable subdaily interval in hours")
#   st.stop()
  
# interval_name = f"{interval}_hour_interval"

# df[interval_name] = df['datetime'].apply(lambda x: (float(x.hour//interval)))
# df_interval = df.groupby(['site', 'date', interval_name]).agg({col : 'mean' for col in variables})
# df_interval.reset_index(inplace = True)
# df_interval['day_of_year'] = (df_interval['date'].dt.strftime('%j').astype(int) - 1)
# df_day = df_interval.groupby(['site', 'day_of_year', interval_name]).agg({col : 'mean' for col in variables})
# df_day.reset_index(inplace = True)
# df_day[long_int_name] = df_day['day_of_year']//long_int
# df_long_int = df_day.groupby(['site', long_int_name, interval_name]).agg({ col : 'mean' for col in variables})
# df_long_int.reset_index(inplace = True)

# grouping_dict = {'datetime' : df, interval_name : df_interval, 'day_of_year' : df_day, long_int_name : df_long_int}


# # Grouping and graphing all relevant variables based on either day and interval or week and interval
# indicator_subset = ['day_of_year', long_int_name]
variable_subset = variables

# xaxis = st.selectbox(label = "Choose an independent variable: ", options = indicator_subset)
# dataframe = grouping_dict[xaxis]

filter_site = st.radio(label = 'Select which sites to graph:', options = ['sjer', 'soap', 'none'], index = 2)

if filter_site != 'none':
  df = df[df['site'] == filter_site]


filter_time_choice = st.checkbox(label = "Would you like to choose values to filter by time values?")

if filter_time_choice:
  slider_options = df['day_of_year'].unique().tolist()
  default_value = [x for x in slider_options if (x >= 6 and x<=42)]
  time_range = st.select_slider("Choose_day_of_year_range", options = slider_options, value = (slider_options[6], slider_options[42]))
  df = df[df['day_of_year'].isin(time_range)]

# if filter_time_choice:
#   slider_options = dataframe[xaxis].unique().tolist()
#   # default_value = [x for x in slider_options if (x >= 6 and x<=42)]
#   time_range = st.select_slider(f"Choose_{xaxis}_range", options = slider_options, value = (slider_options[42], slider_options[6]))
#   dataframe = dataframe[dataframe[xaxis].isin(time_range)]

yaxis = st.selectbox(label = "Choose a dependent variable: ", options = variable_subset)

# label = f"{xaxis}_and_{interval_name}"
# dataframe[label] = dataframe[xaxis] + interval*dataframe[interval_name]/24
# dataframe[label] = pd.to_numeric(dataframe[label], errors = 'coerce')
# # csv_name = label + '_15May2025.csv'
# # # dataframe.to_csv(csv_name)
# plt.clf()
# for site, group in dataframe.groupby("site"):
#   plt.plot(group[label], group[yaxis], label = site)
# plt.title(yaxis)
# plt.xlabel(label)
# plt.grid(True)
# plt.legend(title='Site')
# plt.tight_layout()
# # plt.show()
# st.pyplot()
# # # fig_name = f"{yaxis}_{xaxis}_{interval_name}_14May25.png"
# # # plt.savefig(fig_name)

add_graph = True

dict_df = {}
dict_df = {'df_0' : data}
i = 1

while add_graph:
  long_int = st.text_input('Input a greater-than-daily interval in days', key = f"long_int_{i}")
  if long_int == '':
    st.warning("Input a suitable subdaily interval in hours")
    st.stop()
  else:
    long_int = int(long_int)
  long_int_name = f"{long_int}_day_intervals_of_year"
  df[long_int_name] = df['day_of_year'] // long_int
  interval_loop = st.text_input("Input a subdaily interval in hours", key = f"interval_{i}")
  interval = interval_loop
  if interval == '':
    st.warning("Input a suitable subdaily interval in hours")
    st.stop()
  else:
    interval = float(interval)
  if interval >= 24:
    st.warning("Input a suitable subdaily interval in hours")
    st.stop()
  interval_name = f"{interval}_hour_interval"
  df[interval_name] = df['datetime'].apply(lambda x: (float(x.hour//interval)))
  df_interval = df.groupby(['site', 'date', interval_name]).agg({col : 'mean' for col in variables})
  df_interval.reset_index(inplace = True)
  df_interval['day_of_year'] = (df_interval['date'].dt.strftime('%j').astype(int) - 1)
  df_day = df_interval.groupby(['site', 'day_of_year', interval_name]).agg({col : 'mean' for col in variables})
  df_day.reset_index(inplace = True)
  df_day[long_int_name] = df_day['day_of_year']//long_int
  df_long_int = df_day.groupby(['site', long_int_name, interval_name]).agg({ col : 'mean' for col in variables})
  df_long_int.reset_index(inplace = True)
  grouping_dict = {'datetime' : df, interval_name : df_interval, 'day_of_year' : df_day, long_int_name : df_long_int}
  indicator_subset = ['day_of_year', long_int_name]
  variable_subset = variables
  xaxis = long_int_name
  dataframe = grouping_dict[xaxis]
  label = f"{xaxis}_and_{interval_name}"
  dataframe[label] = dataframe[xaxis] + interval*dataframe[interval_name]/24
  dataframe[label] = pd.to_numeric(dataframe[label], errors = 'coerce')
  plt.clf()
  for site, group in dataframe.groupby("site"):
    plt.plot(group[label], group[yaxis], label = site)
  plt.title(yaxis)
  plt.xlabel(label)
  plt.grid(True)
  plt.legend(title='Site')
  plt.tight_layout()
  st.pyplot()
  dict_df[f"df_{long_int}"] = dataframe
  add_graph = st.checkbox("Create additional graph?", key = f"checkbox_{i}")
  i = i+1

max_temps = {}
for frame in dict_df.keys():
  dataframe = dict_df[frame]
  max = dataframe[yaxis].max()
  max_temps[f"{frame}_max"] = max

st.write(max_temps)

min_temps = {}
for frame in dict_df.keys():
  dataframe = dict_df[frame]
  min = dataframe[yaxis].min()
  min_temps[f"{frame}_min"] = min

st.write(min_temps)


# max_diff = {}
# for frame in dict_df.keys():
#   dataframe = dict_df[frame]
#   diff = dataframe[yaxis].max() - df[yaxis].max()
#   max_diff[f"max_diff_{frame}"] = diff

# st.write(max_diff)


  
# for frame in dict_df.keys():
#   cols = [col for col in frame.columns if 'day_interval' in col]
#   frame.groupby(['site', cols]).agg({col : 'max' for col in frame.columns if col not in ['site', cols]})
#   diff = frame.groupby(['site', short
#   diff_df{f"{frame} - original" : 
  
# df
# # df1.groupby('day').agg({col : 'max'})


# # Grouping and graphing all relevant variables based on either day of year or week of year and site
# variable_subset = variables
# indicator_subset = ['day_of_year', long_int_name]

# dataframe = grouping_dict[xaxis].groupby([xaxis, 'site']).agg({col : 'mean' for col in variable_subset})
# dataframe.reset_index(inplace = True)
# plt.clf()
# for site, group in dataframe.groupby("site"):
#   plt.plot(group[xaxis], group[yaxis], label = site)
# plt.title(f"{yaxis}_avg")
# plt.xlabel(xaxis)
# plt.grid(True)
# plt.legend(title='Site')
# plt.tight_layout()
# st.pyplot()
# #     csv_name = f"{yaxis}_{xaxis}_14May25.png"
# #     plt.savefig(csv_name)
      
