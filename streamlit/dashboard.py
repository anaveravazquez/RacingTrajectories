import streamlit as st
import numpy as np
import pandas as pd
import sys
import os 
import math
from datetime import datetime, timedelta
sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data
from prepare_laps import prepare_laps_data, re_prepare_laps_data, get_specific_lap
from data_visualizations import plot_track

def update_start_time():
    st.session_state.start_time = datetime.now()


def downloade_track_data():
    if 'left_side_df' not in st.session_state or 'right_side_df' not in st.session_state:
        left_side_df, right_side_df = load_track_data()
        left_side_df = transform_coordinates(left_side_df)
        right_side_df = transform_coordinates(right_side_df)

        st.session_state['left_side_df'] = left_side_df
        st.session_state['right_side_df'] = right_side_df


def update_global(name):
    # if the name is different, then we need to update the track data and the name
    if 'name' not in st.session_state or st.session_state['name'] != name:
        st.session_state['name'] = name
    
    if f'laps_df_{name}' in st.session_state and f'lap_times_{name}' in st.session_state:
        st.session_state['laps_df'] = st.session_state[f'laps_df_{name}']
        st.session_state['lap_times'] = st.session_state[f'lap_times_{name}']
    else: 
        laps_df, lap_times = prepare_laps_data(name = name)
        lap_times = lap_times.reset_index(drop=True)
        st.session_state['laps_df'] = laps_df
        st.session_state['lap_times'] = lap_times
        st.session_state[f'laps_df_{name}'] = laps_df
        st.session_state[f'lap_times_{name}'] = lap_times


def update_global_opponent(name):
    if 'name_opponent' not in st.session_state or st.session_state['name_opponent'] != name:
        st.session_state['name_opponent'] = name
    
    if f'laps_df_{name}' in st.session_state and f'lap_times_{name}' in st.session_state:
        st.session_state['laps_df_opponent'] = st.session_state[f'laps_df_{name}']
        st.session_state['lap_times_opponent'] = st.session_state[f'lap_times_{name}']
    else: 
        laps_df, lap_times = prepare_laps_data(name = name)
        lap_times = lap_times.reset_index(drop=True)
        st.session_state['laps_df_opponent'] = laps_df
        st.session_state['lap_times_opponent'] = lap_times
        st.session_state[f'laps_df_{name}'] = laps_df
        st.session_state[f'lap_times_{name}'] = lap_times


def selected_lap_number(name):
    lap_times = st.session_state['lap_times']

    list_of_lap_options = lap_times["Lap Number"].tolist()
    list_of_lap_times   = lap_times["Lap Time"].tolist()
    list_of_lap_options = [str(x) + ". " + " ---> " + list_of_lap_times[idx]  for idx,x in enumerate(list_of_lap_options)]

    lap_number = st.sidebar.selectbox("Select a lap number", list_of_lap_options)
    lap_number = int(lap_number.split(".")[0]) -1

    if 'lap_number' not in st.session_state or st.session_state['lap_number'] != lap_number:
        st.session_state['lap_number'] = lap_number
        update_track_data(name)


def selected_lap_number_opponent(name):
    lap_times = st.session_state['lap_times_opponent']

    list_of_lap_options = lap_times["Lap Number"].tolist()
    list_of_lap_times   = lap_times["Lap Time"].tolist()
    list_of_lap_options = [str(x) + ". " + " ---> " + list_of_lap_times[idx]  for idx,x in enumerate(list_of_lap_options)]

    lap_number = st.sidebar.selectbox("Select opponent lap number", list_of_lap_options)
    lap_number = int(lap_number.split(".")[0]) -1

    if 'lap_number_opponent' not in st.session_state or st.session_state['lap_number_opponent'] != lap_number:
        st.session_state['lap_number_opponent'] = lap_number
        update_track_data(name, opponent = True)


