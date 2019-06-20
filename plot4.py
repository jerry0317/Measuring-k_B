#!/usr/bin/env python3

# plot.py - a simple file for plotting existing data
#
# Created by Jerry Yan


import csv
import util
import numpy as np
import matplotlib.pyplot as plt
import itertools
import time
from scipy import stats

def err_arr_gp(x_arr, data_arr, err_arr):
    if len(data_arr) != len(err_arr):
        return False
    else:
        up_arr = []
        low_arr = []
        seg_arr = []
        for i in range(0, len(data_arr)):
            x_p = x_arr[i]
            data_p = data_arr[i]
            err_p = err_arr[i]
            up_p = data_p + err_p
            low_p = data_p - err_p
            up_arr.append(up_p)
            low_arr.append(low_p)
            seg_arr.append([[x_p, low_p], [x_p, up_p]])

        return (low_arr, up_arr, seg_arr)

def save_plot(fig):
    eps_loc = DATA_NAME + "_plt4_" + str(int(time.time())) + '.eps'
    fig_now.savefig(eps_loc, format='eps')
    print("\nPlot saved to {}.\n".format(eps_loc))

# Boltzmann constant (10^-23)
K_B = 1.38064852

data_id = util.user_input("data number", val_float=False)
DATA_NAME = DATA_NAME = "data/{}".format(data_id)
csv_loc = DATA_NAME + ".csv"

# List storing values
tt_arr = []
time_arr = []
temp_arr = []

derived_kb_arr = []
kb_err_abs_arr = []
pres_arr = []

kb_avg_arr = []

distance_d = 0

h = ["Time", "Exp Distance", "Measured Time Diff", "Temperature", "Derived k_B", "Derived k_B Error", "Pressure", "HC-SRO4 Raw"]

try:
    csvFile = open(csv_loc, "r")
    dict_reader = csv.DictReader(csvFile)

    for row in dict_reader:
        t = float(row[h[0]])
        distance_d = float(row[h[1]])
        tt = float(row[h[2]])
        temp = float(row[h[3]])
        pres = float(row[h[6]])

        kb_d = util.kb_from_tt_rk_n2(tt, temp, distance_d, pres)

        err_pct = util.err_from_tt_pct(tt, temp, distance_d)
        err_abs = err_pct * kb_d

        tt_arr.append(tt)
        time_arr.append(t)
        temp_arr.append(temp)
        pres_arr.append(pres)

        derived_kb_arr.append(kb_d)
        kb_err_abs_arr.append(err_abs)

        kb_d_avg = np.mean(derived_kb_arr)

        kb_avg_arr.append(kb_d_avg)

    print("The data set has been successfully loaded from CSV file.")
except Exception as e:
    print(e)

fig = plt.figure()

ax1 = fig.add_subplot(221)
ax1_2 = fig.add_subplot(222)

ax2 = fig.add_subplot(223)
ax3 = fig.add_subplot(224)

line, (bottoms, tops), verts = ax1.errorbar([0], [0], yerr=0.01, capsize=0.1, fmt='ko', markersize=4, elinewidth=1,label="Realtime Measurement").lines

st_lines = [ax1.plot([], [], linestyle='dashed', label="Mean Measured Value")[0], ax1.plot([], [], linestyle='dashed', label=r"True $k_B$")[0], ax1.plot([], [], '.', label="Instantaneous Average Value", markersize=8)[0], ax2.plot([], [], '.', label="Temperature")[0], ax3.plot([], [], '.', label="Pressure")[0]]

ax1.set_ylabel(r"Derived $k_B$ ($10^{-23} J K^{-1}$)")
ax2.set_ylabel(r"Temperature $T$ (K)")
ax3.set_ylabel(r"Pressure $P$ (Pa)")

for ax in [ax1, ax2, ax3]:
    ax.set_xlabel("Time (s)")
    ax.legend(loc="lower right")
    ax.tick_params(direction="in")

err_gp = util.err_arr_gp(time_arr, derived_kb_arr, kb_err_abs_arr)
line.set_xdata(time_arr)
line.set_ydata(derived_kb_arr)
bottoms.set_xdata(time_arr)
tops.set_xdata(time_arr)
bottoms.set_ydata(err_gp[0])
tops.set_ydata(err_gp[1])
verts[0].set_segments(err_gp[2])

# Plotting Reference lines
# x_list = list(itertools.repeat([np.min(time_arr), np.max(time_arr)], 4))
# y_list = [[kb_d_avg , kb_d_avg], [K_B, K_B], [kb_d_sigma_up, kb_d_sigma_up], [kb_d_sigma_down], [kb_d_sigma_down]]

kb_d_avg = np.mean(derived_kb_arr)

x_list = list(itertools.repeat([np.min(time_arr), np.max(time_arr)], 2))
y_list = [[kb_d_avg , kb_d_avg], [K_B, K_B]]

x_list.append(time_arr)
y_list.append(kb_avg_arr)

x_list.append(time_arr)
y_list.append(temp_arr)

x_list.append(time_arr)
y_list.append(pres_arr)

for lnum, st_line in enumerate(st_lines):
    st_line.set_data(x_list[lnum], y_list[lnum])

# ax1_2.set_xlabel(r"Derived $k_B$ ($10^{-23} J K^{-1}$)")
ax1_2.set_xlabel(r"HC-SR04 Raw Signal Pulse ($10^3 s^{-1}$)")
ax1_2.set_ylabel("Number of Data Points")
#ax1_2.hist(derived_kb_arr, bins=12)
ax1_2.hist(1/np.array(tt_arr)*10**-3, color='g', bins=12)
#ax1_2.axvline(kb_avg_arr[-1], color='#1f77b4', linestyle='dashed', label='Measured Mean Value')
#ax1_2.axvline(K_B, color='#ff7f0e', linestyle='dashed', label=r'True $K_B$')
#ax1_2.legend(loc="upper right")

fig.gca().relim()
fig.gca().autoscale_view()

for ax in [ax1, ax2, ax3]:
    ax.relim()
    ax.autoscale_view()

ax2.set_ylim([np.min(temp_arr) - 0.1,np.max(temp_arr) + 0.1])
ax3.set_ylim([np.min(pres_arr) - 25,np.max(pres_arr) + 25])

try:
    fig_now = plt.gcf()
    plt.show()
except (KeyboardInterrupt, SystemExit):
    save_plot(fig_now)
    exit()
except Exception as e:
    print(e)

save_plot(fig_now)
