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

# long_int = st.text_input('Input a greater-than-daily interval in days')

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

# st.write('updated')

dict_csv = {}
for name in dict_df.keys():
  frame = dict_df[name]
  # dict_csv[f"{name}_csv"] = frame.to_csv(index=False)
  frame = frame.to_csv(index = False)
  st.download_button(label = f"download_{name}", data = frame, file_name = f"{name}.csv", mime='text/csv')

dict_redundant = {}
for name in dict_df.keys():
  frame = dict_df[name]
  if ">" in name:
    interval_short = name.split('>')[1].strip()
    interval_short = int(float(interval_short))
    st.write(f"interval_short = {interval_short}")
    if interval_short == 1:
      df_1 = frame
    elif interval_short > 1:
      num_copies = interval_short - 1
      # st.write(f"num_copies = {num_copies}")
      frame[interval_name] = frame[interval_name]*interval_short
      st.write(frame)
      # st.write(dict_df[name])
      list_copies = [frame]
      for i in range(num_copies):
        # st.write(i)
        copy = frame.copy()
        copy[interval_name] = copy[interval_name] + 1
        # st.write(f"copy column names  = {copy.columns}")
        # st.write(copy)
        # st.write(f"frame column names  = {frame.columns}")
        # st.write(dict_df[name])
        # copy.set_index(interval_name, inplace = True)
        # frame.set_index(interval_name, inplace = True)
        # frame_test = len(list(set(frame[interval_name].to_list())))
        # st.write(frame_test)
        # copy_test = len(list(set(copy[interval_name].to_list())))
        # st.write(copy_test)
        # frame = pd.concat([frame, copy], ignore_index = True)
        list_copies = list_copies.append(copy)
        # test = len(list(set(frame[interval_name].to_list())))
        st.write(list_copies)
      st.write(list_copies)
      if list_copies:
        frame = pd.concat([list_copies], ignore_index = True)
        # dict_redundant[name] = frame
        frame = frame.to_csv(index = False)
        st.download_button(label = 'redundant dataframe', data = frame, file_name = 'redundant.csv', mime = 'text/csv')
      else:
        st.warning(f"No frames to concatenate for {name}")
        continue
      
dict_diff = {}
for name in dict_redundant.keys():
  frame = dict_redundant[name]
  for col in variables:
    frame[col] = frame[col] - df_1[col]
  dict_diff[name] = frame
  frame = frame.to_csv(index = False)
  st.download_button(label = f'difference_dataframe_{name}', data = frame, file_name = f'difference_dataframe_{name}.csv', mime = 'text/csv')

# st.write('updated agian')



      
# dict_diff = {}
# for n

# for name in dict_interval:
#   interval_short = int(dict_interval[name])
#   if interval_short > 1:
#     copies = interval_short - 1
#     copy = dict_df[name
    

# dict_interval = {}
# for name in dict_df.keys():
#   frame = dict_df[name]
#   if ">" in name:
#     dict_interval[name] = frame.split('<')[1].strip()

# for name in dict_interval:
#   interval_short = int(dict_interval[name])
#   if interval_short > 1:
#     copies = interval_short - 1
#     copy = dict_df[name
