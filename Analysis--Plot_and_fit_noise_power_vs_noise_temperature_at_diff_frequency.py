import numpy as np
import os
import Labber
import re
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from scipy.stats import linregress

folder_path = "C:\\Users\\HQD--CPLee\\Downloads\\248p4mT\\248p4mT\\"

key_word = "uW" # This keyword indicates the unit used in the file names
rescale_factor = 0.001 # 'rescale_factor' is used to adjust the magnitude of the independent variable. For example, a factor of 0.001 will convert a value of 1000 to 1.

# Get the list of files
file_list = os.listdir(folder_path)

# Frequency list
spa_freq_start_1 = 6.8464
spa_freq_end_1 = 6.8764
spa_freq_step_1 = 0.001
 
spa_freq_start_2 = 6.8164
spa_freq_end_2 = 6.9114
spa_freq_step_2 = 0.005

spa_freq_list_1 = np.round(np.arange(spa_freq_start_1,
                      spa_freq_end_1,
                      spa_freq_step_1),9)
 
spa_freq_list_2 = np.round(np.arange(spa_freq_start_2,
                      spa_freq_end_2,
                      spa_freq_step_2),9)
 
spa_freq_list = np.concatenate((spa_freq_list_1, spa_freq_list_2), axis=0)
freq_list = np.unique(spa_freq_list)

# Temperature list
temp_list=np.array([175,946,1769,2966,3432,3994,4950]) * rescale_factor


root = tk.Tk()
root.withdraw()  # Hide the main window

exp_name = filedialog.asksaveasfilename(
    filetypes=[('HDF5 files', '*.hdf5')],
    title='Choose the storage location for the hdf5 file'
)
lStep = [dict(name="Noise temperature", unit="K", values=temp_list),
         dict(name="Frequency", unit="Hz", values=freq_list)]
lLog = [dict(name='Power (dBm) at SPA', unit='dBm', vector=False,),
        dict(name='Power (W) at SPA', unit='W', vector=False,)]
g = Labber.createLogFile_ForData(exp_name, lLog, lStep)

folder_path_txt = filedialog.askdirectory(title='Choose the storage location for the txt file')
folder_path_fitting_pic = filedialog.askdirectory(title='Choose the storage location for the fitting result')

noise_temperature = list()

for i in range(len(freq_list)):

    data_list = np.zeros((7,4))
    j = 0
    for file_name in file_list:

        # Build the complete file path
        file_path = os.path.join(folder_path, file_name)

        # Read the Labber LogFile
        f = Labber.LogFile(file_path)

        # Extract the independent variable from the file name
        pattern = re.compile(r"(\d+)"+ key_word)
        match = pattern.search(file_name)
        if match:
            indep_var = int(match.group(1))

        amp_dBm = f.getData('Power (dBm) at SPA')
        amp_W = f.getData('Power (W) at SPA')
        data_list[j,0] = indep_var
        data_list[j,2] = amp_dBm[0][i]
        data_list[j,3] = amp_W[0][i]
        
        j = j+1

    sorted_indices = np.argsort(data_list[:, 0])
    sorted_data_list = data_list[sorted_indices]
    sorted_data_list[:,1] = temp_list
    data = {'Power (dBm) at SPA': sorted_data_list[:,2],
            'Power (W) at SPA': sorted_data_list[:,3]}
    g.addEntry(data)



    np.savetxt(os.path.join(folder_path_txt, str(freq_list[i])+".txt"), sorted_data_list)


    slope, intercept, r_value, p_value, std_err = linregress(sorted_data_list[:,1], sorted_data_list[:,3])

    plt.scatter(sorted_data_list[:,1], sorted_data_list[:,3], label='Original data')

    temperature_fit = np.arange(-intercept/slope-1,5,0.1)
    plt.plot(temperature_fit, slope * temperature_fit + intercept, color='red', label='Linear fit')
    plt.axhline(y=0, color='black', linestyle='--', label='Zero line')

    plt.title('Linear Fit of Temperature and Power')
    plt.xlabel('Temperature (°C)')
    plt.ylabel('Power (W)')

    plt.text(0.9, 0.1, f'Slope: {slope:.2e}\nIntercept: {intercept:.2e}\nR-squared: {r_value**2:.2e}', 
         transform=plt.gca().transAxes, fontsize=10, verticalalignment='bottom', horizontalalignment='right')

    plt.legend()

    plt.savefig(os.path.join(folder_path_fitting_pic, str(freq_list[i])+".png"))
    plt.close()

    noise_temperature.append(intercept/slope)


plt.plot(freq_list, noise_temperature, color='blue', linestyle='-', linewidth=0.5)
plt.xlabel('Frequency [GHz]')
plt.ylabel('Noise temperature')
plt.savefig(os.path.join(folder_path_fitting_pic, "noise_temperature.png"))