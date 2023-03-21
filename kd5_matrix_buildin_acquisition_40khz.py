# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 10:43:32 2022
@author: xs16051
"""

__author__ = "Xiaoyu Sun, University of Bristol (UoB)"
__copyright__ = "UoB, August 2022"
__version__ = "FMC_Acquisition_XS1.0"

# stdlib imports
# import sys

# 3rd party imports
import matplotlib.pyplot as plt
import numpy as np
import time
from scipy.signal import butter, lfilter
# from scipy.signal import chirp

# ----- Functions -----
from ultrasonic_matrix import matrix_controller

def butter_bandpass(lowcut, highcut, fs, order):
    return butter(order, [lowcut, highcut], fs = fs, btype = 'band')

def butter_bandpass_filter(data, lowcut, highcut, fs, order):
    b, a = butter_bandpass(lowcut, highcut, fs, order = order)
    filtered_signal = lfilter(b, a, data)
    return filtered_signal

# Create and configure an Ultrasonic Matrix object
# The AD2 is configured to have a 8k analogue input buffer.
# At 100MHz sample rate, the comms link is quickly saturated
# so the buffer size is the effective limit on acquisition time
# at 100MHz, it is 80us

# ----- Script -----

pulse_shape = "sine"
pulse_cycle = 5
pulse_volt = 10
centre_freq = 40e3
sample_freq = 1e6

ch_tx = 1
ch_rx = 2
ch_num = 2

ratio_buffer_length = (80*1e-6) * (100*1e6) # 100MHz - 80us
acq_time = ratio_buffer_length / sample_freq
max_time_pts = np.int(np.floor(ratio_buffer_length))
time_axis = np.arange(max_time_pts) / sample_freq

usm = matrix_controller.usm(
    tx_channel = ch_tx, # No meaning if 'usm.set_multiplexer_channel' used later
    rx_channel = ch_rx, # No meaning if 'usm.set_multiplexer_channel' used later
    drive_frequency = centre_freq,
    drive_shape = pulse_shape,
    abs_drive_v = pulse_volt,
    num_drive_cycles = pulse_cycle,
    sample_rate = sample_freq,
    max_meas_voltage_vpp = 5,
    trigger_v = 0.5,
    trigger_time_s = 0,
    acq_time_ms = acq_time * 1e3)

# ----- Matrix Acquisition: One Transmitter - All receiver -----
results_combo = []
        
for tx_channel in range(1, (ch_num + 1)):
    for rx_channel in range(1, (ch_num + 1)):
        if rx_channel != tx_channel:
            usm.set_multiplexer_channel(tx_channel = tx_channel, rx_channel = rx_channel)
            time.sleep(0.01) # May only be required if no ultrasound transducer on channel
            results_combo.append(usm.acquire_measurement())
            
# ----- !!! Close the Deivce before Data Processing !!! -----
usm.close()

# ----- Format the received signal -----
time_data = np.zeros((len(results_combo), max_time_pts), dtype = float)

for ii in range(0, (len(results_combo) - 1)):
    time_data[ii][:] = np.fromiter(results_combo[ii][2:], dtype = float)
    
# ----- Add Bandpass Filter -----
lowcut = 30e3
highcut = 50e3
order = 3

data_fltr = np.zeros((len(results_combo), max_time_pts), dtype = float)

for ii in range(0, (len(results_combo) - 1)):
    data_fltr[ii][:] = butter_bandpass_filter(time_data[ii][:], lowcut, highcut, sample_freq, order)

# ----- Multiple Line Plot -----
plt.figure()
# for ii in range(0, ((ch_num-1)**2-1)):
# plt.plot(time_axis * 1e6, time_data[0][:], color = 'black', label = ['Received Rx- %i' %100])
plt.plot(time_axis * 1e6, data_fltr[0][:], color = 'blue', label = ['Filtered Rx- %i' %100])
plt.legend(loc = "lower right")
plt.xlabel('Time ($\mu$s)')
plt.ylabel('Amplitude (V)')

# ----- Save Data as .txt File -----
np.savetxt('record_time_data.txt', time_data, delimiter = ',')
np.savetxt('record_data_fltr.txt', data_fltr, delimiter = ',')
np.savetxt('record_time.txt', time_axis, delimiter = ',')

# =============================================================================
# tx_channel = 8
# 
# for rx_channel in range(1, (ch_num+1)):
#     if rx_channel != tx_channel:
#         usm.set_multiplexer_channel(tx_channel = tx_channel, rx_channel = rx_channel)
#         time.sleep(0.01) # May only be required if no ultrasound transducer on channel
#         results_combo.append(usm.acquire_measurement())
# =============================================================================
