import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import matplotlib.colors as mcolors

sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data
from prepare_laps import prepare_laps_data, get_specific_lap



def plot_track(cur_lap_df, left_side_df, right_side_df, zoom = 14.4, center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}, width = 1400, height = 450):
 
    # Setting up the initial view for the map
    center_lat = center_dict["Lat"]
    center_lon = center_dict["Lon"]

    print("center_lat : ", center_lat)
    print("center_lon : ", center_lon)

    # Using Plotly Express to create the scatter map for current lap data, and add ["Timestamp (s)", "Speed (Km/h)", "Acceleration", X-Coords, Y-Coords] as hover data

    fig = px.scatter_mapbox(cur_lap_df, lat="Latitude", lon="Longitude", color="Speed (Km/h)", hover_name="Speed (Km/h)",
                            size=[1]*len(cur_lap_df),  size_max = 3,
                            color_continuous_scale="Inferno", hover_data=["Timestamp", "LapTime", "Speed (Km/h)", "X-Coords", "Y-Coords"])

    fig.update_layout(mapbox_bearing=-50)
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
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        width  = width,
        height = height,
        mapbox=dict(
            center={"lat": center_lat, "lon": center_lon},
            style="carto-darkmatter",
            zoom=zoom
        )
    )

    return fig


def color_interpolator_and_speed_thresholds(color1 = "#ff9500", color2 = "#00ffff", min_speed = 0, max_speed = 360, interval = 10):
    # Convert hex to RGB

    speed_thresholds = list(range(min_speed, max_speed, interval))  # From 0 to 350 with intervals of 10 km/h
    num_colors = len(speed_thresholds) + 1  # Number of colors to interpolate
    color1_rgb = np.array(mcolors.hex2color(color1))
    color2_rgb = np.array(mcolors.hex2color(color2))
    color_sequence = [mcolors.to_hex(color1_rgb * (1 - i) + color2_rgb * i) for i in np.linspace(0, 1, num_colors)]
    
    print("color_sequence len: ", len(color_sequence))
    print("speed_thresholds len: ", len(speed_thresholds))

    return color_sequence, speed_thresholds


# def plot_track(cur_lap_df, left_side_df, right_side_df, zoom = 14.4, center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}, width = 1400, height = 450):
 
#     # Example speed thresholds (adjust based on your data)
#     colors, speed_thresholds = color_interpolator_and_speed_thresholds()
#     center_lat = center_dict["Lat"]
#     center_lon = center_dict["Lon"]

#     # Create a new DataFrame to store segments
#     segments = []

#     # Iterate through your DataFrame to create segments
#     last_index = 0
#     current_color = 0
#     for i in range(1, len(cur_lap_df)):
#         # Check if the speed has changed to a different range
#         if not (cur_lap_df['Speed (Km/h)'][i-1] < speed_thresholds[current_color] == cur_lap_df['Speed (Km/h)'][i] < speed_thresholds[current_color]):
#             # Append the segment
#             segments.append((last_index, i, colors[current_color]))
#             last_index = i  # Update the last index
#             # Update the current color based on the new speed
#             current_color = sum(s < cur_lap_df['Speed (Km/h)'][i] for s in speed_thresholds)
#         # For the last segment
#         if i == len(cur_lap_df) - 1:
#             segments.append((last_index, i + 1, colors[current_color]))

#     # Initialize the figure
#     fig = go.Figure()

#     # Adding each segment as a separate trace
#     for start, end, color in segments:
#         segment_df = cur_lap_df.iloc[start:end]
#         fig.add_trace(
#             go.Scattermapbox(
#                 lat=segment_df['Latitude'],
#                 lon=segment_df['Longitude'],
#                 mode='lines',
#                 line=dict(width=2, color=color),
#                 name=f'Speed range {color}'  # This can be adjusted or removed as needed
#             )
#         )

#     # Your existing settings for the map layout
#     fig.update_layout(
#         title="Track Map",
#         margin={"r": 0, "t": 0, "l": 0, "b": 0},
#         width  = width,
#         height = height,
#         mapbox=dict(
#             center={"lat": center_lat, "lon": center_lon},  # Adjust with your actual center
#             style="carto-darkmatter",
#             zoom=zoom  # Adjust with your actual zoom level
#         ),
#         showlegend=False  # You can turn the legend on or off
#     )

#     return fig 


if __name__ == "__main__":

    # Get the Laps data
    laps_df, lap_times = prepare_laps_data(name="Ana")
    cur_lap_df = get_specific_lap(laps_df, lap_number=1) 

    # Get the left and right side of the track
    left_side_df, right_side_df = load_track_data()
    left_side_df = transform_coordinates(left_side_df)
    right_side_df = transform_coordinates(right_side_df)

    # Plot the track
    # Latitude is The Y-axis (More is North, Less is South)
    # Longitude is The X-axis (More is East, Less is West)
    zoom = 14.9
    center_dict = {"Lat":50.332, "Lon":6.941}
    fig = plot_track(cur_lap_df, left_side_df, right_side_df, zoom = zoom, center_dict = center_dict)
    fig.show()
    