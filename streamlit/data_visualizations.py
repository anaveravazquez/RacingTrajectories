import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.colors as mcolors
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import time
import os 

sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data
from prepare_laps import prepare_laps_data, get_specific_lap, create_geodataframe, extract_key_points


def plot_track(cur_lap_df, opp_lap_df, 
                left_side_df, right_side_df, 
                zoom = 14.4, center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}, 
                width = 1400, height = 700, bearing = -50, size = 4,
                player_name = "Player", opponent_name = "Opponent", animate = False, iteration = 0):
    
    ### Not in use anymore
    # with open ("./mapbox_token", "r") as file:
        # mapbox_access_token = file.read()
        # px.set_mapbox_access_token(mapbox_access_token)

    # Setting up the initial view for the map
    center_lat = center_dict["Lat"]
    center_lon = center_dict["Lon"]

    opp_informative_points = extract_key_points(opp_lap_df)
    if len(opp_informative_points) != 0:
        opp_max_speed_points = opp_informative_points[opp_informative_points['Description'].str.contains("Max Speed")].reset_index(drop=True)
        opp_min_speed_points = opp_informative_points[opp_informative_points['Description'].str.contains("Min Speed")].reset_index(drop=True)
    else:
        opp_max_speed_points = opp_informative_points
        opp_min_speed_points = opp_informative_points

    cur_informative_points = extract_key_points(cur_lap_df)
    if len(cur_informative_points) != 0:
        cur_max_speed_points = cur_informative_points[cur_informative_points['Description'].str.contains("Max Speed")].reset_index(drop=True)
        cur_min_speed_points = cur_informative_points[cur_informative_points['Description'].str.contains("Min Speed")].reset_index(drop=True)
    else:
        cur_max_speed_points = cur_informative_points
        cur_min_speed_points = cur_informative_points

    speed_bins = range(40, 180, 20)  # Speed ranges from 50 to 350, in steps of 50
    speed_labels = range(50, 190, 20)  # Midpoints of each bin for labeling

    norm = colors.Normalize(vmin=40, vmax=200)
    scalar_map = cm.ScalarMappable(norm=norm, cmap='Greens')
    scalar_map_opp = cm.ScalarMappable(norm=norm, cmap='Oranges')
    player_color_mapping = {label: colors.rgb2hex(scalar_map.to_rgba(label)) for label in speed_labels}
    opp_color_mapping = {label: colors.rgb2hex(scalar_map_opp.to_rgba(label)) for label in speed_labels}

    # Function to assign color based on speed
    def assign_color(speed, opponent=False):
        index = np.digitize(speed, speed_bins, right=True)
        if opponent:
            return opp_color_mapping[speed_labels[index - 1]]
        else:
            return player_color_mapping[speed_labels[index - 1]]


    fig = go.Figure()

    # Add segments of the trajectory for player
    current_speed_label = None
    segment_lat = []
    segment_lon = []
    segment_texts = []

    for idx, row in cur_lap_df.iterrows():
        speed = row['Speed (Km/h)']
        color = assign_color(speed)
        timestamp = row['Timestamp']
        if color != current_speed_label:
            if segment_lat:
                segment_lat.append(row['Latitude'])
                segment_lon.append(row['Longitude'])
                segment_texts.append(f"Timestamp: {timestamp} seconds<br>Speed (Km/h): {speed}")
                fig.add_trace(
                    go.Scattermapbox(
                        lat=segment_lat,
                        lon=segment_lon,
                        mode='lines',
                        line=dict(color=current_speed_label, width=2.5),
                        text = segment_texts,
                        name= player_name,
                        showlegend=False
                    )
                )
            segment_lat = [row['Latitude']]
            segment_lon = [row['Longitude']]
            segment_texts = [f"Timestamp: {timestamp} seconds<br>Speed (Km/h): {speed}"]
            current_speed_label = color
        else:
            segment_lat.append(row['Latitude'])
            segment_lon.append(row['Longitude'])
            segment_texts.append(f"Timestamp: {timestamp} seconds<br>Speed (Km/h): {speed}")

            

    # Add the last segment
    fig.add_trace(
        go.Scattermapbox(
            lat=segment_lat,
            lon=segment_lon,
            mode='lines',
            line=dict(color=current_speed_label, width=2.5),
            text = segment_texts,
            name= player_name,
            showlegend=False
        )
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=opp_lap_df['Latitude'],
            lon=opp_lap_df['Longitude'],
            mode='lines',
            marker=dict(size=size , color="Orange"),
            text = segment_texts,
            name= opponent_name,
            showlegend=False
        )
    )

    # Add segments of the trajectory for opponent
    current_speed_label = None
    segment_lat = []
    segment_lon = []
    segment_texts = []

    for idx, row in opp_lap_df.iterrows():
        speed = row['Speed (Km/h)']
        color = assign_color(speed, opponent=True)
        if color != current_speed_label:
            if segment_lat:
                segment_lat.append(row['Latitude'])
                segment_lon.append(row['Longitude'])
                segment_texts.append(f"Timestamp: {timestamp} seconds<br>Speed (Km/h): {speed}")
                fig.add_trace(
                    go.Scattermapbox(
                        lat=segment_lat,
                        lon=segment_lon,
                        mode='lines',
                        line=dict(color=current_speed_label, width=2.5),
                        text = segment_texts,
                        name= opponent_name,
                        showlegend=False
                    )
                )
            segment_lat = [row['Latitude']]
            segment_lon = [row['Longitude']]
            segment_texts = [f"Timestamp: {timestamp} seconds<br>Speed (Km/h): {speed}"]
            current_speed_label = color
        else:
            segment_lat.append(row['Latitude'])
            segment_lon.append(row['Longitude'])
            segment_texts.append(f"Timestamp: {timestamp} seconds<br>Speed (Km/h): {speed}")



    # Add the last segment
    fig.add_trace(
        go.Scattermapbox(
            lat=segment_lat,
            lon=segment_lon,
            mode='lines',
            line=dict(color=current_speed_label, width=2.5),
            text = segment_texts,
            name= opponent_name,
            showlegend=False
        )
    )


    # Adding Green Markers for Max speed points
    fig.add_trace(
        go.Scattermapbox(
            lat=cur_max_speed_points['Latitude'],
            lon=cur_max_speed_points['Longitude'],
            mode='markers',
            marker=dict(size=int(size*2.5) ,color="Green", symbol='circle'), 
            text = cur_max_speed_points.apply(lambda x: f"Timestamp: {x['Timestamp']} seconds<br>Speed (Km/h): {x['Speed (Km/h)']}<br>EVENT: {x['Description']}", axis=1),
            name= player_name,
            showlegend=False
        )
    )

    # Adding Green Markers for Min speed points
    fig.add_trace(
        go.Scattermapbox(
            lat=cur_min_speed_points['Latitude'],
            lon=cur_min_speed_points['Longitude'],
            mode='markers',
            marker=dict(size=int(size*2.5) ,color="Green" , symbol='circle'),
            text = cur_min_speed_points.apply(lambda x: f"Timestamp: {x['Timestamp']} seconds<br>Speed (Km/h): {x['Speed (Km/h)']}<br>EVENT: {x['Description']}", axis=1),
            name= player_name,
            showlegend=False
        )
    )
    
    # Adding Orange Markers for Max speed points
    fig.add_trace(
        go.Scattermapbox(
            lat=opp_max_speed_points['Latitude'],
            lon=opp_max_speed_points['Longitude'],
            mode='markers',
            marker=dict(size=int(size*2.5) ,color="Orange", symbol='circle'), # Doesn't work with 'x', 'square', 'diamond', 'cross', 'triangle', 'triangle-up', 'triangle-down', 'octagon', 'star', 'hexagon', 'diamond-tall', 'hourglass', 'bowtie', 'circle-open', 'circle-dot', 'circle-open-dot'
            text = opp_max_speed_points.apply(lambda x: f"Timestamp: {x['Timestamp']} seconds<br>Speed (Km/h): {x['Speed (Km/h)']}<br>EVENT: {x['Description']}", axis=1),
            name= opponent_name,
            showlegend=False
        )
    )
    
    # Adding Orange Markers for Min speed points
    fig.add_trace(
        go.Scattermapbox(
            lat=opp_min_speed_points['Latitude'],
            lon=opp_min_speed_points['Longitude'],
            mode='markers',
            marker=dict(size=int(size*2.5) ,color="Orange", symbol='circle'),
            text = opp_min_speed_points.apply(lambda x: f"Timestamp: {x['Timestamp']} seconds<br>Speed (Km/h): {x['Speed (Km/h)']}<br>EVENT: {x['Description']}", axis=1),
            name= opponent_name,
            showlegend=False
        )
    )

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
            # style="mapbox://styles/mapbox/satellite-streets-v11",
            zoom=zoom),
    )

    if animate:
        file_name = f"animation_figures/fig_{iteration:04}.png"
        fig.write_image(file_name, format='png', engine="kaleido", scale=1, validate=False)
        return file_name
    else:
        return fig




