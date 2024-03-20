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



def plot_track(use_file : str, lap_number: int = 1, lap_placement: int = 1 ):
    laps_df, lap_times = prepare_laps_data(use_file=use_file)
    left_side_df, right_side_df = load_track_data()
    left_side_df = transform_coordinates(left_side_df)
    right_side_df = transform_coordinates(right_side_df)

    cur_lap_df = get_specific_lap(laps_df, lap_number=lap_number)

    # Setting up the initial view for the map
    center_lat = cur_lap_df.iloc[0]['Latitude']  - 0.0048
    center_lon = cur_lap_df.iloc[0]['Longitude'] - 0.005

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
                line=dict(width=1, color=color),
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
            zoom=14.4
        )
    )

    return fig


if __name__ == "__main__":
    fig = plot_track(use_file="assetto_corsa_telemetry_F1_Emil_test2_30Laps.csv", lap_placement=1)
    fig.show()
    