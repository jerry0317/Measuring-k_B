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

# Boltzmann constant (10^-23)
K_B = 1.38064852

def save_plot(fig):
    eps_loc = "data/plt3_" + str(int(time.time())) + '.eps'
    fig_now.savefig(eps_loc, format='eps')
    print("\nPlot saved to {}.\n".format(eps_loc))

def std_error(err_arr):
    n = len(err_arr)
    ste = np.sqrt(np.sum([e ** 2 for e in err_arr])/(n-1))
    return ste

data_id = util.user_input("data numbers (separated by comma)", val_float=False)
data_id = data_id.split(",")

data_ids = [d.strip() for d in data_id]

# Desired Offset (ms)
OFFSET = util.user_input("offset in ms", [-1,1])

# List storing values
d_arr = []
kb_arr = []

kb_offset_arr = []
kb_err_arr = []

for di in data_ids:

    DATA_NAME = DATA_NAME = "data/{}".format(di)
    csv_loc = DATA_NAME + ".csv"


    h = ["Time", "Exp Distance", "Measured Time Diff", "Temperature", "Derived k_B", "Derived k_B Error", "Pressure"]

    time_arr = []
    tt_arr = []
    distance_d = 0
    temp_arr = []
    pres_arr = []
    derived_kb_arr = []
    derived_kb_offset_arr = []
    kb_d_avg_arr = []

    try:
        csvFile = open(csv_loc, "r")
        dict_reader = csv.DictReader(csvFile)

        for row in dict_reader:
            time_arr.append(float(row[h[0]]))
            distance_d = float(row[h[1]])
            tt_arr.append(float(row[h[2]]))
            temp_arr.append(float(row[h[3]]))
            pres_arr.append(float(row[h[6]]))

    except Exception as e:
        print(e)

    for i in range(0, len(time_arr)):
        tt = tt_arr[i]
        pres = pres_arr[i]
        tt_offset = tt + OFFSET * 10 ** -3
        temp = temp_arr[i]
        kb_d = util.kb_from_tt_rk_air(tt, temp, distance_d, pres)
        kb_d_offset = util.kb_from_tt_rk_air(tt_offset, temp, distance_d, pres)
        err_pct = util.err_from_tt_pct(tt, temp, distance_d)
        err_abs = err_pct * kb_d

        derived_kb_arr.append(kb_d)
        derived_kb_offset_arr.append(kb_d_offset)
        kb_d_avg_arr.append(err_abs)

    d_arr.append(distance_d)
    kb_arr.append(np.mean(derived_kb_arr))
    kb_offset_arr.append(np.mean(derived_kb_offset_arr))
    kb_err_arr.append(np.mean(kb_d_avg_arr))

fig = plt.figure()

ax1 = fig.add_subplot(111)

ax1.set_xlabel("Distance (m)")
ax1.set_ylabel(r"Derived $k_B$ ($10^{-23} J K^{-1}$)")

ax1.errorbar(d_arr, kb_arr, yerr=kb_err_arr, fmt='.', color='#1f77b4', label="Data", markersize=12)
if OFFSET != 0:
    # ax1.errorbar(d_arr, kb_offset_arr, yerr=kb_err_arr, fmt='c.', label="Data w./ offset {}ms".format(OFFSET), markersize=12)
    ax1.errorbar(d_arr, kb_offset_arr, yerr=kb_err_arr, fmt='m.', label="Data w/o offset", markersize=12)
ax1.plot([np.min(d_arr), np.max(d_arr)],[K_B, K_B], color='#ff7f0e', linestyle = 'dashed', label = r"True $k_B$")

ax1.legend(loc="upper right")
#ax1.loglog()
print("The measurement mean value is {}.".format(np.mean(kb_arr)))
print("The mean error is {}.".format(np.mean(kb_err_arr)))
print("The standard error is {}.".format(std_error(kb_err_arr)))
print("The precision is {}%.".format(np.mean(kb_err_arr) * 100/np.mean(kb_arr)))

try:
    fig_now = plt.gcf()
    plt.show()
except (KeyboardInterrupt, SystemExit):
    save_plot(fig_now)
    exit()
except Exception as e:
    print(e)

save_plot(fig_now)
