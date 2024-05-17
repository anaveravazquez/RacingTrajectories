import pandas as pd
import imageio
import sys
import os
import time
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from shapely.geometry import LineString, Point
import kaleido
from PIL import Image
import plotly.io as pio
from multiprocessing import Pool, cpu_count

sys.path.append("../")

from data_loader import transform_coordinates, load_track_data, load_race_data, reduce_dataframe
from prepare_laps import prepare_laps_data, get_specific_lap
from data_visualizations import plot_track, plot_speed


def create_single_frame(filtered_cur_df, filtered_opp_df, size, player_name, opponent_name, i,
                        left_side_df, right_side_df, zoom, center_dict, width, height, bearing, 
                        x_time_lim,corner):

    if i/20 > filtered_cur_df['Local_Timestamp'].max() and i/20 > filtered_opp_df['Local_Timestamp'].max():
        print(f"Frame {i} skipped because it is out of bounds")
        return False

    local_filtered_cur_df = filtered_cur_df[filtered_cur_df['Local_Timestamp'] < i/20]
    local_filtered_opp_df = filtered_opp_df[filtered_opp_df['Local_Timestamp'] < i/20]

    local_image = plot_track(local_filtered_cur_df, local_filtered_opp_df, 
                            left_side_df, right_side_df, 
                            zoom, center_dict, width, height, bearing, size,
                            player_name, opponent_name, animate = True, iteration = i)

    local_speed_fig = plot_speed(local_filtered_cur_df, local_filtered_opp_df, player_name, opponent_name,
                                x_lim = x_time_lim, figsize_width = width//100, animate = True, iteration = i)

    tmp_local_image = Image.open(local_image)
    tmp_local_speed_fig = Image.open(local_speed_fig)
    
    new_image_width = max(tmp_local_image.width, tmp_local_speed_fig.width)
    new_image_height = tmp_local_image.height + tmp_local_speed_fig.height
    new_image = Image.new('RGB', (new_image_width, new_image_height))

    # Paste the matplotlib figure on top
    new_image.paste(tmp_local_speed_fig, (0, 0))

    left = 0
    upper = tmp_local_speed_fig.height
    right = tmp_local_image.width
    lower = upper + tmp_local_image.height

    tmp_local_image = tmp_local_image.crop((0, 0, min(right, new_image_width), min(lower, new_image_height - upper)))
    new_image.paste(tmp_local_image, (left, upper, right, lower))
    
    image_path = f"finished_animation_figures/frame_{i}.png"
    image_path = f"finished_animation_figures/corner_{corner}_{i}_{player_name}_{opponent_name}.png"
    new_image.save(image_path)

    print(f"Finished creating frame {i}")
    
    return image_path


def create_data_subset(lap_df, min_timestamp, max_timestamp, min_lat, max_lat, min_lon, max_lon, track_df = False):

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

    if not os.path.exists("finished_animation_figures"):
        os.makedirs("finished_animation_figures")

    if not os.path.exists("animation_charts"):
        os.makedirs("animation_charts")

    x_time_lim = max(filtered_cur_df['Local_Timestamp'].max(), filtered_cur_df['Local_Timestamp'].max())

    images = []
    with Pool(processes=cpu_count()//2) as pool:
        args = [(filtered_cur_df, filtered_opp_df, size, player_name, opponent_name, i,
                        left_side_df, right_side_df, zoom, center_dict, width, height, 
                        bearing, x_time_lim, corner) for i in range(frames)]
        results = pool.starmap(create_single_frame, args)
        
        for i, image in enumerate(results):
            if image:
                images.append(image)

    # Create a GIF
    gif_path = f'Gifs/corner_animation_{corner}_{player_name}_{opponent_name}.gif'
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

    players = ["Ana", "Emil", "Bot"]
    best_lap = [36, 51, 7]

    start_time = time.time()
    print("Creating Animation starts now")

    for player_1 in players:
        for player_2 in players:
            if player_1 != player_2:
                print(f"Creating animation for {player_1} vs {player_2}")
                
                laps_df, lap_times = prepare_laps_data(name=player_1)
                cur_lap_df = get_specific_lap(laps_df, lap_number=best_lap[players.index(player_1)]) 

                opp_laps_df, opp_lap_times = prepare_laps_data(name=player_2)
                opp_cur_lap_df = get_specific_lap(opp_laps_df, lap_number=best_lap[players.index(player_2)])

                left_side_df, right_side_df = load_track_data()
                left_side_df = transform_coordinates(left_side_df)
                right_side_df = transform_coordinates(right_side_df)

                ### Corner 1 Gif Creation
                corner = 1
                min_timestamp = 0
                max_timestamp = 40
                max_lat = 50.3345 # north most point
                min_lat = 50.3309 # south most point
                max_lon = 6.94443 # east most point
                min_lon = 6.93755   # west most point
                zoom = 16.9

                filtered_cur_df = create_data_subset(cur_lap_df , min_timestamp, max_timestamp, min_lat, max_lat, min_lon, max_lon)
                filtered_opp_df = create_data_subset(opp_cur_lap_df , min_timestamp, max_timestamp, min_lat, max_lat, min_lon, max_lon)

                

                filtered_cur_df = render_corner(filtered_cur_df, filtered_opp_df, left_side_df=left_side_df, right_side_df=right_side_df,
                                                zoom=zoom, center_dict={"Lat":50.3326 , "Lon":6.9405}, width=1400, height=600, bearing=-10, size=4,
                                                frames= 800 , player_name=player_1, opponent_name=player_2, corner = corner)

                print("\n")
                print("Current runtime: {} hours  {} minutes  {} seconds".format((time.time() - start_time)//3600, (time.time() - start_time)%3600//60, (time.time() - start_time)%60))
                print("\n")


                ### Corner 2 Gif Creation
                corner = 2
                min_timestamp = 20
                max_timestamp = 80
                # Latitude is The Y-axis (More is North (up), Less is South (down))
                # Longitude is The X-axis (More is East (right), Less is West (left))
                max_lat = 50.33 # north most point
                min_lat = 50.32 # south most point
                max_lon = 6.95 # east most point
                min_lon = 6.93   # west most point
                center_dict = {"Lat":50.32636 , "Lon":6.9372}
                zoom = 16.2
                bearing = -40

                filtered_cur_df = create_data_subset(cur_lap_df , min_timestamp, max_timestamp, min_lat, max_lat, min_lon, max_lon)
                filtered_opp_df = create_data_subset(opp_cur_lap_df , min_timestamp, max_timestamp, min_lat, max_lat, min_lon, max_lon)

                filtered_cur_df = render_corner(filtered_cur_df, filtered_opp_df, left_side_df=left_side_df, right_side_df=right_side_df,
                                                zoom=zoom, center_dict=center_dict, width=1400, height=600, bearing=bearing, size=4,
                                                frames= 800 , player_name=player_1, opponent_name=player_2, corner = corner)

                print("\n")
                print("Current runtime: {} hours  {} minutes  {} seconds".format((time.time() - start_time)//3600, (time.time() - start_time)%3600//60, (time.time() - start_time)%60))
                print("\n")

                ### Corner 3 Gif Creation
                corner = 3
                min_timestamp = 50
                max_timestamp = 200
                # Latitude is The Y-axis (More is North (up), Less is South (down))
                # Longitude is The X-axis (More is East (right), Less is West (left))
                max_lat = 50.34 # north most point
                min_lat = 50.335 # south most point
                max_lon = 6.96 # east most point
                min_lon = 6.9437   # west most point, 
                center_dict = {"Lat":50.33661654164608 , "Lon":6.947228193315168}
                zoom = 16.7
                bearing = -45

                filtered_cur_df = create_data_subset(cur_lap_df , min_timestamp, max_timestamp, min_lat, max_lat, min_lon, max_lon)
                filtered_opp_df = create_data_subset(opp_cur_lap_df , min_timestamp, max_timestamp, min_lat, max_lat, min_lon, max_lon)

                filtered_cur_df = render_corner(filtered_cur_df, filtered_opp_df, left_side_df=left_side_df, right_side_df=right_side_df,
                                                zoom=zoom, center_dict=center_dict, width=1400, height=600, bearing=bearing, size=4,
                                                frames= 800 , player_name=player_1, opponent_name=player_2, corner = corner)
                print("\n"*2)
                print("Current runtime: {} hours  {} minutes  {} seconds".format((time.time() - start_time)//3600, (time.time() - start_time)%3600//60, (time.time() - start_time)%60))
                print("\n"*2)



    print("\n"*5)
    print("Creating all Animation  {} hours  {} minutes  {} seconds".format((time.time() - start_time)//3600, (time.time() - start_time)%3600//60, (time.time() - start_time)%60))

                

