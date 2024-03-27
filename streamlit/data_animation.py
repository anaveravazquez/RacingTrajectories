import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import geopandas as gpd
import imageio
import sys
import time
import matplotlib.colors as mcolors

sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data
from prepare_laps import prepare_laps_data, get_specific_lap



def create_animation_frame(frame_number):
    # Your real function will generate different figures based on frame_number
    fig, ax = plt.subplots()
    ax.plot([0, frame_number], [0, frame_number])  # Example plot
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    return fig


def render_corner(cur_lap_df, opp_cur_lap_df, left_side_df, right_side_df, zoom = 14.4, 
                center_dict = {"Lat":50.33082887757034 , "Lon":6.942782900079108}, 
                width = 1400, height = 700, bearing = -50, size = 4,
                player_name = "Player", opponent_name = "Opponent"):
    filenames = []

    # Generate and save frames
    for i in range(100):
        fig = create_animation_frame(i)
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
    

    ### THIS SCRIPT NEEDS A LOT OF WORK, WHICH I CANT BE BOTHERED TO DO RIGHT NOW ####


    laps_df, lap_times = prepare_laps_data(name="Ana")
    cur_lap_df = get_specific_lap(laps_df, lap_number=36) 

    opp_laps_df, opp_lap_times = prepare_laps_data(name="Emil")
    opp_cur_lap_df = get_specific_lap(opp_laps_df, lap_number=51)

    start_time = time.time()
    print("Creating Animation starts now")



    print("Creating Animation finished in ", round(time.time() - start_time, 2), " seconds")