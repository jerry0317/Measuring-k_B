#!/usr/bin/env python3

# plot2.py - a simple file for plotting existing data
#
# Created by Jerry Yan


import csv
import util
import numpy as np
import matplotlib.pyplot as plt
import itertools
import time

def save_plot(fig):
    eps_loc = "data/plt3_" + str(int(time.time())) + '.eps'
    fig_now.savefig(eps_loc, format='eps')
    print("\nPlot saved to {}.\n".format(eps_loc))

data_id = util.user_input("data numbers (separated by comma)", val_float=False)
data_id = data_id.split(",")

data_ids = [d.strip() for d in data_id]

# List storing values
d_arr = []
kb_arr = []

for di in data_ids:

    DATA_NAME = DATA_NAME = "data/{}".format(di)
    csv_loc = DATA_NAME + ".csv"


    h = ["Time", "Exp Distance", "Measured Time Diff", "Temperature", "Derived k_B", "Derived k_B Error"]

    time_arr = []
    tt_arr = []
    distance_d = 0
    temp_arr = []
    derived_kb_arr = []

    try:
        csvFile = open(csv_loc, "r")
        dict_reader = csv.DictReader(csvFile)

        for row in dict_reader:
            time_arr.append(float(row[h[0]]))
            distance_d = float(row[h[1]])
            tt_arr.append(float(row[h[2]]))
            temp_arr.append(float(row[h[3]]))

    except Exception as e:
        print(e)

    for i in range(0, len(time_arr)):
        tt = tt_arr[i]
        temp = temp_arr[i]
        c_s = util.c_from_tt(tt, distance_d)
        kb_d = util.kb_from_tt_vdw_n2_aprx(tt, temp, distance_d)

        derived_kb_arr.append(kb_d)


    d_arr.append(distance_d)
    kb_arr.append(np.mean(derived_kb_arr))

fig = plt.figure()

ax1 = fig.add_subplot(111)

ax1.set_xlabel("Distance (m)")
ax1.set_ylabel(r"Derived $k_B$ ($10^{-23} J K^{-1}$)")

ax1.plot(d_arr, kb_arr, '.', label="Averaged data")
ax1.plot([np.min(d_arr), np.max(d_arr)],[K_B, K_B], linestyle = 'dashed', label = r"True $k_B$")

ax1.legend(loc="upper right")

try:
    fig_now = plt.gcf()
    plt.show()
except (KeyboardInterrupt, SystemExit):
    save_plot(fig_now)
    exit()
except Exception as e:
    print(e)

save_plot(fig_now)
