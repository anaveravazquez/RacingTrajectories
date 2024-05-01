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
from shapely.geometry import LineString
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
                # print("highest_laps_completed : ", highest_laps_completed)
                # print("min tmp_laps_df['Laps Completed'] : ", tmp_laps_df["Laps Completed"].min())
                # print("max tmp_laps_df['Laps Completed'] : ", tmp_laps_df["Laps Completed"].max())

                tmp_laps_df["Laps Completed"] = tmp_laps_df["Laps Completed"] + highest_laps_completed
                # print("min tmp_laps_df['Laps Completed'] : ", tmp_laps_df["Laps Completed"].min())
                # print("max tmp_laps_df['Laps Completed'] : ", tmp_laps_df["Laps Completed"].max())
                laps_df = pd.concat([laps_df, tmp_laps_df], ignore_index=True)
                # list all the coutns of the values in a column called "Lap Completed"
            elif idx == 0:
                laps_df = tmp_laps_df.copy()
            highest_laps_completed = laps_df["Laps Completed"].max()
            idx += 1

    # Remove columns containing only NaN
    laps_df = laps_df.dropna(axis=1)

    return laps_df


def extract_key_points(cur_lap_df):

    # informative_df is a dataframe containing the key points of the lap 
    # that is, point of every 20 Km/h speed change, 
    # Start breaking, stop breaking
    # Start accelerating and stop accelerating
    start_time = time.time()

    latitude_list = []
    longitude_list = []
    time_stamp_list = []
    speed_list = []
    acceleration_list = []
    description_list = []

    all_speeds = cur_lap_df["Speed (Km/h)"]

    for idx,row in enumerate(cur_lap_df.iterrows()):
        cur_speed = row[1]["Speed (Km/h)"]
        cur_latitude = row[1]["Latitude"]
        cur_longitude = row[1]["Longitude"]
        cur_time_stamp = row[1]["Timestamp"]
        recorded_row = False
        if idx == 0:
            latitude_list.append(cur_latitude)
            longitude_list.append(cur_longitude)
            time_stamp_list.append(cur_time_stamp)
            speed_list.append(cur_speed)
            description_list.append("Starting Point")
            recorded_row = True
        elif cur_speed > prev_speed + 20:
            latitude_list.append(cur_latitude)
            longitude_list.append(cur_longitude)
            time_stamp_list.append(cur_time_stamp)
            speed_list.append(cur_speed)
            description_list.append(f"Increasing Speed {cur_speed} Km/h")
            recorded_row = True
        elif cur_speed < prev_speed - 20:
            latitude_list.append(cur_latitude)
            longitude_list.append(cur_longitude)
            time_stamp_list.append(cur_time_stamp)
            speed_list.append(cur_speed)
            description_list.append(f"Decreasing Speed {cur_speed} Km/h")
            recorded_row = True
        elif (cur_speed == all_speeds[idx-400:idx+400].max()) and (cur_speed > all_speeds[idx-400:idx-2].max()) and (cur_speed > all_speeds[idx+2:idx+400].max()) :
            latitude_list.append(cur_latitude)
            longitude_list.append(cur_longitude)
            time_stamp_list.append(cur_time_stamp)
            speed_list.append(cur_speed)
            description_list.append(f"Max Speed at {cur_speed} Km/h")
            recorded_row = True
        elif (cur_speed == all_speeds[idx-400:idx+400].min()) and (cur_speed < all_speeds[idx-400:idx-2].min()) and (cur_speed < all_speeds[idx+2:idx+400].min()) :
            latitude_list.append(cur_latitude)
            longitude_list.append(cur_longitude)
            time_stamp_list.append(cur_time_stamp)
            speed_list.append(cur_speed)
            description_list.append(f"Min Speed at {cur_speed} Km/h")
            recorded_row = True
        else:
            recorded_row = False
        
        if recorded_row:
            # only set prev_speed, prev_latitude, prev_longitude, prev_time_stamp if a row has been added
            prev_rec_speed = cur_speed
            prev_rec_latitude = cur_latitude
            prev_rec_longitude = cur_longitude
            prev_rec_time_stamp = cur_time_stamp
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

    informative_df.drop_duplicates(subset=["Latitude", "Longitude", "Description"], inplace=True)

    end_script_time = time.time()

    return informative_df 


