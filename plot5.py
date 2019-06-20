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
    eps_loc = "data/plt5_" + str(int(time.time())) + '.eps'
    fig_now.savefig(eps_loc, format='eps')
    print("\nPlot saved to {}.\n".format(eps_loc))

def std_error(err_arr):
    n = len(err_arr)
    ste = np.sqrt(np.sum([e ** 2 for e in err_arr])/(n-1))
    return ste

data_id = util.user_input("data numbers (separated by comma)", val_float=False)
data_id = data_id.split(",")

data_ids = [d.strip() for d in data_id]

# List storing values
d_arr = []
kb_arr = []
kb_vdw_arr = []
kb_rk_arr = []

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
    derived_kb_vdw_arr = []
    derived_kb_rk_arr = []
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
        temp = temp_arr[i]
        # kb_d = util.kb_from_tt_n2(tt, temp, distance_d)
        # kb_d_vdw = util.kb_from_tt_vdw_n2(tt, temp, distance_d, pres)
        # kb_d_rk = util.kb_from_tt_rk_n2(tt, temp, distance_d, pres)
        kb_d = util.kb_from_tt_air(tt, temp, distance_d)
        kb_d_vdw = util.kb_from_tt_vdw_air(tt, temp, distance_d, pres)
        kb_d_rk = util.kb_from_tt_rk_air(tt, temp, distance_d, pres)
        err_pct = util.err_from_tt_pct(tt, temp, distance_d)
        err_abs = err_pct * kb_d

        derived_kb_arr.append(kb_d)
        derived_kb_vdw_arr.append(kb_d_vdw)
        derived_kb_rk_arr.append(kb_d_rk)
        kb_d_avg_arr.append(err_abs)

    d_arr.append(distance_d)
    kb_arr.append(np.mean(derived_kb_arr))
    kb_vdw_arr.append(np.mean(derived_kb_vdw_arr))
    kb_rk_arr.append(np.mean(derived_kb_rk_arr))
    kb_err_arr.append(np.mean(kb_d_avg_arr))

fig = plt.figure()

ax1 = fig.add_subplot(111)

ax1.set_xlabel("Distance (m)")
ax1.set_ylabel(r"Derived $k_B$ ($10^{-23} J K^{-1}$)")

# kb_err_arr = 0

ax1.errorbar(d_arr, kb_arr, yerr=kb_err_arr, fmt='k.', label="w./ Ideal Gas Law", markersize=12)
ax1.errorbar(d_arr, kb_vdw_arr, yerr=kb_err_arr, fmt='b.', label="w./ VDW correction", markersize=12)
ax1.errorbar(d_arr, kb_rk_arr, yerr=kb_err_arr, fmt='r.', label="w./ RK correction", markersize=12)
ax1.plot([np.min(d_arr), np.max(d_arr)],[K_B, K_B], linestyle = '-.', color='#ff7f0e', label = r"True $k_B$")
ax1.plot([np.min(d_arr), np.max(d_arr)],[np.mean(kb_arr), np.mean(kb_arr)],color='k', linestyle = 'dashed', label = "Mean (Ideal Gas)")
ax1.plot([np.min(d_arr), np.max(d_arr)],[np.mean(kb_vdw_arr), np.mean(kb_vdw_arr)],color='b', linestyle = 'dashed', label = "Mean (VDW)")
ax1.plot([np.min(d_arr), np.max(d_arr)],[np.mean(kb_rk_arr), np.mean(kb_rk_arr)],color='r', linestyle = 'dashed', label = "Mean (RK)")

# ax1.set_ylim([1.35, 1.41])

ax1.legend(loc="lower right")
#ax1.loglog()

print("The measurement mean value (ideal gas) is {}.".format(np.mean(kb_arr)))
print("The measurement mean value (VDW) is {}.".format(np.mean(kb_vdw_arr)))
print("The measurement mean value (RK) is {}.".format(np.mean(kb_rk_arr)))
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
