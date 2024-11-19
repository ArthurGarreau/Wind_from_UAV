# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 17:15:52 2024

@author: arthurg
"""

import numpy as np
import pandas as pd
from TOOLBOX.functions_misc import deg2rad, rad2deg

# %% Wind calculation from the drone behaviour

def calc_tilt(data,isradian=False):
    """
    Parameters
    ----------
    data : Pandas Dataframe.
        Necessary dataframe of the drone data to retrieve the tilt angle from the parameters 
        "roll", "pitch".
    isradian : bool, optional
        Are the angles in radian? The default is False.

    Returns
    -------
    Array
        Array of tilt angle values.

    """
    
    phi,theta = data["roll"].copy(deep=True),data["pitch"].copy(deep=True)
    if not(isradian): phi, theta = deg2rad(phi),deg2rad(theta)
    
    norm_p = np.sqrt((np.cos(phi) * np.sin(theta))**2 +
                     (np.sin(phi) * np.cos(theta))**2 +
                     (np.cos(phi) * np.cos(theta))**2)
    p_dot_n = - np.cos(theta) * np.cos(phi)
    
    return np.arccos(p_dot_n / norm_p)

def calc_wind_speed_Palomaki(data, DRONE_type='Mavic'):
    """
    Parameters
    ----------
    data : Pandas datafram
        Drone data with the necessary fields for making the wind calculation from
        the drone behaviour with the variables "pitch" and "roll.

    Returns
    -------
    None. It creates a new column in the dataframe called "WS_Palomaki_0".
    This column corresponds to the wind estimation from the regression inspired by the Palomaki method.
    It also adds the tilt angle of the drone to the dataframe.

    """
    
    data["tilt"] = calc_tilt(data,isradian=False) # en radian
    
    # constants for Palomaki method
    if DRONE_type == 'Mavic':
        alpha1, alpha2, beta = 2062.6, 406.95, -24.76
        cut = 0.090
    if DRONE_type == 'Phantom':
        alpha1, alpha2, beta = 1113.2, 501.2, -36.27
        cut = 0.090
    
    data["is_over_gamma_crit"] = np.abs(np.tan(data["tilt"]) > cut)
    data["WS_Palomaki"] = np.sqrt(alpha1 * np.abs(np.tan(data["tilt"])**2)) # alpha <= tan(gamma_crit)
    #data["WS_Palomaki"][data["is_over_gamma_crit"]] = np.sqrt(alpha2 * np.abs(np.tan(data["tilt"][data["is_over_gamma_crit"]])) + beta)
    data.loc[data["is_over_gamma_crit"],"WS_Palomaki"] = np.sqrt(alpha2 * np.abs(np.tan(data.loc[data["is_over_gamma_crit"],"tilt"])) + beta) # alpha > tan(gamma_crit)
    
    data["WS_Palomaki_0"] = np.sqrt(338.72 * np.abs(np.tan(data["tilt"])))
    
    
def calc_windir(data):
    """
    

    Parameters
    ----------
    data : Pandas datafram
        Drone data with the necessary fields for making the wind calculation from
        the drone behaviour with the variables "pitch", "roll" and "yaw".

    Returns
    -------
    None. It creates a new column in the dataframe called "WD".
    This column corresponds to the wind direction. 

    """
    
    phi, theta = deg2rad(data["roll"].copy(deep=True)), deg2rad(data["pitch"].copy(deep=True))
    yaw = data["yaw"]
    
    norm_p = np.sqrt((np.cos(phi) * np.sin(theta)) ** 2 +
                     (np.sin(phi) * np.cos(theta)) ** 2)
    
    p_dot_n = - np.cos(phi) * np.sin(theta)
    
    lambada = rad2deg(np.arccos(p_dot_n / norm_p))
    
    test = np.sin(phi) * np.cos(theta)
    
    a = test < 0
    b = test >=0
    
    wdir = test * 0
    wdir[a] = (360 - lambada[a] + yaw[a]) % 360
    wdir[b] = (lambada[b] + yaw[b]) % 360
    
    data["WD"] = wdir
    

def height_speed_from_height(data):
    """
    

    Parameters
    ----------
    data : Pandas Dataframe
        Needs the column "GPS_Height".

    Returns
    -------
    None. Adds a column called "GPS_Height_Speed" corresponding to the height speed of the drone.

    """
    
    # Ensure 'GPS_Height' column exists
    if 'GPS_Height' not in data.columns:
        raise ValueError("DataFrame must contain a 'GPS_Height' column.")

    # Calculate the time difference between consecutive entries in seconds
    time_diff = data.index.to_series().diff().dt.total_seconds()

    # Calculate the altitude difference between consecutive entries
    height_diff = data['GPS_Height'].diff()

    # Calculate the vertical speed (height speed) in m/s
    data['GPS_Height_Speed'] = height_diff / time_diff
    
    
def add_is_profile_column(data):
    """
    Adds a boolean column 'isProfile' to the DataFrame. The value is True if 
    the height difference is > 0.5 meters and GPS_Height_Speed is > 0.5 m/s.
    
    Parameters
    ----------
    data : Pandas DataFrame
        Must contain columns 'GPS_Height' and 'GPS_Height_Speed'.
        
    Returns
    -------
    None. Adds a column 'isProfile' to the DataFrame with boolean values.
    """
    # Ensure required columns exist
    if 'GPS_Height' not in data.columns:
        raise ValueError("DataFrame must contain a 'GPS_Height' column.")
    
    # Compute GPS_Height_Speed if it does not already exist
    if 'GPS_Height_Speed' not in data.columns:
        height_speed_from_height(data)

    # Calculate the height difference between consecutive entries
    height_diff = data['GPS_Height'].diff()

    # Create the 'isProfile' column based on the conditions
    data['isProfile'] = (height_diff > 0.5) & (data['GPS_Height_Speed'] > 0.9)



def split_by_time_gap(data, max_gap='30S'):
    """
    Splits the input DataFrame into smaller DataFrames whenever the time gap 
    between consecutive rows exceeds max_gap.

    Parameters
    ----------
    data : pd.DataFrame
        The DataFrame with a datetime index.
    max_gap : str, optional
        The maximum allowed gap between consecutive rows (default is '30S' for 30 seconds).

    Returns
    -------
    profiles : dict
        A dictionary where keys are profile names (e.g., 'profile_1', 'profile_2', etc.) 
        and values are the corresponding DataFrame slices.
    """

    data = data.sort_index()  # Sort index if not sorted
    time_diffs = data.index.to_series().diff()  # Calculate time differences between consecutive rows
    
    # Generate a unique group id each time the time difference exceeds max_gap
    group_id = (time_diffs > pd.Timedelta(max_gap)).cumsum()
    
    # Split data into a list of DataFrames based on the group_id
    profiles = [profile for _, profile in data.groupby(group_id)]

    return profiles