def update_track_data(name, opponent = False):
    if opponent:
        lap_number = st.session_state['lap_number_opponent']
        laps_df = st.session_state['laps_df_opponent']
        cur_lap_df = get_specific_lap(laps_df, lap_number=lap_number)
        st.session_state['cur_lap_df_opponent'] = cur_lap_df
    else: 
        lap_number = st.session_state['lap_number']
        laps_df = st.session_state['laps_df']
        cur_lap_df = get_specific_lap(laps_df, lap_number=lap_number)
        st.session_state['cur_lap_df'] = cur_lap_df


def page1():
    
    
    lap_times = st.session_state['lap_times']
    laps_df = st.session_state['laps_df']

    opp_lap_times = st.session_state['lap_times_opponent']
    opp_laps_df = st.session_state['laps_df_opponent']

    col1, col2 = st.columns(2)
    height = 550
    with col1:
        st.title(f"{st.session_state['name']}")
        # avg_lap_time_ms
        avg_lap_time = lap_times["Lap Time"].apply(lambda x: float(x.split(":")[0]) * 60 + float(x.split(":")[1])).mean()
        avg_lap_time_min = str(math.floor(avg_lap_time / 60)) 
        avg_lap_time_sec = str(round(avg_lap_time % 60, 3))
        if len(avg_lap_time_sec.split(".")[0]) == 1:
            avg_lap_time_sec = "0"+avg_lap_time_sec
        avg_lap_time = avg_lap_time_min + ":" + avg_lap_time_sec
        # Display Total Laps and Best Lap but add space between the two
        st.markdown(f"```\nTotal Laps: {len(lap_times)}            Avg. Lap: {avg_lap_time}            Best Lap: {lap_times['Lap Time'][0]}\n```", unsafe_allow_html=True)
        st.dataframe(lap_times, height=height, use_container_width=True)

    with col2:
        # Centered text
        st.title(f"{st.session_state['name_opponent']}")
        opp_avg_lap_time = opp_lap_times["Lap Time"].apply(lambda x: float(x.split(":")[0]) * 60 + float(x.split(":")[1])).mean()
        opp_avg_lap_time_min = str(math.floor(opp_avg_lap_time / 60)) 
        opp_avg_lap_time_sec = str(round(opp_avg_lap_time % 60, 3))
        if len(opp_avg_lap_time_sec.split(".")[0]) == 1:
            opp_avg_lap_time_sec = "0"+opp_avg_lap_time_sec
        opp_avg_lap_time = opp_avg_lap_time_min + ":" + opp_avg_lap_time_sec
        # Display Total Laps and Best Lap but add space between the two
        st.markdown(f"```\nBest Lap: {opp_lap_times['Lap Time'][0]}            Avg. Lap: {opp_avg_lap_time}            Total Laps: {len(opp_lap_times)}\n```", unsafe_allow_html=True)
        st.dataframe(opp_lap_times[["Lap Time", "Lap Number", "Lap Placement"]], use_container_width=True,  height=height)
    
    


def page2():
    
    st.title("Overview of Lap")
    # Crete an element where you can select the lap number that is not a slider 
    left_side_df = st.session_state['left_side_df']
    right_side_df = st.session_state['right_side_df']
    cur_lap_df = st.session_state['cur_lap_df']
    opp_cur_lap_df = st.session_state['cur_lap_df_opponent']

    zoom = 14.9
    center_dict = {"Lat":50.332, "Lon":6.941}
    plotly_fig = plot_track(cur_lap_df, opp_cur_lap_df, left_side_df, right_side_df, zoom = zoom, 
                            center_dict = center_dict , player_name = st.session_state['name'], opponent_name = st.session_state['name_opponent'])
    st.plotly_chart(plotly_fig, use_container_width=True)


def page3():

    st.title("Corner 1")
    left_side_df = st.session_state['left_side_df']
    right_side_df = st.session_state['right_side_df']
    cur_lap_df = st.session_state['cur_lap_df']
    opp_cur_lap_df = st.session_state['cur_lap_df_opponent']

    # Latitude is The Y-axis (More is North (up), Less is South (down))
    # Longitude is The X-axis (More is East (left), Less is West (right))
    center_dict = {"Lat":50.3325 , "Lon":6.9402}
    zoom = 16.6

    plotly_fig = plot_track(cur_lap_df, opp_cur_lap_df, left_side_df, right_side_df, zoom = zoom, 
                            center_dict = center_dict , player_name = st.session_state['name'], opponent_name = st.session_state['name_opponent'])
    st.plotly_chart(plotly_fig, use_container_width=True)


