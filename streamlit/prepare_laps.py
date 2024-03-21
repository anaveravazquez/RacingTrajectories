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


def prepare_laps_data(name : str):

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
    lap_times["Lap Time"] = lap_times["Lap Time"].apply(lambda x: str(math.floor(x / 60)) + ":" + str(round(x % 60, 3)))

    return laps_df, lap_times


def get_specific_lap(laps_df, lap_number=None, lap_placement=None):
    if lap_number:
        return laps_df[laps_df["Laps Completed"] == lap_number]
    elif lap_placement:
        return laps_df[laps_df["Lap Placement"] == lap_placement]
    else: 
        raise ValueError("Please provide either lap_number or lap_placement")




if __name__ == "__main__":

    # laps_df = merge_lap_data(name="Emil")
    laps_df,lap_times = prepare_laps_data(name ="Emil")


    # count unique values in a column called "Lap Placement"

    # laps_df, lap_times = prepare_laps_data(use_file="assetto_corsa_telemetry_F1_Emil_test2_30Laps.csv")
    print("laps_df.head(): ", laps_df.head())
    # print("")
    print("lap_times.head(): ", lap_times.head())

    # print("")
    # lap_test = get_specific_lap(laps_df, lap_number=5)
    # print("lap_test.head(): ", lap_test.head())
    # print("")
    # lap_test = get_specific_lap(laps_df, lap_placement=1)
    # print("lap_test.head(): ", lap_test.head())
    # print("")

