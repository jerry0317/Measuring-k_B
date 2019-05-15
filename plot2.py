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

def c_from_tt(tt, dis):
    c_sound = dis / tt
    return c_sound

def kb_from_tt(tt, temp, dis):
    c_sound = c_from_tt(tt, dis)
    kb = (c_sound ** 2) * MOLAR_MASS / (GAMMA * N_A * temp)
    return kb

# N2 VDW Approximation
def kb_from_tt_vdw_n2_aprx(tt, temp, dis):
    c_sound = c_from_tt(tt, dis)
    kb = ((c_sound ** 2) - 131) / (1.002 * 1.4 * temp) * (2.32586 * 2 * 10 ** -3)
    return kb

def err_from_tt_pct(tt, temp, dis):
    dis_err_pct = DIS_ERR_ABS / dis
    temp_err_pct = TEMP_ERR_ABS / temp
    tt_err_pct = TT_ERR_ABS / tt
    err_pct = 2 * (dis_err_pct + tt_err_pct) + temp_err_pct
    return err_pct

def err_from_tt_vdw_pct(tt, temp, pres, dis):
    dis_err_pct = DIS_ERR_ABS / dis
    temp_err_pct = TEMP_ERR_ABS / temp
    tt_err_pct = TT_ERR_ABS / tt
    err_pct = 2 * (dis_err_pct + tt_err_pct) + temp_err_pct
    return err_pct

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
    eps_loc = DATA_NAME + "_plt2_" + str(int(time.time())) + '.eps'
    fig_now.savefig(eps_loc, format='eps')
    print("\nPlot saved to {}.\n".format(eps_loc))

# Boltzmann constant (10^-23)
K_B = 1.38064852

# Avogadro constant (10^23)
N_A = 6.02214

# Experiment Constants
# DISTANCE = 1
MOLAR_MASS = 28.97 * 10 ** (-3)
GAMMA = 1.40

# Van der Waals Constants
VDW_A = 0
VDW_B = 0

# Controller Constants
DELAY = 1

# Experiment Error Constants
DIS_ERR_ABS = 0.0025
TT_ERR_ABS = 4.665306263360271e-07
TEMP_ERR_ABS = 0.5

data_id = util.user_input("data number", float=False)
DATA_NAME = DATA_NAME = "data/{}".format(data_id)
csv_loc = DATA_NAME + ".csv"

# List storing values
tt_arr = []
time_arr = []
temp_arr = []

derived_kb_arr = []
kb_err_abs_arr = []
kb_avg_arr = []

derived_kb_vdw_arr = []
kb_err_abs_vdw_arr = []
kb_avg_vdw_arr = []

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

    print("The data set has been successfully loaded from CSV file.")
except Exception as e:
    print(e)

for i in range(0, len(time_arr)):
    tt = tt_arr[i]
    temp = temp_arr[i]
    c_s = c_from_tt(tt, distance_d)
    # kb_d = kb_from_tt(tt, temp, distance_d)
    kb_d = kb_from_tt(tt, temp, distance_d)

    err_pct = err_from_tt_pct(tt, temp, distance_d)
    err_abs = err_pct * kb_d

    derived_kb_arr.append(kb_d)
    kb_err_abs_arr.append(err_abs)

    kb_d_avg = np.mean(derived_kb_arr)

    kb_avg_arr.append(kb_d_avg)

    kb_d = kb_from_tt_vdw_n2_aprx(tt, temp, distance_d)
    err_pct = err_from_tt_pct(tt, temp, distance_d)
    err_abs = err_pct * kb_d

    derived_kb_vdw_arr.append(kb_d)
    kb_err_abs_vdw_arr.append(err_abs)

    kb_d_avg = np.mean(derived_kb_vdw_arr)

    kb_avg_vdw_arr.append(kb_d_avg)

fig = plt.figure()

ax1 = fig.add_subplot(211)

ax2 = fig.add_subplot(212)

line, (bottoms, tops), verts = ax1.errorbar([0], [0], yerr=0.01, capsize=0.1, fmt='ko', markersize=4, elinewidth=1,label="Measurement").lines

lineb, (bottomsb, topsb), vertsb = ax1.errorbar([0], [0], yerr=0.01, capsize=0.1, fmt='bo', markersize=4, elinewidth=1,label="Measurement (w./ Correction)").lines

st_lines = [ax1.plot([], [], linestyle='dashed', label="Mean Measured Value")[0], ax1.plot([], [], linestyle='dashed', label="Mean Measured Value (w./ Correction)")[0], ax1.plot([], [], '.', label="Instantaneous Average Value", markersize=8)[0], ax1.plot([], [], '.', label="Instantaneous Average Value (w./ Correction)", markersize=8)[0], ax1.plot([], [], linestyle='dashed', label=r"True $k_B$")[0], ax2.plot([], [], '.', label="Temperature")[0]]

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

err_gpb = err_arr_gp(time_arr, derived_kb_vdw_arr, kb_err_abs_vdw_arr)
lineb.set_xdata(time_arr)
lineb.set_ydata(derived_kb_vdw_arr)
bottomsb.set_xdata(time_arr)
topsb.set_xdata(time_arr)
bottomsb.set_ydata(err_gpb[0])
topsb.set_ydata(err_gpb[1])
vertsb[0].set_segments(err_gpb[2])

kb_d_avgb = np.mean(derived_kb_vdw_arr)

x_list = [[np.min(time_arr), np.max(time_arr)], [np.min(time_arr), np.max(time_arr)], time_arr, time_arr, [np.min(time_arr), np.max(time_arr)], time_arr]
y_list = [[kb_d_avg , kb_d_avg], [kb_d_avgb , kb_d_avgb],kb_avg_arr, kb_avg_vdw_arr, [K_B, K_B], temp_arr]

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