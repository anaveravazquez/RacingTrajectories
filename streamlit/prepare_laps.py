import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import math
import sys
import os
import movingpandas as mpd
from shapely.geometry import LineString, Point
import time

pd.set_option('display.max_rows', None)

sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data


def merge_lap_data(name):

    # find all the files that contain the name
    highest_laps_completed = 0
    files = [x for x in os.listdir("../Data/Telemetry_data") if name in x]
    all_laps_df = []
    idx = 0
    for file in files:
        if ".csv" in file:
            tmp_laps_df = load_race_data(file = file, remove_first_lap= True)
            tmp_laps_df = transform_coordinates(tmp_laps_df)
            if idx > 0:
                tmp_laps_df["Laps Completed"] = tmp_laps_df["Laps Completed"] + highest_laps_completed
                laps_df = pd.concat([laps_df, tmp_laps_df], ignore_index=True)
            elif idx == 0:
                laps_df = tmp_laps_df.copy()
            highest_laps_completed = laps_df["Laps Completed"].max()
            idx += 1

    laps_df = laps_df.dropna(axis=1)

    return laps_df


def extract_key_points(cur_lap_df):

    start_time = time.time()

    latitude_list = []
    longitude_list = []
    time_stamp_list = []
    speed_list = []
    description_list = []

    cur_lap_df.reset_index(drop=True, inplace=True)

    all_speeds = cur_lap_df["Speed (Km/h)"]

    for idx,row in enumerate(cur_lap_df.iterrows()):
        cur_speed = row[1]["Speed (Km/h)"]
        cur_latitude = row[1]["Latitude"]
        cur_longitude = row[1]["Longitude"]
        cur_time_stamp = row[1]["Timestamp"]
        if idx == 0:
            latitude_list.append(cur_latitude)
            longitude_list.append(cur_longitude)
            time_stamp_list.append(cur_time_stamp)
            speed_list.append(cur_speed)
            description_list.append("Starting Point")
        elif (cur_speed == all_speeds[idx-150:idx+40].max()):
            latitude_list.append(cur_latitude)
            longitude_list.append(cur_longitude)
            time_stamp_list.append(cur_time_stamp)
            speed_list.append(cur_speed)
            description_list.append(f"DECELERATION \n Max Speed at {round(cur_speed,2)} Km/h")
        elif (cur_speed == all_speeds[idx-150:idx+40].min()):
            latitude_list.append(cur_latitude)
            longitude_list.append(cur_longitude)
            time_stamp_list.append(cur_time_stamp)
            speed_list.append(cur_speed)
            description_list.append(f"ACCELERATION \n Min Speed at {round(cur_speed,2)} Km/h")
        else: 
            pass
        
        prev_speed = cur_speed
        prev_latitude = cur_latitude
        prev_longitude = cur_longitude
        prev_time_stamp = cur_time_stamp

    
    informative_df = pd.DataFrame({
        "Timestamp": time_stamp_list,
        "Latitude": latitude_list,
        "Longitude": longitude_list,
        "Speed (Km/h)": speed_list,
        "Description": description_list,
    })

    end_time = time.time()
    print(f"Time taken to extract key points: {end_time - start_time}")
    informative_df.drop_duplicates(subset=["Latitude", "Longitude", "Description"], inplace=True, keep="first")
    end_script_time = time.time()

    return informative_df 


