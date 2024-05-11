import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import geopandas as gpd
import imageio
import sys
import os
import time
import matplotlib.colors as mcolors
import movingpandas as mpd
from shapely.geometry import LineString, Point
import kaleido
import re
import json
import plotly.graph_objects as go
import plotly.io as pio
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append("../")

from data_loader import transform_coordinates, load_track_data, load_race_data, reduce_dataframe
from prepare_laps import prepare_laps_data, get_specific_lap



def base_satic_track(left_side_df, right_side_df, zoom = 14.4, 
                center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}, 
                width = 1400, height = 700, bearing = -50, size = 4,
                player_name = "Player", opponent_name = "Opponent"):
    
    # Setting up the initial view for the map
    center_lat = center_dict["Lat"]
    center_lon = center_dict["Lon"]
    
    fig = go.Figure()

    fig.update_layout(mapbox_bearing=bearing)
    # Adding left and right side data as red lines
    for df, name, color in zip([left_side_df, right_side_df], ['Left Side', 'Right Side'], ['red', 'red']):
        fig.add_trace(
            go.Scattermapbox(
                lat=df['Latitude'],
                lon=df['Longitude'],
                mode='lines',
                line=dict(width=0.4, color=color),
                name=name,
                hoverinfo='none',
                showlegend=False
            )
        )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width  = width,
        height = height,
        mapbox=dict(
            center={"lat": center_lat, "lon": center_lon},
            style="carto-darkmatter",
            zoom=zoom),
    )

    return fig
    

def add_racing_trajectory(base_track_fig, cur_lap_df, opp_cur_lap_df,
                        size, player_name = "Player", opponent_name = "Opponent"):
    fig = go.Figure(base_track_fig)

    # Normalize the 'Speed (Km/h)' column for both datasets to use the same color scale
    norm = colors.Normalize(vmin=0, vmax=500)

    scalar_map = cm.ScalarMappable(norm=norm, cmap='Greens_r')
    scalar_map_opp = cm.ScalarMappable(norm=norm, cmap='Oranges_r')
    
    speed_colors =     [colors.rgb2hex(scalar_map_opp.to_rgba(speed)) for speed in cur_lap_df['Speed (Km/h)']]
    opp_speed_colors = [colors.rgb2hex(scalar_map.to_rgba(speed)) for speed in opp_cur_lap_df['Speed (Km/h)']]

    fig.add_trace(
    go.Scattermapbox(
        lat=cur_lap_df['Latitude'],
        lon=cur_lap_df['Longitude'],
        mode='markers',
        marker=dict(size=size, color=speed_colors),
        hoverinfo='none',
        name= player_name,
        showlegend=False
        )
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=opp_cur_lap_df['Latitude'],
            lon=opp_cur_lap_df['Longitude'],
            mode='markers',
            marker=dict(size=size, color=opp_speed_colors),
            hoverinfo='none',
            name= opponent_name,
            showlegend=False
        )
    )

    return fig




def process_frame(i, filtered_cur_df, filtered_opp_df, base_fig, size, player_name, opponent_name):
    print(f"Creating frame {i}")
    local_filtered_cur_df = filtered_cur_df[filtered_cur_df['Local_Timestamp'] < i/3]
    local_filtered_opp_df = filtered_opp_df[filtered_opp_df['Local_Timestamp'] < i/3]
    fig = add_racing_trajectory(base_fig, local_filtered_cur_df, local_filtered_opp_df, size=size, player_name=player_name, opponent_name=opponent_name)
    
    filename = f'animation_figures/frame_{i:04}.png'
    fig.write_image(filename, format="png", engine="kaleido", scale=1, validate=False)
    return filename


def create_data_subset_1(lap_df, track_df = False):
    min_timestamp = 0
    max_timestamp = 40
    max_lat = 50.3345
    min_lat = 50.3315
    max_lon = 6.944412
    min_lon = 6.9375
    
    if track_df:
        conditions = (
            (lap_df['Timestamp']  > min_timestamp) )
    else: 
        conditions = (
            (lap_df['Timestamp'] > min_timestamp) &
            (lap_df['Timestamp'] < max_timestamp) &
            (lap_df['Longitude'] > min_lon) &
            (lap_df['Longitude'] < max_lon) &
            (lap_df['Latitude']  > min_lat) &
            (lap_df['Latitude']  < max_lat)
        )

    filtered_df = lap_df[conditions]    
    
    local_min_timestamp = filtered_df['Timestamp'].min()
    filtered_df['Local_Timestamp'] = filtered_df['Timestamp'] - local_min_timestamp
    filtered_df = filtered_df[['Local_Timestamp', 'Timestamp', 'Speed (Km/h)', 'Latitude', 'Longitude']]

    return filtered_df


def render_corner(cur_lap_df, opp_cur_lap_df, left_side_df, right_side_df, zoom = 14.4, 
                center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}, 
                width = 700, height = 400, bearing = -50, size = 4, frames = 100,
                player_name = "Player", opponent_name = "Opponent"):
    filenames = []
    images = []

    if not os.path.exists("animation_figures"):
        os.makedirs("animation_figures")

    filtered_cur_df = create_data_subset_1(cur_lap_df)
    filtered_opp_df = create_data_subset_1(opp_cur_lap_df)
    left_side_df    = create_data_subset_1(left_side_df, track_df=True)
    right_side_df   = create_data_subset_1(right_side_df, track_df=True)

    base_fig = base_satic_track(left_side_df, right_side_df, zoom = zoom, 
                center_dict = center_dict, 
                width = width, height = height, bearing = bearing, size = size)

    filenames = []
    with ThreadPoolExecutor(max_workers=16) as executor:  # Adjust max_workers based on your CPU
        # Submitting all tasks to the executor
        future_to_frame = {executor.submit(process_frame, i, filtered_cur_df, filtered_opp_df, base_fig, size, player_name, opponent_name): i for i in range(frames)}
        
        for future in as_completed(future_to_frame):
            filename = future.result()  # Getting the result (filename) from the future
            filenames.append(filename)
            print(f"Finished {filename}")

    # Create a GIF
    with imageio.get_writer('corner_animation.gif', mode='I', duration=1/20) as writer:  # 20 frames per second
        for img_bytes in images:
            # Read image from bytes
            image = imageio.imread(img_bytes)
            writer.append_data(image)
        # for filename in filenames:
        #     # convert html to png
        #     image = imageio.imread(filename)
        #     writer.append_data(image)



if __name__ == "__main__":
    

    laps_df, lap_times = prepare_laps_data(name="Ana")
    cur_lap_df = get_specific_lap(laps_df, lap_number=36) 

    opp_laps_df, opp_lap_times = prepare_laps_data(name="Emil")
    opp_cur_lap_df = get_specific_lap(opp_laps_df, lap_number=51)

    left_side_df, right_side_df = load_track_data()
    left_side_df = transform_coordinates(left_side_df)
    right_side_df = transform_coordinates(right_side_df)

    start_time = time.time()
    print("Creating Animation starts now")

    filtered_cur_df = render_corner(cur_lap_df, opp_cur_lap_df, left_side_df=left_side_df, right_side_df=right_side_df,
                                    zoom=16.2, center_dict={"Lat":50.3326 , "Lon":6.9405}, width=700, height=400, bearing=-10, size=4,
                                    frames= 100 , player_name="Ana", opponent_name="Emil")

    print("Creating Animation finished in ", round(time.time() - start_time, 2), " seconds")

   