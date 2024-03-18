import pandas as pd
import numpy as np

def drop_right_track_indices(df):
    """
    Removes bad indices from the right track dataframe in order to smooth the track.
    """
    # indeces_to_drop = [] #TBD.
    # for x in indeces_to_drop:
    #     df.drop(df.index[x], inplace=True)

    return df

def drop_left_track_indices(df):
    """
    Removes bad indices from the left track dataframe in order to smooth the track.
    """
    # indeces_to_drop = [] # TBD.
    # for x in indeces_to_drop:
    #     df.drop(df.index[x], inplace=True)

    return df


def load_track_data(distance_pr_dot:float = 0.1):
    track_left_side = pd.read_csv(f'Data/Map_details/nurburgring_GP_track_leftside_raw.csv', index_col=False)
    track_right_side = pd.read_csv(f'Data/Map_details/nurburgring_GP_track_rightside_raw.csv', index_col=False)

    track_left_side = track_left_side[["Timestamp","X-Coords", "Y-Coords", "Z-Coords"]]
    track_right_side = track_right_side[["Timestamp","X-Coords", "Y-Coords", "Z-Coords"]]

    track_left_side = drop_left_track_indices(track_left_side)
    track_right_side = drop_right_track_indices(track_right_side)

    track_left_side.reset_index(inplace=True)
    track_right_side.reset_index(inplace=True)

    track_left_side["Z-Coords"]   = track_left_side["Z-Coords"] * -1
    track_right_side["Z-Coords"]  = track_right_side["Z-Coords"] * -1
    track_left_side["X-Coords"]   = track_left_side["X-Coords"] * -1
    track_right_side["X-Coords"]  = track_right_side["X-Coords"] * -1
    track_left_side["Timestamp"]  = track_left_side["Timestamp"] / 1000
    track_right_side["Timestamp"] = track_right_side["Timestamp"] / 1000

    # Rename columns
    track_left_side.rename(columns={"X-Coords": "Y-Coords", 
                                    "Z-Coords": "X-Coords", 
                                    "Y-Coords": "Z-Coords"}, inplace=True)

    track_right_side.rename(columns={"X-Coords": "Y-Coords", 
                                     "Z-Coords": "X-Coords", 
                                     "Y-Coords": "Z-Coords"}, inplace=True)

    
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
        track_left_side  = reduce_dataframe(track_left_side,  distance_pr_dot)
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
    telemetry_df["LapTime"]   = -telemetry_df["Timestamp"].diff()
    telemetry_df["Z-Coords"]  = telemetry_df["Z-Coords"] * -1
    telemetry_df["X-Coords"]  = telemetry_df["X-Coords"] * -1
    telemetry_df["NewLap"] = telemetry_df["LapTime"] > 60
    if remove_first_lap:
        telemetry_df = telemetry_df[telemetry_df["Laps Completed"] > 0]

    # Rename columns
    telemetry_df.rename(columns={"X-Coords": "Y-Coords", 
                                 "Z-Coords": "X-Coords", 
                                 "Y-Coords": "Z-Coords"}, inplace=True)


    telemetry_df = telemetry_df.sort_values(by=["Laps Completed", "Timestamp"])
    telemetry_df.reset_index(drop=True, inplace=True)

    return telemetry_df


def transform_coordinates(original_df, rotation_angle = 45.1, 
                                        scale_x = 0.00001406, 
                                        scale_y = 0.000009005, 
                                        shift_x = 6.940315, 
                                        shift_y = 50.330715, 
                                        center_x = 0, 
                                        center_y = 0):
    """
    Transforms coordinates by rotating, scaling, and shifting.
    # THIS DOES NOT ACCOUNT FOR THE ALTITUDE YET !!!!!

    Args:
    original_df: a pandas dataframe with columns 'X-Coords' and 'Y-Coords'.
    rotation_angle: rotation angle in degrees.
    scale_x, scale_y: scaling factors for the x and y axes.
    shift_x, shift_y: shifting values for the x and y axes.
    center_x, center_y: the center point around which rotation is performed.

    Default values:
    
    rotation_angle = 44.8 # More is left, less is to the right
    scale_x = 0.00001397
    scale_y = 0.000009045
    shift_x = 6.940328
    shift_y = 50.3307159
    center_x = 0
    center_y = 0

    rotation_angle = 45.3 # More is left, less is to the right
    scale_x = 0.00001414
    scale_y = 0.000008989
    shift_x = 6.940317
    shift_y = 50.33072324
    center_x = 0
    center_y = 0

    ### THIS  appears to be the best transformation ####
    rotation_angle = 45.15 # More is left, less is to the right
    scale_x = 0.00001406
    scale_y = 0.000009005
    shift_x = 6.940315
    shift_y = 50.330715
    center_x = 0
    center_y = 0





    Returns:
    Transformed x and y coordinates as numpy arrays.
    """
    x = np.array(original_df['X-Coords'])
    y = np.array(original_df['Y-Coords'])

    angle_rad = np.radians(rotation_angle)
    rotation_matrix = np.array([[np.cos(angle_rad), -np.sin(angle_rad)],
                                [np.sin(angle_rad), np.cos(angle_rad)]])
    x_shifted, y_shifted = x - center_x, y - center_y
    original_points = np.vstack((x_shifted, y_shifted))

    rotated_points = np.dot(rotation_matrix, original_points)
    scaled_points = np.vstack((rotated_points[0] * scale_x, rotated_points[1] * scale_y))
    transformed_points = scaled_points + np.vstack((shift_x + center_x, shift_y + center_y))

    new_df = original_df.copy()
    new_df['X-Coords'] = transformed_points[0, :]
    new_df['Y-Coords'] = transformed_points[1, :]

    return new_df





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