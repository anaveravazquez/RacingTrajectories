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
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from shapely.geometry import LineString, Point
import kaleido
import re
import json
import plotly.graph_objects as go
import io
from PIL import Image
import plotly.io as pio
from multiprocessing import Pool, cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append("../")

from data_loader import transform_coordinates, load_track_data, load_race_data, reduce_dataframe
from prepare_laps import prepare_laps_data, get_specific_lap



def base_satic_track(left_side_df, right_side_df, zoom = 14.4, 
                center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}, 
                width = 1400, height = 700, bearing = 0, size = 4,
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
                line=dict(width=0.6, color=color),
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
                        size, player_name, opponent_name, iteration):
    fig = base_track_fig

    # Normalize the 'Speed (Km/h)' column for both datasets to use the same color scale
    norm = colors.Normalize(vmin=100, vmax=400)

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

    # write as image
    file_name = f"animation_figures/fig_{iteration:04}.png"
    fig.write_image(file_name, format='png', engine="kaleido", scale=1, validate=False)

    # img_bytes = io.BytesIO()
    # fig.write_image(img_bytes, format='png', engine="kaleido", scale=1, validate=False)
    # img_bytes.seek(0)  # Rewind to the beginning of the BytesIO buffer after writing
    # image = Image.open(img_bytes)
    # image_array = np.array(image)  # Convert PIL Image to numpy array
    # img_bytes.close()
    return file_name
    # return image_array


def old_add_racing_trajectory(base_map_fig, base_map_ax, cur_lap_df, opp_cur_lap_df,
                        size, player_name, opponent_name , iteration):
    fig = base_map_fig
    ax  = base_map_ax

    # Normalize the 'Speed (Km/h)' column for both datasets to use the same color scale
    norm = Normalize(vmin=0, vmax=500)
    cmap_player = plt.get_cmap('Greens_r')
    cmap_opponent = plt.get_cmap('Oranges_r')
    
    scalar_map_player = ScalarMappable(norm=norm, cmap=cmap_player)
    scalar_map_opponent = ScalarMappable(norm=norm, cmap=cmap_opponent)

    player_colors = scalar_map_player.to_rgba(cur_lap_df['Speed (Km/h)'])
    opponent_colors = scalar_map_opponent.to_rgba(opp_cur_lap_df['Speed (Km/h)'])

    sc_player = ax.scatter(cur_lap_df['Longitude'], cur_lap_df['Latitude'], c=player_colors, s=size, label=player_name, alpha=0.7)

    sc_opponent = ax.scatter(opp_cur_lap_df['Longitude'], opp_cur_lap_df['Latitude'], c=opponent_colors, s=size, label=opponent_name, alpha=0.7)

    # Create legends
    plt.legend(handles=[sc_player, sc_opponent], loc='upper right')
    ax.axis('off')

    # Convert to an image
    canvas = FigureCanvas(fig)
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    # fig.savefig(f"animation_figures/fig_{iteration:04}.png", format='png')
    buf.seek(0)
    image = Image.open(buf)
    image_array = np.array(image)  # Convert PIL Image to numpy array
    buf.close()  # Now you can safely close the buffer
    return image_array


def process_plotly_figure_to_matplotlib(local_figure, max_lat, min_lat, max_lon, min_lon):
    # Generate the image bytes from Plotly figure
    img_bytes = io.BytesIO()
    local_figure.write_image(img_bytes, format='png', engine="kaleido", scale=1, validate=False)
    img_bytes.seek(0)  # Rewind to the beginning of the BytesIO buffer after writing
    image = Image.open(img_bytes)

    # Convert the image to an array that matplotlib can handle if necessary
    image = image.convert('RGBA')  # Ensure image is in RGBA format for matplotlib compatibility
    
    # Create a matplotlib figure and set the axis according to the lon and lat values
    fig, ax = plt.subplots()
    # set the size of the figure to match the image
    fig.set_size_inches(image.size[0] / 100, image.size[1] / 100)

    ax.axis('off')  # Turn off axis
    # Map the image to the axes coordinates defined by longitude and latitude
    ax.imshow(image, extent=[min_lon, max_lon, min_lat, max_lat], aspect='auto')

    # save the figure
    fig.savefig("animation_figures/base_fig_0000.png", format='png')

    return fig, ax


