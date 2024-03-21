import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data
from prepare_laps import prepare_laps_data, get_specific_lap



def plot_track(cur_lap_df, left_side_df, right_side_df, zoom = 14.4, center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}):
 
    # Setting up the initial view for the map
    center_lat = center_dict["Lat"]
    center_lon = center_dict["Lon"]

    print("center_lat : ", center_lat)
    print("center_lon : ", center_lon)

    # Using Plotly Express to create the scatter map for current lap data
    fig = px.scatter_mapbox(cur_lap_df, lat="Latitude", lon="Longitude", color="Speed (Km/h)", hover_name="Speed (Km/h)",
                            color_continuous_scale="Inferno")

    # Adding left and right side data as red lines
    for df, name, color in zip([left_side_df, right_side_df], ['Left Side', 'Right Side'], ['red', 'red']):
        fig.add_trace(
            go.Scattermapbox(
                lat=df['Latitude'],
                lon=df['Longitude'],
                mode='lines',
                line=dict(width=0.7, color=color),
                name=name
            )
        )


    fig.update_layout(
        title="Track Map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width  = 1400,
        height = 700,
        mapbox=dict(
            center={"lat": center_lat, "lon": center_lon},
            style="carto-darkmatter",
            zoom=zoom
        )
    )

    return fig


if __name__ == "__main__":

    # Get the Laps data
    laps_df, lap_times = prepare_laps_data(name="Ana")
    cur_lap_df = get_specific_lap(laps_df, lap_number=1) 

    # Get the left and right side of the track
    left_side_df, right_side_df = load_track_data()
    left_side_df = transform_coordinates(left_side_df)
    right_side_df = transform_coordinates(right_side_df)

    # Plot the track
    zoom = 15.9
    # Latitude is The Y-axis (More is North, Less is South)
    # Longitude is The X-axis (More is East, Less is West)
    center_dict = {"Lat":50.3264 , "Lon":6.9373}
    fig = plot_track(cur_lap_df, left_side_df, right_side_df, zoom = zoom, center_dict = center_dict)
    fig.show()
    