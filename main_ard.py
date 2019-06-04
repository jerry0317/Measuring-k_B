#!/usr/bin/env python3

# main_ard.py - the main file for measuring Boltzmann constant experiment (with Arduino)
#
# Created by Jerry Yan
#
# Some code excerpted from Physics 13BH/CS15B

import util

import sys
import time
import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from scipy import stats
import os
import csv
import itertools

import serial
import json
import threading
import serial.tools.list_ports

# Boltzmann constant (10^-23)
K_B = 1.38064852

# HC-SR04 Offset (us)
SR04_OFFSET = 55

# Data Name Format
DATA_NAME = "data/{}".format(int(time.time()))

# Saving file name
def file_name(suffix):
    return DATA_NAME + "." + str(suffix)

# Saving the data
def save_data():
    h = ["Time", "Exp Distance", "Measured Time Diff", "Temperature", "Derived k_B", "Derived k_B Error", "Pressure", "HC-SRO4 Raw"]

    try:
        with open(file_name("csv"), "w+") as f:
            dict_writer = csv.DictWriter(f, h)

            dict_writer.writeheader()
            try:
                count = len(time_arr)
                if len(temp_arr) != count or len(tt_arr) != count or len(derived_kb_arr) != count:
                    raise Exception("Different list lengths.")
            except Exception as e:
                print(e)
            else:
                pass

            for i in range(0, count):
                dict_writer.writerow({
                    h[0]: time_arr[i],
                    h[1]: distance_d,
                    h[2]: tt_arr[i],
                    h[3]: temp_arr[i],
                    h[4]: derived_kb_arr[i],
                    h[5]: kb_err_abs_arr[i],
                    h[6]: pres_arr[i],
                    h[7]: time_arr[i] - SR04_OFFSET
                })

            f.close()
        print("Data saved to {}.\n".format(file_name('csv')))
    except Exception as e:
        print(e)
    else:
        pass
    pass

# Save the plot
def save_plot(fig):
    fig_now.savefig(file_name("eps"), format='eps')
    print("Plot saved to {}.\n".format(file_name("eps")))

# Search for Arduino Serial Port
def search_ard_serial_port():
    bhold = True
    off_delay = 3
    while bhold:
        try:
            ports = serial.tools.list_ports.comports()
            for pinfo in ports:
                if 'Arduino' in str(pinfo.manufacturer):
                    print("Arduino has been located.")
                    print("Serial information: {}".format(pinfo.device))
                    bhold = False
                    return pinfo.device
                elif 'DevB' in str(pinfo.device):
                    print("Bluetooth module has been located.")
                    print("Serial information: {}".format(pinfo.device))
                    bhold = False
                    return pinfo.device
            if bhold is True:
                raise Exception("Failed to locate an Arduino. Check the connection.")
        except Exception as e:
            print(e)
            print("Will search again in {} seconds...".format(off_delay))
            time.sleep(off_delay)

# Controller Constants
DELAY = 1

# Arduino Serial Port Information
SERIAL_ADR = search_ard_serial_port()
SERIAL_PORT = 9600
SERIAL_DELAY = 1

distance_d = util.user_input("distance in cm", (1,400))
distance_d = distance_d / 100 * 2

# List storing values
tt_arr = []
time_arr = []
temp_arr = []
pres_arr = []

derived_kb_arr = []
kb_err_abs_arr = []

kb_avg_arr = []

t0 = time.perf_counter()

# Arduino Data Collecting Process
def data_collection_ard():
    global tt_arr, time_arr, temp_arr, derived_kb_arr, kb_err_abs_arr, kb_avg_arr, pres_arr
    try:
        ser = serial.Serial(SERIAL_ADR, SERIAL_PORT, timeout=20)
    except Exception as e:
        print(e)
        print("FATAL ERROR. EARLY EXIT.")
        return
    else:
        pass

    while True:
        l = ser.readline()
        l = l.decode('utf-8')
        try:
            l_json = json.loads(l)
            tt_us = l_json['tt_us']
            temp = l_json['temp']
            pres = l_json['pres']
            if tt_us == 0:
                raise Exception("Zero Time Diff.")
        except Exception as e:
            print(e)
            print("Serial reads:")
            print(l)
        else:
            tt = (tt_us + SR04_OFFSET) * 10 ** (-6)
            temp = temp + 273.15

            c_s = util.c_from_tt(tt, distance_d)
            #kb_d = util.kb_from_tt(tt, temp, distance_d)
            #kb_d = util.kb_from_tt_vdw_n2_aprx(tt, temp, distance_d)
            #kb_d = util.kb_from_tt_vdw_n2(tt, temp, distance_d, pres)
            kb_d = util.kb_from_tt_rk_air(tt, temp, distance_d, pres)


            err_pct = util.err_from_tt_pct(tt, temp, distance_d)
            err_abs = err_pct * kb_d

            # Calculate time since started
            t = time.perf_counter() - t0

            # Recording data
            tt_arr.append(tt)
            time_arr.append(t)
            temp_arr.append(temp)
            pres_arr.append(pres)

            derived_kb_arr.append(kb_d)
            kb_err_abs_arr.append(err_abs)

            kb_d_avg = np.mean(derived_kb_arr)

            kb_avg_arr.append(kb_d_avg)

            if len(time_arr) > 1:
                kb_d_sigma = stats.sem(derived_kb_arr)
            else:
                kb_d_sigma = 0
            kb_d_sigma_up = kb_d_avg + 3 * kb_d_sigma
            kb_d_sigma_down = kb_d_avg - 3 * kb_d_sigma

            # Print result
            print("The measured temperature is {0} K ({1} °C).".format(round(temp,2), round((temp-273.15),2)))
            print("The derived speed of sound is {} m/s.".format(c_s))
            print("The derived k_B is {}.".format(kb_d))
            print("The averaged derived k_B is {}.".format(kb_d_avg))
            print("The precision of the measurement is {}%.".format(err_pct * 100))

            print()

        time.sleep(SERIAL_DELAY)

