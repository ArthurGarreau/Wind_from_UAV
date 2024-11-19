# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 19:57:40 2024

@author: arthurg
"""


import pandas as pd
import glob
import os
os.chdir(r'C:\Users\arthurg\OneDrive - NTNU\Workspace\Wind_from_Drones_Python')


def read_wind_data(wind_folder):
    # Find all .dat files in the folder
    wind_files = glob.glob(os.path.join(wind_folder, '*.dat'))
    wind_data = pd.DataFrame()
    
    for wind_file in wind_files:
        print(wind_file)
        # Read the wind data
        df = pd.read_csv(wind_file, skiprows=[0,2,3])  # Skip the first five rows of metadata
        # Select columns of interest
        df = df[['TIMESTAMP', 'VH1_sek', 'VR1_sek']]
        # Rename columns for clarity
        df.columns = ['timestamp', 'wind_speed', 'wind_direction']
        # Append to wind_data DataFrame
        wind_data = pd.concat([wind_data, df], ignore_index=True)
        
    # Convert timestamp to datetime
    wind_data['timestamp'] = pd.to_datetime(wind_data['timestamp'])

    return wind_data

def read_drone_data(drone_folder):
    # Find all .csv files in the folder
    drone_files = glob.glob(os.path.join(drone_folder, '*FLY*.csv'))
    drone_data = pd.DataFrame()
    
    for drone_file in drone_files:
        print(drone_file)
        # Read the drone data
        df = pd.read_csv(drone_file, low_memory=False)
        # Select columns of interest
        df = df[['GPS:dateTimeStamp', 
                  'IMU_ATTI(0):roll', 
                  'IMU_ATTI(0):pitch', 
                  'IMU_ATTI(0):yaw', 
                  'IMU_ATTI(0):accel:X', 
                  'IMU_ATTI(0):accel:Y', 
                  'IMU_ATTI(0):accel:Z', 
                  'IMU_ATTI(0):accel:Composite', 
                  'IMU_ATTI(0):gyro:X', 
                  'IMU_ATTI(0):gyro:Y', 
                  'IMU_ATTI(0):gyro:Z', 
                  'IMU_ATTI(0):gyro:Composite', 
                  'GPS(0):velN', 
                  'GPS(0):velE', 
                  'GPS(0):velD', 
                  'GPS(0):Long', 
                  'GPS(0):Lat', 
                  'IMU_ATTI(0):Longitude', 
                  'IMU_ATTI(0):Latitude', 
                  'Motor:Speed:RFront',
                  'Motor:Speed:LFront',
                  'Motor:Speed:LBack',
                  'Motor:Speed:RBack',
                  'General:relativeHeight']]
        # Rename the timestamp column
        df.rename(columns={'GPS:dateTimeStamp': 'timestamp'}, inplace=True)

        # Append to drone_data DataFrame
        drone_data = pd.concat([drone_data, df], ignore_index=True)

    # Convert timestamp to datetime
    
    drone_data['timestamp'] = pd.to_datetime(drone_data['timestamp'], errors='coerce')
    
    
    return drone_data

from TOOLBOX.functions_wind_calculations import calc_wind_speed_Palomaki, calc_windir

# %% READ the data

drone_data_folder = 'C:/Users/arthurg/OneDrive - NTNU/Workspace/Wind_from_Drones_Python/DATA/CALIBRATION_DATA_PHANTOM/'
wind_data_folder = 'C:/Users/arthurg/OneDrive - NTNU/Workspace/Wind_from_Drones_Python/DATA/ANEMOMETER_DATA/'

wind_data = read_wind_data(wind_data_folder)
drone_data = read_drone_data(drone_data_folder)


# drone_data.dropna(inplace=True)

drone_data.set_index('timestamp', inplace=True)
wind_data.set_index('timestamp', inplace=True)
# Convert wind_data timestamp to UTC
wind_data.index = wind_data.index.tz_localize('UTC')

averaged_drone_data = (drone_data.groupby([drone_data.index.floor('1S')])  # Group by each second
    .mean())  # You can also use .first(), .sum(), etc. depending on your needs


# %% Calculate the wind with the simple method

# Perform the merge on the timestamps, matching to the nearest timestamp
merged_data = pd.merge_asof(
    averaged_drone_data,wind_data,
    left_on='timestamp',
    right_index=True,
    direction='nearest'  # You can change to 'forward' or 'backward' if needed
)

merged_data = merged_data.rename(columns={
    'IMU_ATTI(0):roll': 'roll',
    'IMU_ATTI(0):pitch': 'pitch',
    'IMU_ATTI(0):yaw': 'yaw',
    'wind_speed': 'ANEMO_wind_speed',
    'wind_direction': 'ANEMO_wind_direction',
    'Wind:velocity': 'DRONE_wind_speed',
    'Wind:direction': 'DRONE_wind_direction'
})

calc_wind_speed_Palomaki(merged_data, DRONE_type='Phantom')
calc_windir(merged_data)


    
# %%

import matplotlib.pyplot as plt


# Define each date and time range
# For training
time_ranges = {
    '2020-04-27': [('15:30:10', '15:35:50')],
    '2020-05-06': [('11:49:00', '11:54:30'), ('11:58:30', '12:02:50'), ('12:09:30', '12:18:50')],
    '2020-05-13': [('11:01:30', '11:11:30')],
    '2020-05-18': [('14:09:30', '14:24:30')],
    '2020-05-22': [('13:31:10', '13:42:50'), ('13:43:10', '13:46:50')],
    '2020-06-03': [('15:50:10', '15:59:30')]
}

# For validation
# time_ranges = {
#     '2020-05-06': [('12:09:30', '12:18:50')],
#     '2020-05-13': [('11:21:10', '11:26:50')],
#     '2020-05-22': [('13:47:00', '13:52:30')],
#     '2020-06-03': [('14:37:10', '14:51:30')]
# }

# List to collect all filtered data segments for concatenation
all_filtered_data = []

# Loop through each date and time range
for date, intervals in time_ranges.items():
    for start_time, end_time in intervals:
        # Filter data for the specific date and time range
        filtered_data = merged_data.loc[f'{date} {start_time}':f'{date} {end_time}']
        
        # Append each segment to the list
        all_filtered_data.append(filtered_data)
        
        # Plot settings
        plt.figure(figsize=(14, 8))
        
        # First subplot for wind speeds
        plt.subplot(2, 1, 1)
        plt.plot(filtered_data.index, filtered_data['ANEMO_wind_speed'], label='ANEMO Wind Speed', color='blue')
        plt.plot(filtered_data.index, filtered_data['WS_Palomaki'], label='DRONE Wind Speed Calculated', color='orange')
        plt.xlabel('Timestamp')
        plt.ylabel('Wind Speed (m/s)')
        plt.title(f'Wind Speed: ANEMO vs DRONE ({date} {start_time} to {end_time})')
        plt.legend()
        plt.grid(True)
        
        # Second subplot for wind directions
        plt.subplot(2, 1, 2)
        plt.plot(filtered_data.index, filtered_data['ANEMO_wind_direction'], label='ANEMO Wind Direction', color='blue')
        plt.plot(filtered_data.index, filtered_data['WD'], label='DRONE Wind Direction Calculated', color='orange')        
        plt.xlabel('Timestamp')
        plt.ylabel('Wind Direction (°)')
        plt.title(f'Wind Direction: ANEMO vs DRONE ({date} {start_time} to {end_time})')
        plt.ylim([0,360])
        plt.legend()
        plt.grid(True)
        
        # Adjust layout and display
        plt.tight_layout()
        # plt.show()
       
        start_time_formatted = start_time.replace(':', '_')
        end_time_formatted = end_time.replace(':', '_')

        plt.savefig(drone_data_folder + f'{date} {start_time_formatted} - {end_time_formatted}.png')
        plt.close()
# Concatenate all filtered segments into a single DataFrame
concatenated_data = pd.concat(all_filtered_data)

# # Save to CSV
concatenated_data.to_csv(os.path.join(drone_data_folder,"Drone_Anemometer_data_for_training.csv"), float_format='%.3f')
# concatenated_data.to_csv(os.path.join(drone_data_folder,"Drone_Anemometer_data_for_validation.csv"), float_format='%.3f')

