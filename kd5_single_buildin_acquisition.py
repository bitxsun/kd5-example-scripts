# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 10:43:32 2022
@author: xs16051
"""

__author__ = "Xiaoyu Sun, University of Bristol (UoB)"
__copyright__ = "UoB, August 2022"
__version__ = "FMC_Acquisition_XS1.0"

import os
os.system('cls')

# 3rd party imports
import time
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from scipy.signal import butter
from fn_create_hanning_burst import *  # Upload Functions
# from scipy.signal import freqz
# from scipy.signal import chirp

# local imports
from ultrasonic_matrix import matrix_controller

# ----- Butterworth Filter Function -----
def butter_bandpass(lowcut, highcut, fs, order):
    return butter(order, [lowcut, highcut], fs=fs, btype='band')

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

# Create and configure an Ultrasonic Matrix object
# The AD2 is configured to have a 8k analogue input buffer.
# At 100MHz sample rate, the comms link is quickly saturated
# so the buffer size is the effective limit on acquisition time
# at 100MHz, it is 80us

# ----- Script -----
pulse_shape = "square" # 1. "square" 2. "sine" 3. "custom"
pulse_cycle = 5
pulse_volt = 5
centre_freq = 40e3
sample_freq = 500e3
velocity = 343;

# ----- Single Pitch-Catch Mode Measurement (SMA Channels) -----
ch_tx = 0 # To use the SMA port
ch_rx = 0 # To use the SMA port

# acq_time = ((100e6) / sample_freq) * (80e-6)
max_time_pts = 8000
acq_time = max_time_pts / sample_freq
time_axis = np.arange(max_time_pts) / sample_freq
dist_axis = time_axis * (velocity / 2)

# ----- Acquisition Time -----
measure_num = 1

# ----- Add Bandpass Filter -----
lowcut = 30e3
highcut = 50e3
order = 5

for kk in range(1, measure_num+1, 1):
    usm = matrix_controller.usm(
        tx_channel = ch_tx,
        rx_channel = ch_rx,
        drive_frequency = centre_freq,
        drive_shape = pulse_shape,
        abs_drive_v = pulse_volt,
        num_drive_cycles = pulse_cycle,
        sample_rate = sample_freq,
        max_meas_voltage_vpp = 5,
        trigger_v = 0.5,
        trigger_time_s = 0,
        acq_time_ms = acq_time * 1e3)
    
    results = usm.acquire_measurement()
    
    # ----- !!! Close the Deivce before Data Processing !!! -----
    usm.close()

    # ----- Format Array Results -----
    time_data = np.fromiter(results[2:], dtype = float)
    
    data_fltr = butter_bandpass_filter(time_data, lowcut, highcut, sample_freq, order)

    # ----- Plot Signal -----
    # plt.plot(dist_axis*1e2, time_data, color = 'black', linestyle = "-", label = 'Received Data')
    plt.plot(dist_axis*1e2, data_fltr, color = 'blue', linestyle = "-", label = 'Filtered Data')
    plt.ylim([-1, 1])
    # plt.legend()
    plt.xlabel('Distance (cm)')
    plt.ylabel('Amplitude (V)')
    plt.show()
    
    time.sleep(1)
    # ----- Print Cycle -----
    print(kk)

# =============================================================================
# data_fltr = butter_bandpass_filter(time_data, lowcut, highcut, sample_freq, order)
# 
# # ----- Plot Signal -----
# # plt.plot(dist_axis*1e2, time_data, color = 'black', linestyle = "-", label = 'Received Data')
# plt.plot(dist_axis*1e2, data_fltr, color = 'blue', linestyle = "-", label = 'Filtered Data')
# plt.ylim([-0.5, 0.5])
# plt.legend()
# plt.xlabel('Distance (cm)')
# plt.ylabel('Amplitude (V)')
# plt.show()
# =============================================================================

# ----- Save Data as .txt File -----
# =============================================================================
# np.savetxt('record_sma_time_data.txt', time_data, delimiter = ',')
# np.savetxt('record_sma_data_fltr.txt', data_fltr, delimiter = ',')
# np.savetxt('record_sma_time.txt', time_axis, delimiter = ',')
# =============================================================================

# ----- Save Data as .csv File -----
# =============================================================================
# f = open("record1.csv", "w")
# for v in results:
#     f.write("%s\n" % v)
# f.close()
# =============================================================================
