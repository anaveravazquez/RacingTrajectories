import streamlit as st
import numpy as np
import pandas as pd
import sys
import os
from datetime import datetime, timedelta
sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data
from prepare_laps import prepare_laps_data, get_specific_lap
from data_visualizations import plot_track

file = ""

def page1():
    global file
    st.title("Choose a dataset to visualize:")
    # create an option to choose between the different csv files
    file_options = [x for x in os.listdir("../Data/Telemetry_data") if x.endswith(".csv")]
    file = st.selectbox("Select a dataset", file_options)
    laps_df, lap_times = prepare_laps_data(use_file=file)

    lap_times = lap_times.reset_index(drop=True)
    # height = 45 + 35 * len(lap_times)
    height = 420
    st.dataframe(lap_times, width=1000, height=height)

def page2():
    global file
    st.title("Page 2: Plotly Visualization")
    # Call your function to get the Plotly figure
    plotly_fig = plot_track(file)
    st.plotly_chart(plotly_fig, use_container_width=True)

def page3():
    global file
    st.title("Page 3: Visualization Title")
    # Your code for visualization goes here

def page4():
    global file
    st.title("Page 4: Visualization Title")
    # Your code for visualization goes here

def page5():
    global file
    st.title("Page 5: Visualization Title")
    # Your code for visualization goes here

def page6():
    global file
    st.title("Page 6: Visualization Title")
    # Your code for visualization goes here

def page7():
    global file
    st.title("Page 7: Visualization Title")
    # Your code for visualization goes here

def page8():
    global file
    st.title("Page 8: Visualization Title")
    # Your code for visualization goes here




# Initialize or increment the counter in session state
if 'last_refresh' not in st.session_state:
    # Set the initial value of the timer to the current time
    st.session_state['last_refresh'] = datetime.now()

# Function to refresh the page
def refresh_page():
    # Update the 'last_refresh' time to current time
    st.session_state['last_refresh'] = datetime.now()
    # Force a rerun of the script
    st.experimental_rerun()

# Check if five seconds have passed since the last refresh
if datetime.now() - st.session_state['last_refresh'] > timedelta(seconds=5):
    refresh_page()


# Dictionary of pages
pages = {
    "Select Dataset": page1,
    "Page 2": page2,
    "Page 3": page3,
    "Page 4": page4,
    "Page 5": page5,
    "Page 6": page6,
    "Page 7": page7,
    "Page 8": page8,
}

# Sidebar for navigation
st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(pages.keys()))

# Display the selected page
page = pages[selection]
page()