def create_single_frame(base_map_fig, filtered_cur_df, filtered_opp_df, size, player_name, opponent_name, i):
    if i/10 > filtered_cur_df['Local_Timestamp'].max() and i/20 > filtered_opp_df['Local_Timestamp'].max():
        print(f"Frame {i} skipped because it is out of bounds")
        return False

    local_filtered_cur_df = filtered_cur_df[filtered_cur_df['Local_Timestamp'] < i/10]
    local_filtered_opp_df = filtered_opp_df[filtered_opp_df['Local_Timestamp'] < i/10]
    local_image = add_racing_trajectory(base_map_fig, local_filtered_cur_df, local_filtered_opp_df, size=size, 
                                        player_name=player_name, opponent_name=opponent_name, iteration=i)
    print(f"Finished creating frame {i}")
    
    return local_image

def create_data_subset_1(lap_df, track_df = False):
    min_timestamp = 0
    max_timestamp = 40
    max_lat = 50.3345 # north most point
    min_lat = 50.3309 # south most point
    max_lon = 6.94441 # east most point
    min_lon = 6.93755   # west most point
    
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


def render_corner(filtered_cur_df, filtered_opp_df, left_side_df, right_side_df, zoom, 
                center_dict, width, height, bearing, size, frames,
                player_name = "Player", opponent_name = "Opponent",
                corner = 1):
    filenames = []
    images = []

    if not os.path.exists("animation_figures"):
        os.makedirs("animation_figures")
    if os.path.exists("corner_animation.gif"):
        # remove old files
        for file in os.listdir("animation_figures"):
            os.remove(os.path.join("animation_figures", file))

    base_map_fig = base_satic_track(left_side_df, right_side_df, zoom = zoom, 
                center_dict = center_dict, 
                width = width, height = height, bearing = 0, size = size)

    images = []
    with Pool(processes=cpu_count()//2) as pool:
        args = [(base_map_fig, filtered_cur_df, filtered_opp_df, size, player_name, opponent_name, i) for i in range(frames)]
        results = pool.starmap(create_single_frame, args)
        
        for i, image in enumerate(results):
            if image:
                images.append(image)

    # Create a GIF
    gif_path = f'Gifs/corner_animation_{corner}.gif'
    with imageio.get_writer(gif_path, mode='I', duration=1/30) as writer:  # 20 frames per second
        for filename in images:
            image = imageio.imread(filename)
            writer.append_data(image)

    return gif_path


if __name__ == "__main__":
    

    ### NOTE: This entire script was depricated, as it was taking too long to create in real time. 
    # The code will create a gif of the animation, combining in with streamlit to create a real time animation
    # Is not phesible in its current state, with the current packages.
    # Check out the Animation in "GitHub\RacingTrajectories\streamlit\Gifs\corner_animation_1.gif"


    laps_df, lap_times = prepare_laps_data(name="Ana")
    cur_lap_df = get_specific_lap(laps_df, lap_number=36) 

    opp_laps_df, opp_lap_times = prepare_laps_data(name="Emil")
    opp_cur_lap_df = get_specific_lap(opp_laps_df, lap_number=51)

    left_side_df, right_side_df = load_track_data()
    left_side_df = transform_coordinates(left_side_df)
    right_side_df = transform_coordinates(right_side_df)

    ### Corner 1 Gif Creation

    filtered_cur_df = create_data_subset_1(cur_lap_df)
    filtered_opp_df = create_data_subset_1(opp_cur_lap_df)
    left_side_df    = create_data_subset_1(left_side_df, track_df=True)
    right_side_df   = create_data_subset_1(right_side_df, track_df=True)

    corner = 1

    start_time = time.time()
    print("Creating Animation starts now")

    filtered_cur_df = render_corner(filtered_cur_df, filtered_opp_df, left_side_df=left_side_df, right_side_df=right_side_df,
                                    zoom=17, center_dict={"Lat":50.3326 , "Lon":6.9405}, width=1400, height=800, bearing=-10, size=4,
                                    frames= 400 , player_name="Ana", opponent_name="Emil", corner = corner)

    print("Creating Animation finished in ", round(time.time() - start_time, 2), " seconds")

   ### Corner 2 Gif Creation



   ### Corner 3 Gif Creation



   ### Corner 4 Gif Creation