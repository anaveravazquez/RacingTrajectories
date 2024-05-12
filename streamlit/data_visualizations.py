import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import matplotlib.colors as mcolors

sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data
from prepare_laps import prepare_laps_data, get_specific_lap, create_geodataframe, extract_key_points


def plot_track(cur_lap_df, cur_lap_line_gdf, opp_lap_df, opp_lap_line_gdf, 
                left_side_df, left_side_line_gdf, right_side_df, right_side_line_gdf, 
                zoom = 14.4, center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}, 
                width = 1400, height = 700, bearing = -50, size = 4,
                player_name = "Player", opponent_name = "Opponent"):
    
    # with open ("./mapbox_token", "r") as file:
        # mapbox_access_token = file.read()
        # px.set_mapbox_access_token(mapbox_access_token)

    # Setting up the initial view for the map
    center_lat = center_dict["Lat"]
    center_lon = center_dict["Lon"]

    # Normalize the 'Speed (Km/h)' column for both datasets to use the same color scale
    norm = colors.Normalize(vmin=50, vmax=350)

    scalar_map = cm.ScalarMappable(norm=norm, cmap='Greens_r')
    scalar_map_opp = cm.ScalarMappable(norm=norm, cmap='Oranges_r')
    
    # Convert speed values to colors
    opp_speed_colors = [colors.rgb2hex(scalar_map.to_rgba(speed)) for speed in opp_cur_lap_df['Speed (Km/h)']]
    speed_colors =     [colors.rgb2hex(scalar_map_opp.to_rgba(speed)) for speed in cur_lap_df['Speed (Km/h)']]


    cur_informative_points = extract_key_points(cur_lap_df)
    opp_informative_points = extract_key_points(opp_lap_df)


    fig = go.Figure()

    # Adding Green line
    fig.add_trace(
        go.Scattermapbox(
            lat=cur_lap_df['Latitude'],
            lon=cur_lap_df['Longitude'],
            mode='lines',
            marker=dict(size=size ,color="Green"), 
            # text = cur_lap_df.apply(lambda x: f"Timestamp: {x['Timestamp']}<br>Speed (Km/h): {x['Speed (Km/h)']}", axis=1),
            name= player_name,
            showlegend=False,
            hoverinfo='none'
        )
    )

    # Adding Green Markers for informative points
    fig.add_trace(
        go.Scattermapbox(
            lat=cur_informative_points['Latitude'],
            lon=cur_informative_points['Longitude'],
            mode='markers',
            marker=dict(size=int(size*2.5) ,color="Green"), 
            text = cur_informative_points.apply(lambda x: f"Timestamp: {x['Timestamp']}<br>Speed (Km/h): {x['Speed (Km/h)']}<br>EVENT: {x['Description']}", axis=1),
            name= player_name,
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=opp_cur_lap_df['Latitude'],
            lon=opp_cur_lap_df['Longitude'],
            mode='lines',
            marker=dict(size=size , color="Orange"),
            # text = opp_cur_lap_df.apply(lambda x: f"Timestamp: {x['Timestamp']}<br>Speed (Km/h): {x['Speed (Km/h)']}", axis=1),
            name= opponent_name,
            showlegend=False,
            hoverinfo='none'
        )
    )

    fig.add_trace(
        go.Scattermapbox(
            lat=opp_informative_points['Latitude'],
            lon=opp_informative_points['Longitude'],
            mode='markers',
            marker=dict(size=int(size*2.5) ,color="Orange"), 
            text = opp_informative_points.apply(lambda x: f"Timestamp: {x['Timestamp']}<br>Speed (Km/h): {x['Speed (Km/h)']}<br>EVENT: {x['Description']}", axis=1),
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

    return fig


def add_slider_to_map(fig):

    steps = []
    for i in range(int(50), int(300), 10): 
        i = i /10
        step = dict(
            method="update",
            args=[{'visible': [
                ((cur_lap_df['Timestamp'] >= i) & (cur_lap_df['Timestamp'] < i + 60)).tolist(),
                ((opp_cur_lap_df['Timestamp'] >= i) & (opp_cur_lap_df['Timestamp'] < i + 60)).tolist(),
                True,  # Keep the track visible
                True   # Keep the track visible
            ]}],
        )
        steps.append(step)

    sliders = [dict(
        active=0,
        currentvalue={"prefix": "Timestamp: "},
        pad={"t": 50},
        steps=steps
    )]

    fig.update_layout(sliders=sliders)

    return fig


if __name__ == "__main__":

    # Get the Laps data
    laps_df, lap_times = prepare_laps_data(name="Ana")
    cur_lap_df, cur_line_gdf = get_specific_lap(laps_df, lap_number=36) 

    opp_laps_df, opp_lap_times = prepare_laps_data(name="Emil")
    opp_cur_lap_df, opp_cur_line_gdf = get_specific_lap(opp_laps_df, lap_number=51)

    # Get the left and right side of the track
    left_side_df, right_side_df = load_track_data()
    
    left_side_df = transform_coordinates(left_side_df)
    left_side_gdf, left_side_line_gdf = create_geodataframe(left_side_df)
    right_side_df = transform_coordinates(right_side_df)
    right_side_gdf, right_side_line_gdf = create_geodataframe(right_side_df)
    
    # Plot the track
    # Latitude is The Y-axis (More is North, Less is South)
    # Longitude is The X-axis (More is East, Less is West)
    zoom = 14.9
    center_dict = {"Lat":50.332, "Lon":6.941}
    fig = plot_track(cur_lap_df = cur_lap_df, cur_lap_line_gdf = cur_line_gdf, 
                    opp_lap_df = opp_cur_lap_df, opp_lap_line_gdf = opp_cur_line_gdf, 
                    left_side_df = left_side_df, right_side_df = right_side_df,
                    left_side_line_gdf = left_side_line_gdf, right_side_line_gdf = right_side_line_gdf,
                    zoom = zoom, center_dict = center_dict, player_name="Ana", opponent_name="Emil")
    fig.show()
    