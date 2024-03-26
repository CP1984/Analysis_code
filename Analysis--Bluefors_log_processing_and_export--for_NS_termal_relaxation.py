import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import Labber

def convert_date_time_to_seconds(df, date_column=0, time_column=1):
    """
    Converts date and time columns in the DataFrame to seconds since the first timestamp.
    Args:
        df (pd.DataFrame): Input DataFrame containing date and time columns.
        date_column (int): Index of the date column (default is 0).
        time_column (int): Index of the time column (default is 1).
    Returns:
        np.ndarray: Array of time durations in seconds.
    """

    df['Datetime'] = pd.to_datetime(df.iloc[:, date_column] + ' ' + df.iloc[:, time_column])
    time_duration_seconds = (df['Datetime'] - df['Datetime'].iloc[0]).dt.total_seconds()
    time_duration_array = time_duration_seconds.to_numpy()
    
    return time_duration_array

def save_data_to_file(data, file_format, extract_subdata=False, lower_limit=None, upper_limit=None):
    """
    Saves data to a text file in either txt or hdf5 format.
    Args:
        data (np.ndarray): Data to be saved.
        file_format (str): Format of the file ('txt' or 'hdf5').
        extract_subdata (bool): If True, extracts a subset of data based on provided limits.
        lower_limit (float): Lower limit for data extraction (inclusive).
        upper_limit (float): Upper limit for data extraction (exclusive).
    """

    # Extract subdata if specified
    if extract_subdata:
        mask = (data[:, 0] > lower_limit) & (data[:, 0] < upper_limit)
        data = data[mask]
        data[:,0] = data[:,0] - data[:,0][0]

    # Save data based on file format
    if file_format == "txt":
        root = tk.Tk()
        root.withdraw()
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        np.savetxt(filename, data, delimiter='\t', fmt='%.10f')
    
    elif file_format == "hdf5":
        exp_name = filedialog.asksaveasfilename(filetypes=[('HDF5 files', '*.hdf5')])
        lStep = [dict(name="Duration", unit='s', values=data[:, 0])]
        lLog = [dict(name='MXC temperature', unit='K', vector=False),
                dict(name='Noise source temperature', unit='K', vector=False),
                dict(name='Heater power', unit='W', vector=False)]
        f = Labber.createLogFile_ForData(exp_name, lLog, lStep)
        data_dict = {'MXC temperature': data[:, 1],
                     'Noise source temperature': data[:, 2],
                     'Heater power': data[:, 3]}
        f.addEntry(data_dict)


# Load data from CSV files
df_MXC_temp = pd.read_csv('C:\\Users\\HQD--CPLee\\Desktop\\MXC_temp.log', sep=',')
df_NS_temp = pd.read_csv('C:\\Users\\HQD--CPLee\\Desktop\\NS_temp.log', sep=',')
df_NS_heater_power = pd.read_csv('C:\\Users\\HQD--CPLee\\Desktop\\NS_heater_power.log', sep=',')

# Calculate time duration array
time_duration_array = convert_date_time_to_seconds(df_MXC_temp)

# Extract relevant data arrays
MXC_temp_array = df_MXC_temp.iloc[:, 2].to_numpy()
NS_temp_array = df_NS_temp.iloc[:, 2].to_numpy()
NS_heater_power_array = df_NS_heater_power.iloc[:, 3].to_numpy()

# Combine arrays
combined_data = np.column_stack((time_duration_array, MXC_temp_array, NS_temp_array, NS_heater_power_array))

# Save combined data
save_data_to_file(combined_data, "hdf5", True, 33460, 44360)