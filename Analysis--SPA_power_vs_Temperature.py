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
folder_path = "D:\\NAS\\temporary Storage Zone\\OIST\\Data\\Noise_temperature_measurement\\2024\\03\\Data_0301\\"
save_data = True  # Set to True to save data in HDF5 format; set to False to plot data using pyplot

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
    
    # Extract the temperature from the file name
    pattern = re.compile(r"(\d+)mK")
    match = pattern.search(file_name)
    if match:
        temperature = int(match.group(1))
    
    # Get the frequency and amplitude data
    freq = f.getEntry(0)['SPA frequency']
    amp_dBm = f.getData('SPA data')

    # Calculate the average amplitude
    amp_Vrms = np.sqrt((50/1000) * (10**(amp_dBm/10)))
    error_Vrms = np.std(amp_Vrms) 
    avg_amp_Vrms = np.average(amp_Vrms)
    avg_amp_dBm = 10 * np.log10(1000*(avg_amp_Vrms**2)/50)
    
    # Add the extracted data as a tuple (temperature, average amplitude in dBm and Vrms, and error in Vrms) to data_list
    data_list.append((temperature, avg_amp_dBm, avg_amp_Vrms, error_Vrms))


# Sort data_list by temperature (the first element of the tuple)
sorted_data_list = sorted(data_list, key=lambda x: x[0])
temp_list = np.array(sorted_data_list)[:,0]/1000
avg_amp_dBm_list = np.array(sorted_data_list)[:,1]
avg_amp_Vrms_list = np.array(sorted_data_list)[:,2]
error_Vrms_list = np.array(sorted_data_list)[:,3]

if save_data == True:
    # save data in HDF5 format
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    exp_name = filedialog.asksaveasfilename(
        filetypes=[('HDF5 files', '*.hdf5')],
        title='Choose the storage location for the hdf5 file'
    )

    lStep = [dict(name='Noise temperature', unit='K', values=temp_list)]
    lLog = [dict(name='Power at SPA', unit='dBm', vector=False,),
            dict(name='Voltage at SPA', unit='V', vector=False,),
            dict(name='error', unit='V', vector=False,),]
    
    f = Labber.createLogFile_ForData(exp_name, lLog, lStep)

    data = {'Power at SPA': avg_amp_dBm_list,
            'Voltage at SPA': avg_amp_Vrms_list,
            'error': error_Vrms_list}
    f.addEntry(data)
else:
    # plot data using pyplot
    plt.figure(figsize=(8, 6))
    plt.scatter(np.array(sorted_data_list)[:,0]/1000, np.array(sorted_data_list)[:,1], label='6.821 GHz', color='blue')
    plt.xlabel('Noise temperature [mK]')
    plt.ylabel('Power at SPA [dBm]')
    plt.title('Power at SPA versus noise temperature')
    plt.legend()
    plt.grid(True)
    plt.show()