def page4():

    st.title("Corner 2")

    left_side_df = st.session_state['left_side_df']
    right_side_df = st.session_state['right_side_df']
    lap_number = st.session_state['lap_number']
    cur_lap_df = st.session_state['cur_lap_df']
    opp_cur_lap_df = st.session_state['cur_lap_df_opponent']

    # Latitude is The Y-axis (More is North (up), Less is South (down))
    # Longitude is The X-axis (More is East (left), Less is West (right))
    center_dict = {"Lat":50.3262 , "Lon":6.9368}
    zoom = 16.6

    plotly_fig = plot_track(cur_lap_df, opp_cur_lap_df, left_side_df, right_side_df, zoom = zoom, bearing = -50, 
                            center_dict = center_dict, player_name = st.session_state['name'], opponent_name = st.session_state['name_opponent'])
    st.plotly_chart(plotly_fig, use_container_width=True)


def page5():

    st.title("Corner 3")
    st.write("Needs to be implemented...")

    left_side_df = st.session_state['left_side_df']
    right_side_df = st.session_state['right_side_df']
    lap_number = st.session_state['lap_number']
    cur_lap_df = st.session_state['cur_lap_df']
    opp_cur_lap_df = st.session_state['cur_lap_df_opponent']

    # Latitude is The Y-axis (More is North (up), Less is South (down))
    # Longitude is The X-axis (More is East (left), Less is West (right))

    # FIX ME
    # center_dict = {"Lat":50.3264 , "Lon":6.9373}
    # zoom = 15.8

    # plotly_fig = plot_track(cur_lap_df, opp_cur_lap_df, left_side_df, right_side_df, zoom = zoom, center_dict = center_dict)
    # st.plotly_chart(plotly_fig, use_container_width=True)

def page6():

    st.title("Page 6: Visualization Title")
    # Your code for visualization goes here

# def page7():
#     global name
#     st.title("Page 7: Visualization Title")
#     # Your code for visualization goes here

# def page8():
#     global name
#     st.title("Page 8: Visualization Title")
#     # Your code for visualization goes here



#### RUNS FROM HERE. DO NOT MAKE (IF__NAME__ == "__MAIN__") AS IT DOESN'T WORK WITH STREAMLIT  ####)


# Pre-requisites
st.set_page_config(layout="wide")
update_start_time()
downloade_track_data()


players   = ['Emil','Ana','Bot']
opponents = ['Ana','Emil','Bot']

# Sidebar for Player
st.sidebar.title('Select Player')
name = st.sidebar.selectbox('Choose a player', players, key='name')
update_global(name = name)

# Sidebar for specific Lap Player
selected_lap_number(name)


# # Sidebar for Opponent
st.sidebar.title('Select Opponent')
name_opponent = st.sidebar.selectbox('Choose an opponent', opponents , key='name_opponent')
update_global_opponent(name = name_opponent)

# # Sidebar for specific Lap Opponent
selected_lap_number_opponent(name_opponent)



# Dictionary of pages
pages = {
    "Select Dataset": page1,
    "Whole Track": page2,
    "Section 1"  : page3,
    "Section 2" : page4,
    "Section 3": page5,
    "Page 6": page6
}

# Sidebar for navigation
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(pages.keys()))

# for _ in range(14): 
#     st.sidebar.write("")  # This adds some space between the stuff and the button

if 'start_time' in st.session_state:
    elapsed_time = datetime.now() - st.session_state.start_time
    # Display the elapsed time in the sidebar
    st.sidebar.write("")  # You can use empty writes to add space if needed
    st.sidebar.write(f"Loading time: {elapsed_time.seconds}s {elapsed_time.microseconds // 1000}ms")

st.sidebar.button("Recompute Data for {}".format(name), on_click=re_prepare_laps_data, args=([name]), help=f"Recomputes and cleans the dataset for {name}")



# Display the selected page
page = pages[selection]
page()
