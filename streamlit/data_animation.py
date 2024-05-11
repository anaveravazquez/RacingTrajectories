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

sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data
from prepare_laps import prepare_laps_data, get_specific_lap



def create_animation_frame(frame_number):
    raise NotImplementedError
    return fig


def create_base_figure(left_side_df, right_side_df, zoom, center_dict, width, height, bearing):
    fig, ax = plt.subplots()
    # Example: Load a map image or create a complex plot
    map_image = plt.imread('../Data/Map_details/map_track_cut.png')
    # add the map image to the plot
    ax.imshow(map_image, extent=[left_side_df['Longitude'].min(), right_side_df['Longitude'].max(), left_side_df['Latitude'].min(), right_side_df['Latitude'].max()])
    ax.set_xlim(left_side_df['Longitude'].min(), right_side_df['Longitude'].max())
    ax.set_ylim(left_side_df['Latitude'].min(), right_side_df['Latitude'].max())
    ax.set_aspect('auto')

    return fig, ax


def render_corner(cur_lap_df, opp_cur_lap_df, left_side_df, right_side_df, zoom = 14.4, 
                center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}, 
                width = 1400, height = 700, bearing = -50, size = 4,
                player_name = "Player", opponent_name = "Opponent"):
    filenames = []

    if not os.path.exists("animation_figures"):
        os.makedirs("animation_figures")

    base_fig, base_ax = create_base_figure(left_side_df, right_side_df, zoom = zoom, 
                center_dict = center_dict, width = width, height = height, bearing = bearing)

    # Generate and save frames
    for i in range(10):
        fig = create_animation_frame(i, cur_lap_df, opp_cur_lap_df, left_side_df, right_side_df, 
                                    zoom, center_dict, width, height, bearing, size, player_name, opponent_name)
        filename = f'animation_figures/frame_{i:03}.png'
        fig.savefig(filename)
        plt.close(fig)
        filenames.append(filename)

    # Create a GIF
    with imageio.get_writer('corner_animation.gif', mode='I', duration=1/20) as writer:  # 20 frames per second
        for filename in filenames:
            image = imageio.imread(filename)
            writer.append_data(image)



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

    base_fig, base_ax = render_corner(cur_lap_df, opp_cur_lap_df, left_side_df=left_side_df, right_side_df=right_side_df)

    print("Creating Animation finished in ", round(time.time() - start_time, 2), " seconds")

    plt.show()