print()
print("NOTE!: Exit the recodring early by pressing ctrl + C.")

thread1 = threading.Thread(target=data_collection_ard, daemon=True)

thread1.start()

fig = plt.figure()

ax1 = fig.add_subplot(211)

# ax2 = fig.add_subplot(234)
# ax3 = fig.add_subplot(235)
# ax4 = fig.add_subplot(236)

ax2 = fig.add_subplot(223)
ax3 = fig.add_subplot(224)

line, (bottoms, tops), verts = ax1.errorbar([0], [0], yerr=0.01, capsize=0.1, fmt='ko', markersize=4, elinewidth=1,label="Realtime Measurement").lines

# st_lines = [plt.plot([], [], linestyle='dashed', label="Mean Measured Value")[0], plt.plot([], [], linestyle='dashed', label=r"True $k_B$")[0], plt.plot([], [], 'm', linestyle='dashed', label=r"+3$\sigma$")[0], plt.plot([], [], 'm', linestyle='dashed', label=r"-3$\sigma$")[0]]
st_lines = [ax1.plot([], [], linestyle='dashed', label="Mean Measured Value")[0], ax1.plot([], [], linestyle='dashed', label=r"True $k_B$")[0], ax1.plot([], [], '.', label="Instantaneous Average Value", markersize=8)[0], ax2.plot([], [], '.', label="Temperature")[0], ax3.plot([], [], '.', label="Pressure")[0]]

def plt_init():

    ax1.set_ylabel(r"Derived $k_B$ ($10^{-23} J K^{-1}$)")
    ax2.set_ylabel(r"Temperature $T$ (K)")
    ax3.set_ylabel(r"Pressure $P$ (Pa)")
    #ax4.set_ylabel("Echo Pulse duration (s)")

    for ax in [ax1, ax2, ax3]:
        ax.set_xlabel("Time (s)")
        ax.legend(loc="lower right")
        ax.tick_params(direction="in")

    return line, bottoms, tops, verts, st_lines

def main_controller(frame):
    global tt_arr, time_arr, temp_arr, derived_kb_arr, kb_err_abs_arr, kb_avg_arr

    try:
        # Plotting Data with Error Bars
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

        # x_list.append(time_arr)
        # y_list.append(tt_arr)

        for lnum, st_line in enumerate(st_lines):
            st_line.set_data(x_list[lnum], y_list[lnum])

        fig.gca().relim()
        fig.gca().autoscale_view()

        for ax in [ax1, ax2, ax3]:
            ax.relim()
            ax.autoscale_view()

        ax2.set_ylim([np.min(temp_arr) - 0.1,np.max(temp_arr) + 0.1])
        ax3.set_ylim([np.min(pres_arr) - 25,np.max(pres_arr) + 25])
        #ax4.set_ylim([np.min(tt_arr) * 0.9, np.max(tt_arr) * 1.1])

    except (KeyboardInterrupt, SystemExit):
        print()
        print("Interrupt experienced.")
    except Exception as e:
        print(e)
    finally:
        return line, bottoms, tops, verts, st_lines

anim = animation.FuncAnimation(fig, main_controller, interval=DELAY*1000, init_func = plt_init)

try:
    print("NOTE: You can close the pyplot window to exit the program.")
    fig_now = plt.gcf()
    plt.show()
except (KeyboardInterrupt, SystemExit):
    save_data()
    save_plot(fig_now)
    print("Interrupt experienced. Early Exit.")
    exit()
except Exception as e:
    print(e)

print("Exiting the program...")
save_data()
save_plot(fig_now)
