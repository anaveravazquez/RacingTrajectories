import pandas as pd
import numpy as np

def load_track_data(distance_pr_dot:float = 0):
    track_left_side = pd.read_csv(f'Data/Map_details/nurburgring_GP_track_leftside_raw.csv', index_col=False)
    track_right_side = pd.read_csv(f'Data/Map_details/nurburgring_GP_track_rightside_raw.csv', index_col=False)

    track_left_side = track_left_side[["Timestamp","X-Coords", "Y-Coords", "Z-Coords"]]
    track_right_side = track_right_side[["Timestamp","X-Coords", "Y-Coords", "Z-Coords"]]

    track_left_side["Z-Coords"] = track_left_side["Z-Coords"] * -1
    track_right_side["Z-Coords"] = track_right_side["Z-Coords"] * -1
    track_left_side["X-Coords"] = track_left_side["X-Coords"] * -1
    track_right_side["X-Coords"] = track_right_side["X-Coords"] * -1
    track_left_side["Timestamp"] = track_left_side["Timestamp"] / 1000
    track_right_side["Timestamp"] = track_right_side["Timestamp"] / 1000

    
    if type(distance_pr_dot) not in [float, int]:
        print("\n"*2)
        for i in range(5):
            print("Paramter: distance_pr_dot must be a positive float")
        print("\n"*2)
        raise ValueError("Paramter: distance_pr_dot must be a float")
    if distance_pr_dot < 0:
        print("\n"*2)
        for i in range(5):
            print("Paramter: distance_pr_dot must be positive")
        print("\n"*2)
        raise ValueError("Paramter: distance_pr_dot must be positive")
    if distance_pr_dot > 0:
        track_left_side = reduce_dataframe(track_left_side, distance_pr_dot)
        track_right_side = reduce_dataframe(track_right_side, distance_pr_dot)

    return track_left_side, track_right_side


def reduce_dataframe(df, distance_pr_dot):
        rows = []
        for index, row in df.iterrows():
            if index == 0:
                rows.append(row)
                continue
            previous_row = rows[-1]
            if np.sqrt((row['X-Coords'] - previous_row['X-Coords'])**2 + 
                        (row['Z-Coords'] - previous_row['Z-Coords'])**2 + 
                        (row['Y-Coords'] - previous_row['Y-Coords'])**2) >= distance_pr_dot:
                rows.append(row)

        reduced_df = pd.DataFrame(rows, columns=df.columns)
        return reduced_df


def load_race_data(file: str, remove_first_lap: bool = True):
    telemetry_df = pd.read_csv(f'Data/Telemetry_data/{file}', index_col=False)

    telemetry_df["Timestamp"] = telemetry_df["Timestamp"] / 1000
    telemetry_df["LapTime"] = -telemetry_df["Timestamp"].diff()
    telemetry_df["Z-Coords"] = telemetry_df["Z-Coords"] * -1
    telemetry_df["NewLap"] = telemetry_df["LapTime"] > 60
    if remove_first_lap:
        telemetry_df = telemetry_df[telemetry_df["Laps Completed"] > 0]

    telemetry_df = telemetry_df.sort_values(by=["Laps Completed", "Timestamp"])
    telemetry_df.reset_index(drop=True, inplace=True)

    return telemetry_df

if __name__ == "__main__":

    # Example usecase
    df_left, df_right = load_track_data()
    print("df_left.head(20)")
    print(df_left.head(20))
    print("\n")

    # Example usecase
    race_df = load_race_data(file = "assetto_corsa_telemetry_F1_Emil_test2_30Laps.csv", remove_first_lap= True)
    print("race_df.head(20)")
    print(race_df.head(20))