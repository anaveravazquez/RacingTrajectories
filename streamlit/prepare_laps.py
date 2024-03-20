import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import math
import sys

sys.path.append("../")
from data_loader import transform_coordinates, load_track_data, load_race_data



def prepare_laps_data(use_file):
    laps_df = load_race_data(file = use_file, remove_first_lap= True)

    laps_df = transform_coordinates(laps_df)

    lap_times = laps_df[laps_df["NewLap"] == True]
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
    laps_df, lap_times = prepare_laps_data(use_file="assetto_corsa_telemetry_F1_Emil_test2_30Laps.csv")
    print("laps_df.head(): ", laps_df.head())
    print("")
    print("lap_times.head(): ", lap_times.head())

    print("")
    lap_test = get_specific_lap(laps_df, lap_number=5)
    print("lap_test.head(): ", lap_test.head())
    print("")
    lap_test = get_specific_lap(laps_df, lap_placement=1)
    print("lap_test.head(): ", lap_test.head())
    print("")

