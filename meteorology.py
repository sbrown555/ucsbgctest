import pandas as pd
import streamlit as st
import datetime as dt
import matplotlib.pyplot as plt

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

# Update indicator columns
variables = ['T_HMP_C', 'RH_%', 'PAR_IN_umol_photons.m2.s', 'soil_moisture_10cm_m3.m3', 'soil_moisture_30cm_m3.m3','soil_moisture_60cm_m3.m3', 'soil_moisture_90cm_m3.m3']
indicator_columns = [col for col in df.columns if col not in variables]
variable_subset = variables

filter_site = st.radio(label = 'Select which sites to graph:', options = ['sjer', 'soap', 'both'], index = 2)
if filter_site != 'both':
  df = df[df['site'] == filter_site]

yaxis = st.selectbox(label = "Choose a dependent variable: ", options = variable_subset)

add_graph = True
dict_df = {}
dict_df = {'df_0' : df}
i = 1

while add_graph:
  df = dict_df['df_0']
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
  if interval > 24:
    st.warning("Input a suitable subdaily interval in hours")
    st.stop()
  interval_name = f"{interval}_hour_interval"
  df[interval_name] = df['datetime'].apply(lambda x: (float(x.hour//interval)))
  filter_time_choice = st.checkbox(label = "Would you like to filter by time values?", key = f'filter_time_{i}')
  if filter_time_choice:
    slider_options = list(set(df[long_int_name].tolist()))
    slider_options = [int(x) for x in slider_options]
    slider_min = min(slider_options)
    slider_max = max(slider_options)
    start, end = st.slider(f"Choose_{long_int_name}_range", min_value = slider_min, max_value = slider_max, value = (slider_min, slider_max))
    df = df[(df[long_int_name] >= start) & (df[long_int_name] <= end)]
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
  dict_df[f"df_{long_int}>{interval}"] = dataframe
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

# Download option for datasets used to make graphs
dict_csv = {}
for name in dict_df.keys():
  frame = dict_df[name]
  csv_data = frame.to_csv(index = True)
  st.download_button(label = f"download_{name}", data = csv_data, file_name = f"{name}.csv", mime='text/csv')


# ___________________
# Create dataframes with differences between dataframes using different time intervals
st.write('Comparison of dataframes with different subdaily time intervals')

long_int_list = []
for name in dict_df.keys():
  frame = dict_df[name]
  for col in frame.columns:
    if 'day' in col:
      long_int_list.append(col)
  if len(set(long_int_list)) != 1:
    st.write('All greater than daily intervals should be the same length for comparison')

  

dict_redundant = {}
for name in dict_df.keys():
  frame = dict_df[name]
  if ">" in name:
    interval_short = name.split('>')[1].strip()
    interval_short = int(float(interval_short))
    # st.write(f"interval_short = {interval_short}")
    if interval_short == 1:
      df_1 = frame
    elif interval_short > 1:
      num_copies = interval_short - 1
      frame[interval_name] = frame[interval_name]*interval_short
      # st.write(frame)
      list_copies = [frame]
      for i in range(num_copies):
        copy = frame.copy()
        copy[interval_name] = copy[interval_name] + 1
        list_copies.append(copy)
      if list_copies:
        frame = pd.concat(list_copies, ignore_index = True)
        test = len(list(set(frame[interval_name].to_list())))
        frame.set_index(['site', long_int_name, interval_name], inplace=True)
        csv_data = frame.to_csv(index = True)
        st.download_button(label = 'redundant dataframe', data = csv_data, file_name = 'redundant.csv', mime = 'text/csv')
        dict_redundant[name] = frame
      else:
        st.warning(f"No frames to concatenate for {name}")
        continue

if not df_1.empty:
  dict_diff = {}
  df_1.reset_index(inplace=True)
  df_1.rename(columns={'1.0_hour_interval': interval_name}, inplace=True)
  # st.write(df_1.columns)
  df_1.set_index(['site', long_int_name, interval_name], inplace=True)
  # st.write(df_1)
  for name in dict_redundant.keys():
    frame = dict_redundant[name]
    new_frame = df_1.copy()
    for col in variables:
      new_frame[col] = frame[col] - df_1[col]
    label = f"{long_int_name}_and_1.0_hour_interval"
    new_label = f"{long_int_name}_and_2.0_hour_interval"
    new_frame[new_label] = df_1[label]
    name_diff = f"{name}_diff"
    dict_diff[name] = new_frame
    csv_data = new_frame.to_csv(index=True)
    st.download_button(label = f'difference_dataframe_{name}', data = csv_data, file_name = f'difference_dataframe_{name}.csv', mime = 'text/csv')
else:
  st.warning('for comparison of dataframes include a short time interval of 1 and make sure long intervals are the same')


  # dataframe = grouping_dict[xaxis]
  # label = f"{xaxis}_and_{interval_name}"
  # dataframe[label] = dataframe[xaxis] + interval*dataframe[interval_name]/24
  # dataframe[label] = pd.to_numeric(dataframe[label], errors = 'coerce')


# Create graphs for comparison of dataframes with different time intervals
for name in dict_diff.keys():
  st.write(name)
  st.write(dict_diff[name])
  dataframe = dict_diff[name]
  dataframe.reset_index(inplace = True)
  interval_name = dataframe.columns[2]
  # st.write(dataframe.columns)
  label = f"{dataframe.columns[1]}_and_{dataframe.columns[2]}"
  xaxis = label
  yaxis = 'T_HMP_C'
  plt.clf()
  for site, group in dataframe.groupby("site"):
    plt.plot(group[xaxis], group[yaxis], label = site)
  plt.title(yaxis)
  plt.xlabel(label)
  plt.grid(True)
  plt.legend(title='Site')
  plt.tight_layout()
  st.pyplot()
  plt.clf()
  # for col in variables:
  #   dataframe[col] = abs(dataframe[col])
  # for site, group in dataframe.groupby(['site', interval_name]).agg(col:'max'):
  #   plt.plot(group[xaxis], group[yaxis], label = site)
  # plt.title(yaxis)
  # plt.xlabel(label)
  # plt.grid(True)
  # plt.legend(title='Site')
  # plt.tight_layout()
  # st.pyplot()
# Take absolute value of specified columns
  for col in variables:
    dataframe[col] = dataframe[col].abs()  # or abs(dataframe[col])
  st.write(dataframe)
  # for site, group in dataframe.groupby(['site', interval_name]).agg({col:'max' for col in variables}):
  #   plt.plot(group[xaxis], group[yaxis], label = site)
  for site, group in dataframe.groupby("site"):
    plt.plot(group[xaxis], group[yaxis], label = site)
  plt.title(yaxis)
  plt.xlabel(label)
  plt.grid(True)
  plt.legend(title='Site')
  plt.tight_layout()
  st.pyplot()
  # sites = dataframe['site'].unique()
  # fig, axes = plt.subplots(nrows=len(sites), ncols=1, figsize=(8, 4 * len(sites)), sharex=True)
  # if len(sites) == 1:
  #   axes = [axes]
  # for ax, site in zip(axes, sites):
  #   group = dataframe[dataframe['site'] == site].groupby(interval_name).agg({xaxis: 'max', yaxis: 'max'}).reset_index()
  #   ax.plot(group[xaxis], group[yaxis], label=f"{site}")
  #   ax.set_title(f"{yaxis} - {site}")
  #   ax.set_ylabel(yaxis)
  #   ax.grid(True)
  #   ax.legend()
  # axes[-1].set_xlabel(xaxis)
  # plt.tight_layout()
  # st.pyplot(fig)
  grouped_interval = dataframe.groupby(['site',interval_name]).agg({col:'max' for col in variables})
  grouped_interval.reset_index(inplace=True)
  xaxis = interval_name
  for site, group in grouped_interval.groupby("site"):
    plt.plot(group[xaxis],group[yaxis], label = site)
  plt.title(yaxis)
  plt.xlabel(label)
  plt.grid(True)
  plt.legend(title='Site')
  plt.tight_layout()
  st.pyplot()

    
