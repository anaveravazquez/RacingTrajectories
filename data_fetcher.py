
import csv
import time
import sys
import math
sys.path.append('C://Program Files (x86)//Steam//steamapps//common//assettocorsa//apps//python//ac_dashboard')
from sim_info import info

def record_telemetry():
    """
    This script only works on my computer because it uses a python script which extracts Assetto Corsa lua files to fetch telemetry data.
    Telemetry is fetched using this integration: https://github.com/ev-agelos/ac_dashboard/tree/master

    """
    with open('Data/assetto_corsa_telemetry_F1_test_1.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Laps Completed', 'Speed (Km/h)', 'Acceleration (g)', 'X-Coords', 'Y-Coords', 'Z-Coords', 
                        'X-Acceleration (g)', 'Y-Acceleration (g)', 'Penalty Time', 'Gas', 'Brake', 'Gear', 'RPM', 'Steer Angle', 
                        'Heading','Tire Dirty Level', 'Tire Core Temp'])
        iteration = 0

        while True:  
            iteration += 1
            
            timestamp = info.graphics.iCurrentTime  # Current timestamp
            speed = info.physics.speedKmh
            acceleration = math.sqrt(info.physics.accG[0]**2 + info.physics.accG[1]**2) 
            acceleration_x = info.physics.accG[0]  
            acceleration_y = info.physics.accG[1]  
            laps_completed = info.graphics.completedLaps
            penaltyTime = info.graphics.penaltyTime
            world_pos_x = info.graphics.carCoordinates[0]
            world_pos_y = info.graphics.carCoordinates[1]
            world_pos_z = info.graphics.carCoordinates[2]
            gas = info.physics.gas
            brake = info.physics.brake
            gear = info.physics.gear
            rpm = info.physics.rpms
            steer_angle = info.physics.steerAngle
            heading = info.physics.heading
            one_tire_dirty_level = info.physics.tyreDirtyLevel[0]
            one_tire_core_temp = info.physics.tyreCoreTemperature[0]
            pit_status = info.graphics.isInPit

            # Write a row of data
            writer.writerow([timestamp, laps_completed, speed, acceleration, world_pos_x, world_pos_y, world_pos_z, 
                            acceleration_x, acceleration_y, penaltyTime, gas, brake, gear, rpm, steer_angle, 
                            heading, one_tire_dirty_level, one_tire_core_temp, pit_status])
            
            time.sleep(0.01)

            if iteration%100 == 0:
                print(f"Iteration:    {iteration}    Time:{timestamp}    Laps: {laps_completed}    Speed (Km/h): {speed:.2f}    Acceleration: {acceleration:.2f}    X-Coords:{world_pos_x:.2f}    Y-Coords:{world_pos_y:.2f}    penaltyTime:{penaltyTime:.2f}")
       

if __name__ == '__main__':
    record_telemetry()

    #while True:
        
        #time.sleep(0.5)


