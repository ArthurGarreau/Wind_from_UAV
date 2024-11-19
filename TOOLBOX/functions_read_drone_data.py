# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 16:59:49 2024

@author: arthurg
"""
import pandas as pd
import glob

#%% read file: 
## TODO read multiple files in a folder or multiple drones

def read_mavic2(file_pattern):
    """
    

    Parameters
    ----------
    file_pattern : STR
        filepath + filename of the flight log(s).

    Returns
    -------
    A pandas dataframe called "data".

    """

    # Use glob to find all files matching the pattern
    file_list = glob.glob(file_pattern)

    # List to store each individual file's data
    df_list = []
    
    # Loop through each file and process it
    for flight_log in file_list:
        # Read each file
        data_raw = pd.read_csv(flight_log)
        
        # Parse datetime and set as index
        data_raw['CUSTOM.updateTime'] = pd.to_datetime(data_raw['CUSTOM.updateTime'], errors='coerce')
        data_raw.set_index('CUSTOM.updateTime', inplace=True)
        
        # Extract and rename relevant columns
        data = data_raw[[
            "OSD.latitude", "OSD.longitude", "OSD.height [m]",
            "OSD.pitch", "OSD.roll", "OSD.yaw",
            "CUSTOM.hSpeed [m/s]", "CUSTOM.distance [m]", "CUSTOM.travelled [m]"
        ]]
        
        data.rename(columns={
            'OSD.latitude': 'GPS_Lat',
            'OSD.longitude': 'GPS_Lon',
            'OSD.height [m]': 'GPS_Height',
            'OSD.pitch': 'pitch',
            'OSD.roll': 'roll',
            'OSD.yaw': 'yaw',
            'CUSTOM.hSpeed [m/s]': 'hSpeed',
            'CUSTOM.distance [m]': 'distance',
            'CUSTOM.travelled [m]': 'travelled'
        }, inplace=True)
        
        # Append the processed data to the list
        df_list.append(data)

    # Concatenate all data into a single DataFrame
    combined_data = pd.concat(df_list, ignore_index=False)  # Keep original datetime index

    return combined_data