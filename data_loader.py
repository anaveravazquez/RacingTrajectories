import pandas as pd
import numpy as np
from scipy.interpolate import interp1d



def fix_track_indices(df, left_right = "left"):
    """
    Removes bad indices from the right track dataframe in order to smooth the track.
    """
    if left_right == "left":
        ranges_to_smooth = [(20400, 23500)]
        ranges_to_remove = [[[20400,21000],[21000,22611],[22611,23500]]]

    elif left_right == "right":
        ranges_to_smooth = [(3540, 6686), (25600, 27200)]
        ranges_to_remove = [[[3540,4368],[4368,6005],[6211,6686]], [[25811,27180]]]

    else: 
        raise ValueError("left_right must be either 'left' or 'right'")

    # You might g_indices, 'Y-coords'], fill_value="extrapolate")
    idx = 0
    for start, end in ranges_to_smooth:

        # Remove the bad indices
        for bad_range in ranges_to_remove[idx]:
            _start = bad_range[0]
            _end = bad_range[1]
            indices = np.arange(_start, _end)
            # x_interp = interp1d([_start, _end], [df['X-Coords'][_start], df['X-Coords'][_end]], kind='linear', fill_value="extrapolate")
            # y_interp = interp1d([_start, _end], [df['Y-Coords'][_start], df['Y-Coords'][_end]], kind='linear', fill_value="extrapolate")
            # df.loc[_start:_end-1, 'X-Coords'] = x_interp(indices)
            # df.loc[_start:_end-1, 'Y-Coords'] = y_interp(indices)
            # create a straight line from _start to _end and replace the values in the dataframe
            new_line = np.array([np.linspace(df['X-Coords'][_start], df['X-Coords'][_end], _end-_start), 
                                    np.linspace(df['Z-Coords'][_start], df['Z-Coords'][_end], _end-_start)]).T

            # print("Start index ", _start)
            # print("Start coords ", df['X-Coords'][_start], df['Z-Coords'][_start])
            # print("End index ", _end)
            # print("End coords ", df['X-Coords'][_end], df['Z-Coords'][_end])
            # print("")

            df.loc[_start:_end-1, 'X-Coords'] = new_line[:,0]
            df.loc[_start:_end-1, 'Z-Coords'] = new_line[:,1]

        x = 100
        tmp_df = df.copy()
            # tmp_df["X-Coords"] = tmp_df["X-Coords"].shift(-x//2)
            # tmp_df["Y-Coords"] = tmp_df["Y-Coords"].shift(-x//2)

        df.loc[end:end, 'X-Coords'] = tmp_df.loc[start:end,   'X-Coords'].rolling(window=x, min_periods=1, center=True).mean()
        df.loc[end:end, 'Y-Coords'] = tmp_df.loc[start:end  , 'Y-Coords'].rolling(window=x, min_periods=1, center=True).mean() 

        # df.loc[end:end, 'X-Coords'] = df.loc[start:end,   'X-Coords'].rolling(window=x, min_periods=1, center=True).mean()
        # df.loc[end:end, 'Y-Coords'] = df.loc[start:end  , 'Y-Coords'].rolling(window=x, min_periods=1, center=True).mean() 

        # end += 10
        # for i in range(1, x//2):
        #     df.loc[end-i:end-i, 'X-Coords'] = df.loc[end-i:end,   'X-Coords'].rolling(window=x, min_periods=1, center=True).mean()[end-i]
        #     df.loc[end-i:end-i, 'Y-Coords'] = df.loc[end-i:end  , 'Y-Coords'].rolling(window=x, min_periods=1, center=True).mean()[end-i]

        idx += 1
        # Generate new indices for interpolation from pre_start to post_end

        # print("")
        # print("left right", left_right)
        # print("length of indices", len(indices))
        # print("length of x_interp(indices)", len(x_interp(indices)))
        # print("length of y_interp(indices)", len(y_interp(indices)))
        # print("length of df.loc[start:end-1, 'X-Coords'] :", len(df.loc[start:end-1, 'X-Coords']))
        # print("")

        # Replace the coordinates in the DataFrame for the defined range

    return df



def load_track_data(distance_pr_dot:float = 0.1):
    try:
        track_left_side = pd.read_csv(f'Data/Map_details/nurburgring_GP_track_leftside_raw.csv', index_col=False)
        track_right_side = pd.read_csv(f'Data/Map_details/nurburgring_GP_track_rightside_raw.csv', index_col=False)
    except FileNotFoundError:
        track_left_side = pd.read_csv(f'../Data/Map_details/nurburgring_GP_track_leftside_raw.csv', index_col=False)
        track_right_side = pd.read_csv(f'../Data/Map_details/nurburgring_GP_track_rightside_raw.csv', index_col=False)

    track_left_side = track_left_side[["Timestamp","X-Coords", "Y-Coords", "Z-Coords", 'Speed (Km/h)']]
    track_right_side = track_right_side[["Timestamp","X-Coords", "Y-Coords", "Z-Coords", 'Speed (Km/h)']]

    track_left_side.reset_index(inplace=True, drop=True)
    track_right_side.reset_index(inplace=True, drop=True)

    # Uses 1D interpolation to fix areas which are known to be measure incorrectly, by backing up the car and realigning the track
    track_left_side = fix_track_indices(track_left_side, left_right = "left")
    track_right_side = fix_track_indices(track_right_side, left_right = "right")

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
    try:
        telemetry_df = pd.read_csv(f'Data/Telemetry_data/{file}', index_col=False)
    except FileNotFoundError:
        telemetry_df = pd.read_csv(f'../Data/Telemetry_data/{file}', index_col=False)

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
    new_df["Longitude"] = new_df["X-Coords"]
    new_df["Latitude"] = new_df["Y-Coords"]

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