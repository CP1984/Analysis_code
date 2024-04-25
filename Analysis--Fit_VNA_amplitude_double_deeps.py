import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from inspect import signature
import Labber
import os

##############################
#    Analysis parameters     #

folder_path = "C:\\Users\\HQD--CPLee\\Desktop\\Fit_double_peak_backGround\\hdf5\\"
file_name = "0012-BackGroundCheck_241p57mT_maser_off.hdf5"
pic_folder_path = "C:\\Users\\HQD--CPLee\\Desktop\\Fit_double_peak_backGround\\pic\\"
pic_file_name = "241p57mT"
background_folder_path = "C:\\Users\\HQD--CPLee\\Desktop\\Fit_double_peak_backGround\\background\\"
background_file_name = "background.txt"

Lozentz_deeps_lower_bound = 6.837
Lozentz_deeps_upper_bound = 6.888
Lower_deep_shift = -0.006
Upper_deep_shift = 0.006
Lower_deep_width = 0.001
Upper_deep_width = 0.001

#    Analysis parameters     #
##############################

# Define a Fourier series function with 8 terms
def fourier_series8(f, a0, w, a1, b1, a2, b2, a3, b3, a4, b4, a5, b5, a6, b6, a7, b7, a8, b8):
    return a0 + a1*np.sin(1*w*f) + b1*np.cos(1*w*f) + a2*np.sin(2*w*f) + b2*np.cos(2*w*f) \
            + a3*np.sin(3*w*f) + b3*np.cos(3*w*f) + a4*np.sin(4*w*f) + b4*np.cos(4*w*f) \
            + a5*np.sin(5*w*f) + b5*np.cos(5*w*f) + a6*np.sin(6*w*f) + b6*np.cos(6*w*f) \
            + a7*np.sin(7*w*f) + b7*np.cos(7*w*f) + a8*np.sin(8*w*f) + b8*np.cos(8*w*f)

# Define a function to perform masked curve fitting
def masked_curve_fit(x1, x2, func, x, y, p_guess, bandpass=False):
    y_masked = y.copy()
    if bandpass:
        y_masked[(x<x1) + (x>x2)] = np.nan #Set values between x1 and x2 to nan
    else:
        y_masked[(x>x1) * (x<x2)] = np.nan #Set values between x1 and x2 to nan
    return curve_fit(func, x, y_masked, p0=p_guess, nan_policy='omit')

# Define a double Lorentzian function with offset
def double_lorentz_offset(f, Pmax1, Pmax2, f01, f02, W1, W2, a01, a02):
    lorentz1 = Pmax1 * W1**2 / ((f - f01)**2 + W1**2) + a01
    lorentz2 = Pmax2 * W2**2 / ((f - f02)**2 + W2**2) + a02
    return lorentz1 + lorentz2

# Define a double Lorentzian function
def double_lorentz(f, Pmax1, Pmax2, f01, f02, W1, W2):
    lorentz1 = Pmax1 * W1**2 / ((f - f01)**2 + W1**2)
    lorentz2 = Pmax2 * W2**2 / ((f - f02)**2 + W2**2)
    return lorentz1 + lorentz2

# Construct the file path and load Labber data file
file_path = os.path.join(folder_path, file_name)
f = Labber.LogFile(file_path)

# Get frequency and amplitude
data_freq = f.getEntry(0)['Frequency']
data_freq = data_freq/1e9
data_amp_array = f.getData('S21 Amplitude')
data_amp = data_amp_array[0,:]

# Define the background function using a Fourier series
bg_func = fourier_series8

# Fit the background function
sig = signature(bg_func)
coeffs = np.zeros(len(sig.parameters)-3)
fmean = np.mean(data_freq)
fcent = data_freq-fmean # centered about mean frequency domain
p_guess = (np.mean(data_amp), 1, *coeffs)
res = curve_fit(bg_func, fcent, data_amp, p0=p_guess) #Fit BG with centered freq domain
pfit_bg = res[0] #fitted params
fitted_bg = bg_func(fcent,*pfit_bg) #Plot over centered freq domain

# Fit the background function with masked data
res = masked_curve_fit(Lozentz_deeps_lower_bound-fmean, Lozentz_deeps_upper_bound-fmean, bg_func, fcent, data_amp, pfit_bg) #Fit BG with centered freq domain
pfit_bg2 = res[0] #fitted params
fitted_bg2 = bg_func(fcent,*pfit_bg2) #Plot over centered freq domain

# Fit the double Lorentzian function with masked data
p_guess = (np.min(data_amp), np.min(data_amp), 0+Lower_deep_shift, 0+Upper_deep_shift, Lower_deep_width, Upper_deep_width, pfit_bg2[0], pfit_bg2[0])
res = masked_curve_fit(Lozentz_deeps_lower_bound-fmean, Lozentz_deeps_upper_bound-fmean, double_lorentz_offset, fcent, data_amp, p_guess, bandpass=True) #Fit BG with centered freq domain
pfit_peak = res[0] #fitted params
fitted_peak = double_lorentz_offset(fcent,*pfit_peak) #Plot over centered freq domain

# Define the fitting function combining Lorentzian and background
# Fit the combined fitting function
p_guess = np.concatenate((pfit_peak[:-2], [(pfit_bg2[0]+pfit_peak[-1])/2], pfit_bg2[1:]))
fitting_func = lambda *args : double_lorentz(*args[:7]) + bg_func(args[0], *args[7:])
res = curve_fit(fitting_func, fcent, data_amp, p0=p_guess, maxfev = 200000) #Fit BG with centered freq domain
pfit_peak_bg = res[0] #fitted params
std = np.sqrt(np.diag(res[1])) #standard deviation
fitted_peak_bg = fitting_func(fcent,*pfit_peak_bg) #Plot over centered freq domain
fitted_bg = bg_func(fcent, pfit_peak_bg[0], *pfit_peak_bg[7:])
fitted_peak = double_lorentz(fcent, *pfit_peak_bg[0:6])

# Plot the original data and fitting results
plt.scatter(data_freq, data_amp, s = 1, color = "grey", alpha = 0.5, label = "Original data") # plot raw data
plt.plot(data_freq, fitted_peak_bg, color = 'purple', label = "Fitting result with Lozentz deeps") # plot fitting result with two Lozentz deeps
plt.plot(data_freq, fitted_bg-(fitted_bg[0]-fitted_peak_bg[0]), color = "red", label = "Fitting result of background") # plot fitting result of back ground, without two Lozentz deeps
plt.legend()
plt.xlabel("Frequency (GHz)")
plt.ylabel("$S_{21}$ (dB)")
plt.savefig(os.path.join(pic_folder_path, pic_file_name))
plt.show()

print(data_freq,fitted_bg-(fitted_bg[0]-fitted_peak_bg[0]))

data = np.column_stack((data_freq*1e9, fitted_bg-(fitted_bg[0]-fitted_peak_bg[0])))

output_file_path = os.path.join(background_folder_path, background_file_name)

np.savetxt(output_file_path, data, delimiter=',', fmt='%.8e')
