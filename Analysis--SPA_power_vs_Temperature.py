import numpy as np
import os
import Labber
import re
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog


##############################
#    Analysis parameters     #

# Define the folder path where you save the original data
folder_path = "D:\\NAS\\temporary Storage Zone\\OIST\\Data\\Noise_temperature_measurement\\2024\\03\\temp\\"
save_data = False  # Set to True to save data in HDF5 format; set to False to plot data using pyplot

key_word = "mK" # This keyword indicates the unit used in the file names
indep_var_label = "Noise temperature"
indep_var_unit = "K"
rescale_factor = 0.001 # 'rescale_factor' is used to adjust the magnitude of the independent variable. For example, a factor of 0.001 will convert a value of 1000 to 1.

#    Analysis parameters     #
##############################


# Get the list of files
file_list = os.listdir(folder_path)

# Initialize an empty list to store the extracted data
data_list = []

# Iterate over each file
for file_name in file_list:
    # Build the complete file path
    file_path = os.path.join(folder_path, file_name)
    
    # Read the Labber LogFile
    f = Labber.LogFile(file_path)
    num_data = f.getNumberOfEntries()
    
    # Extract the independent variable from the file name
    pattern = re.compile(r"(\d+)"+ key_word)
    match = pattern.search(file_name)
    if match:
        indep_var = int(match.group(1))
    
    # Get the frequency and amplitude data
    freq = f.getEntry(0)['SPA frequency']
    amp_dBm = f.getData('SPA data')

    # Calculate the average amplitude
    amp_Watt = (1/1000) * (10**(amp_dBm/10))
    error_Watt = np.std(amp_Watt) 
    avg_amp_Watt = np.average(amp_Watt)
    avg_amp_dBm = 10 * np.log10(1000*(avg_amp_Watt))
    
    # Add the extracted data as a tuple (temperature, average amplitude in dBm and Vrms, and error in Vrms) to data_list
    data_list.append((indep_var, avg_amp_dBm, avg_amp_Watt, error_Watt))


# Sort data_list by temperature (the first element of the tuple)
sorted_data_list = sorted(data_list, key=lambda x: x[0])
x_list = np.array(sorted_data_list)[:,0] * rescale_factor
avg_amp_dBm_list = np.array(sorted_data_list)[:,1]
avg_amp_Watt_list = np.array(sorted_data_list)[:,2]
error_Watt_list = np.array(sorted_data_list)[:,3]

if save_data == True:
    # save data in HDF5 format
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    exp_name = filedialog.asksaveasfilename(
        filetypes=[('HDF5 files', '*.hdf5')],
        title='Choose the storage location for the hdf5 file'
    )

    lStep = [dict(name=indep_var_label, unit=indep_var_unit, values=x_list)]
    lLog = [dict(name='Power (dBm) at SPA', unit='dBm', vector=False,),
            dict(name='Power (W) at SPA', unit='W', vector=False,),
            dict(name='error', unit='W', vector=False,),]
    
    f = Labber.createLogFile_ForData(exp_name, lLog, lStep)

    data = {'Power (dBm) at SPA': avg_amp_dBm_list,
            'Power (W) at SPA': avg_amp_Watt_list,
            'error': error_Watt_list}
    f.addEntry(data)
else:
    # plot data using pyplot
    plt.figure(figsize=(8, 6))
    plt.scatter(x_list, avg_amp_dBm_list, color='blue')
    plt.xlabel(indep_var_label + " [" + indep_var_unit+ "]")
    plt.ylabel('Power at SPA [dBm]')
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(8, 6))
    plt.errorbar(x_list, avg_amp_Watt_list, error_Watt_list, color='blue', ecolor='black', capsize=5)
    plt.xlabel(indep_var_label + " [" + indep_var_unit+ "]")
    plt.ylabel('Power at SPA [W]')
    plt.grid(True)
    plt.show()