def plot_speed(df_player, df_opponent, player_name, opponent_name, x_lim, figsize_width, animate = False, iteration = 0):
    # Set the style of the plot
    plt.style.use('dark_background')
    
    # Create a new figure with a fixed size
    fig, ax = plt.subplots(figsize=(figsize_width, 2.5))  # Width is dynamic based on input, height is fixed
    
    # Plotting the data
    ax.plot(df_player['Local_Timestamp'], df_player['Speed (Km/h)'], color='#289603', label=f'{player_name}')
    ax.plot(df_opponent['Local_Timestamp'], df_opponent['Speed (Km/h)'], color='#FF6201', label=f'{opponent_name}')
    
    ax.set_ylim(0, 350)
    ax.set_xlim(0, x_lim)
    ax.set_yticks(range(0, 351, 50))
    
    ax.grid(True, which='both', color='grey', linestyle='-', linewidth=0.5)

    ax.set_ylabel('Speed (Km/h)')
    
    # set xticks every 5 seconds on the top axis
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(range(0, int(x_lim)+1, 5))
    ax2.set_xticklabels(range(0, int(x_lim)+1, 5))
    ax.set_xticks([])

    # Remove some of the padding
    plt.tight_layout()

    # Adding a legend
    ax.legend()
    
    if animate:
        file_name = f"animation_charts/fig_{iteration:04}.png"
        fig.savefig(file_name)
        return file_name
    else:
        return fig


if __name__ == "__main__":

    # Get the Laps data
    laps_df, lap_times = prepare_laps_data(name="Ana")
    cur_lap_df = get_specific_lap(laps_df, lap_number=36) 

    opp_laps_df, opp_lap_times = prepare_laps_data(name="Emil")
    opp_cur_lap_df = get_specific_lap(opp_laps_df, lap_number=51)

    # Get the left and right side of the track
    left_side_df, right_side_df = load_track_data()
    
    left_side_df = transform_coordinates(left_side_df)
    right_side_df = transform_coordinates(right_side_df)
    
    # Plot the track
    # Latitude is The Y-axis (More is North, Less is South)
    # Longitude is The X-axis (More is East, Less is West)
    zoom = 14.9
    center_dict = {"Lat":50.332, "Lon":6.941}
    fig = plot_track(cur_lap_df = cur_lap_df, opp_lap_df = opp_cur_lap_df, 
                    left_side_df = left_side_df, right_side_df = right_side_df,
                    zoom = zoom, center_dict = center_dict, player_name="Ana", opponent_name="Emil")
    fig.show()
    