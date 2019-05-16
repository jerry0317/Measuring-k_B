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
    eps_loc = DATA_NAME + "_plt_" + str(int(time.time())) + '.eps'
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

kb_avg_arr = []

distance_d = 0

h = ["Time", "Exp Distance", "Measured Time Diff", "Temperature", "Derived k_B", "Derived k_B Error"]

try:
    csvFile = open(csv_loc, "r")
    dict_reader = csv.DictReader(csvFile)

    for row in dict_reader:
        time_arr.append(float(row[h[0]]))
        distance_d = float(row[h[1]])
        tt_arr.append(float(row[h[2]]))
        temp_arr.append(float(row[h[3]]))
        derived_kb_arr.append(float(row[h[4]]))
        kb_err_abs_arr.append(float(row[h[5]]))

    print("The data set has been successfully loaded from CSV file.")
except Exception as e:
    print(e)

for i in range(0, len(derived_kb_arr)):
    kb_avg_arr.append(np.mean(derived_kb_arr[0:i+1]))

fig = plt.figure()

ax1 = fig.add_subplot(211)

ax2 = fig.add_subplot(212)

line, (bottoms, tops), verts = ax1.errorbar([0], [0], yerr=0.01, capsize=0.1, fmt='ko', markersize=4, elinewidth=1,label="Realtime Measurement").lines

st_lines = [ax1.plot([], [], linestyle='dashed', label="Mean Measured Value")[0], ax1.plot([], [], linestyle='dashed', label=r"True $k_B$")[0], ax1.plot([], [], '.', label="Instantaneous Average Value", markersize=8)[0], ax2.plot([], [], '.', label="Temperature")[0]]

ax1.set_xlabel("Time (s)")
ax1.set_ylabel(r"Derived $k_B$ ($10^{-23} J K^{-1}$)")
ax1.legend(loc="lower right")

ax2.set_xlabel("Time (s)")
ax2.set_ylabel(r"Temperature $T$ (K)")
ax2.legend(loc="lower right")

err_gp = err_arr_gp(time_arr, derived_kb_arr, kb_err_abs_arr)
line.set_xdata(time_arr)
line.set_ydata(derived_kb_arr)
bottoms.set_xdata(time_arr)
tops.set_xdata(time_arr)
bottoms.set_ydata(err_gp[0])
tops.set_ydata(err_gp[1])
verts[0].set_segments(err_gp[2])

kb_d_avg = np.mean(derived_kb_arr)

x_list = list(itertools.repeat([np.min(time_arr), np.max(time_arr)], 2))
y_list = [[kb_d_avg , kb_d_avg], [K_B, K_B]]

x_list.append(time_arr)
y_list.append(kb_avg_arr)

x_list.append(time_arr)
y_list.append(temp_arr)

for lnum, st_line in enumerate(st_lines):
    st_line.set_data(x_list[lnum], y_list[lnum])

fig.gca().relim()
fig.gca().autoscale_view()

ax1.relim()
ax1.autoscale_view()

ax2.relim()
ax2.autoscale_view()
ax2.set_ylim([np.min(temp_arr) - 0.1,np.max(temp_arr) + 0.1])

try:
    fig_now = plt.gcf()
    plt.show()
except (KeyboardInterrupt, SystemExit):
    save_plot(fig_now)
    exit()
except Exception as e:
    print(e)

save_plot(fig_now)