def re_prepare_laps_data(name : str):

    laps_df = merge_lap_data(name)
    lap_times = laps_df[laps_df["NewLap"] == True]

    lap_times.sort_values(by="LapTime", inplace=True)
    lap_times.reset_index(drop=True, inplace=True)
    lap_times.reset_index(inplace=True)
    lap_times.rename(columns={"index": "Lap Placement"}, inplace=True)
    lap_times["Lap Placement"] = lap_times["Lap Placement"] + 1

    laps_df["Lap Placement"] = np.nan
    lap_time_indeces = laps_df[laps_df["NewLap"] == True].index

    for i in range(len(lap_time_indeces) - 1):
        laps_df.loc[lap_time_indeces[i]:lap_time_indeces[i + 1], "Lap Placement"] = i + 1
    lap_times = lap_times[["Lap Placement", "Laps Completed", "LapTime"]]
    lap_times = lap_times.rename(columns={"LapTime": "Lap Time", "Laps Completed": "Lap Number"})
    lap_times_formatted = lap_times["Lap Time"].apply(lambda x: str(math.floor(x / 60)) + ":" + str(round(x % 60, 3)))
    lap_times_unformatted = lap_times["Lap Time"]
    
    lap_placements = lap_times["Lap Placement"]
    lap_numbers = lap_times["Lap Number"]
    lap_times["Lap Time"] = lap_times_formatted

    # Removing redundant columns
    laps_df = laps_df[["Timestamp", "LapTime", "Speed (Km/h)", "X-Coords", "Y-Coords", "Z-Coords", "Latitude", "Longitude", "Lap Placement", "Laps Completed"]]

    if not os.path.exists("laps_data"):
        os.makedirs("laps_data")
    laps_df.to_csv(f"laps_data/{name}_laps_data.csv", index=False)
    lap_times.to_csv(f"laps_data/{name}_lap_times.csv", index=False)

    return laps_df, lap_times


def prepare_laps_data(name : str):

    if os.path.exists(f"laps_data/{name}_laps_data.csv") and os.path.exists(f"laps_data/{name}_lap_times.csv"):
        print("Reading from file")
        laps_df = pd.read_csv(f"laps_data/{name}_laps_data.csv")
        lap_times = pd.read_csv(f"laps_data/{name}_lap_times.csv")
    else:
        print("Constructing from file")
        laps_df, lap_times = re_prepare_laps_data(name)
    return laps_df, lap_times


def get_specific_lap(laps_df, lap_number=None, lap_placement=None):
    if lap_number:
        specific_lap_df = laps_df[laps_df["Laps Completed"] == lap_number]
    elif lap_placement:
        specific_lap_df = laps_df[laps_df["Lap Placement"] == lap_placement]
    else: 
        raise ValueError("Please provide either lap_number or lap_placement")

    ### Depricated line of code as we didn't find any use for it, and it caused errors in combination with plotly
    # specific_lap_gdf, specific_line_gdf = create_geodataframe(specific_lap_df)

    return specific_lap_df


def convert_points_to_linestring(gdf):
    ### Depricated function as we didn't find any use for it, and it caused errors in combination with plotly
    line = LineString(gdf.geometry.tolist())
    line_gdf = gpd.GeoDataFrame(geometry=[line], crs=gdf.crs).loc[0]
    return line_gdf


def create_geodataframe(df):
    ### Depricated function as we didn't find any use for it, and it caused errors in combination with plotly
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']),
        crs="EPSG:4326"  
    )
    line_gdf = convert_points_to_linestring(gdf)
    return gdf, line_gdf


def points_to_lines(df, groupby_column):
    """
    Convert points in a Pandas DataFrame to LineString geometries grouped by a specified column.

    Parameters:
    - df (DataFrame): Pandas DataFrame containing point coordinates.
    - groupby_column (str): Name of the column to group points by.

    Returns:
    - GeoDataFrame: GeoDataFrame containing LineString geometries.
    """
    # Groups points by specified column and aggregates into LineString geometries
    lines = df.groupby(groupby_column)['geometry'].apply(lambda x: LineString(x.tolist()) if x.size > 1 else None)
    lines_gdf = gpd.GeoDataFrame(geometry=lines.values, index=lines.index, crs=df.crs)
    
    return lines_gdf

def lines_to_trajectories(lines_gdf):
    trajectories = []
    for idx, row in lines_gdf.iterrows():
        trajectory = mpd.Trajectory(row['geometry'], idx)
        trajectories.append(trajectory)
    
    traj_collection = mpd.TrajectoryCollection(trajectories)
    
    return traj_collection


    
if __name__ == "__main__":

    # laps_df = merge_lap_data(name="Emil")
    # laps_df,lap_times = prepare_laps_data(name ="Emil")
    laps_df,lap_times = re_prepare_laps_data(name ="Ana")

    print("")
    specific_lap_df = get_specific_lap(laps_df, lap_number=5)
    print("lap_test.head(): ", specific_lap_df.head())
    print("")
    # print("specific_line_gdf: ", specific_line_gdf)
    key_points_df = extract_key_points(specific_lap_df)
    print("key_points_df")


