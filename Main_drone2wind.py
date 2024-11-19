#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 20:13:39 2024

@author: julesb
"""

# General libraries
import os as os
import matplotlib.pyplot as plt
os.chdir(r'C:\Users\arthurg\OneDrive - NTNU\Workspace\Wind_from_Drones_Python')

# Specific libraries for the necessary functions
from TOOLBOX.functions_read_drone_data import read_mavic2
from TOOLBOX.functions_wind_calculations import calc_wind_speed_Palomaki, \
    calc_windir, add_is_profile_column, split_by_time_gap



# %% READ data 
date_str = "2024-10-04" # date of the flight record
datapath = r"C:\Users\arthurg\OneDrive - NTNU\Workspace\Wind_from_Drones_Python\DATA\Mavic2"
flight_log = os.path.join(datapath,f"DJIFlightRecord_{date_str}_*.csv")
os.path.isfile(flight_log)

data = read_mavic2(flight_log)

#%% CALCULATION of the windspeed "WS" and wind direction "WD"

calc_wind_speed_Palomaki(data)
calc_windir(data)

# %%
data_1sec = data.resample('1S').mean()
add_is_profile_column(data_1sec)



#%% PLOT the drone height

data["GPS_Height"].plot(grid=True,title="Drone height over time", xlabel="Time",ylabel="Altitude [m]")

# Prepare the different profiles 
data_plot = data_1sec[data_1sec['isProfile']]
profiles = split_by_time_gap(data_plot)


#%% PLOT the WS and WD profiles

col_ws = 'WS_Palomaki'
# i=0

for i in range(len(profiles)):
    profile = profiles[i]  # Select a profile
    # plot the windspeed and direction
    fig, axes = plt.subplots(1, 2, figsize=(9, 12))
    
    # Left plot: WS_Palomaki vs GPS_Height
    axes[0].plot(profile[col_ws], profile['GPS_Height'], label=col_ws,color='b')
    axes[0].set_xlabel('Wind speed [m/s]')
    axes[0].set_ylabel('GPS Height [m]')
    axes[0].set_title('Wind speed profile')
    axes[0].set_xlim(0,data_plot[col_ws].mean()*2)
    axes[0].set_ylim(axes[0].get_ylim()[0], axes[0].get_ylim()[1] * 1.05)
    axes[0].legend()
    axes[0].grid()
    
    # Right plot: WD vs GPS_Height
    axes[1].scatter(profile['WD'], profile['GPS_Height'], color='k', marker = '+')
    axes[1].set_xlabel('Wind direction [deg]')
    axes[1].set_ylabel('GPS Height [m]')
    axes[1].set_title('Wind direction profile')
    axes[1].set_xlim(0,360)
    axes[1].set_ylim(axes[0].get_ylim()[0], axes[0].get_ylim()[1] * 1.05)
    axes[1].grid()
    
    
    # Create filename with date and profile number
    profile_date = profile.index[0].strftime('%Y-%m-%d')
    save_folder = r'C:\Users\arthurg\OneDrive - NTNU\Workspace\Wind_from_Drones_Python\FIGURES'
    filename = f"{profile_date}_profile_{i+1}.png"
    filepath = os.path.join(save_folder, filename)
    
    # Save the plot
    plt.savefig(filepath)

    plt.close(fig)
#Save the profiles
for i, df in enumerate(profiles, start=1):
    filename = os.path.join(save_folder, f"{profile_date}_profile_{i}.csv")
    df.to_csv(filename, float_format="%.4f", decimal=",")
    