def re_prepare_laps_data(name : str):

    laps_df = merge_lap_data(name)
    
    lap_times = laps_df[laps_df["NewLap"] == True]

    # Create a dataframe called lap_times the only contains rows of the first entry ecah each lap, where "NewLap" is not being used as a column

    lap_times.sort_values(by="LapTime", inplace=True)
    lap_times.reset_index(drop=True, inplace=True)
    lap_times.reset_index(inplace=True)
    lap_times.rename(columns={"index": "Lap Placement"}, inplace=True)
    lap_times["Lap Placement"] = lap_times["Lap Placement"] + 1

    laps_df["Lap Placement"] = np.nan
    lap_time_indeces = laps_df[laps_df["NewLap"] == True].index

    # Add Lap Placement to each run
    for i in range(len(lap_time_indeces) - 1):
        laps_df.loc[lap_time_indeces[i]:lap_time_indeces[i + 1], "Lap Placement"] = i + 1
    lap_times = lap_times[["Lap Placement", "Laps Completed", "LapTime"]]
    lap_times = lap_times.rename(columns={"LapTime": "Lap Time", "Laps Completed": "Lap Number"})
    # change lap time to minutes and seconds format
    lap_times_formatted = lap_times["Lap Time"].apply(lambda x: str(math.floor(x / 60)) + ":" + str(round(x % 60, 3)))
    lap_times_unformatted = lap_times["Lap Time"]
    
    lap_placements = lap_times["Lap Placement"]
    lap_numbers = lap_times["Lap Number"]
    # for i in range(len(lap_times_formatted)):
    #     print(f"Lap Placement: {lap_placements[i]:<4}    Lap Number: {lap_numbers[i]:<4}    Unformatted: {lap_times_unformatted[i]:<12} Formatted: {lap_times_formatted[i]:<12}")

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

    specific_lap_gdf, specific_line_gdf = create_geodataframe(specific_lap_df)

    return specific_lap_df, specific_line_gdf


def convert_points_to_linestring(gdf):
    line = LineString(gdf.geometry.tolist())
    line_gdf = gpd.GeoDataFrame(geometry=[line], crs=gdf.crs).loc[0]
    return line_gdf


def create_geodataframe(df):
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['Longitude'], df['Latitude']),
        crs="EPSG:4326"  # Explicitly setting the CRS to EPSG:4326
    )
    line_gdf = convert_points_to_linestring(gdf)
    return gdf, line_gdf


if __name__ == "__main__":

    # laps_df = merge_lap_data(name="Emil")
    # laps_df,lap_times = prepare_laps_data(name ="Emil")
    laps_df,lap_times = re_prepare_laps_data(name ="Ana")

    # Count Lap Number
    # print("lap_times['Lap Number'].value_counts(): ", lap_times["Lap Number"].value_counts().sort_values()) # count unique values in a column called "Lap Number"

    # count unique values in a column called "Lap Placement"

    # laps_df, lap_times = prepare_laps_data(use_file="assetto_corsa_telemetry_F1_Emil_test2_30Laps.csv")
    # print("laps_df.head(): ", laps_df.head())
    # print("")
    # print("lap_times.head(): ", lap_times.head())

    print("")
    specific_lap_df, specific_line_gdf = get_specific_lap(laps_df, lap_number=5)
    print("lap_test.head(): ", specific_lap_df.head())
    print("")
    # print("specific_line_gdf: ", specific_line_gdf)
    key_points_df = extract_key_points(specific_lap_df)
    print("key_points_df")


