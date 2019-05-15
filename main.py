#!/usr/bin/env python3

# main.py - the main file for measuring Boltzmann constant experiment
#
# Created by Jerry Yan
#
# Some code excerpted from Physics 13BH/CS15B

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

import RPi.GPIO as GPIO

import board
import busio
import adafruit_bmp280

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

i2c = busio.I2C(board.SCL, board.SDA)
bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

if (bmp280.temperature > 0):
    print()
    print("BMP280 has been connected.")
    print()

# Data Name Format
DATA_NAME = "data/{}".format(int(time.time()))

# Module to securely prompt for a user input
def user_input(val_name, val_range = None):
    input_hold = True

    while(input_hold):
        try:
            val_d = input("Please enter the value of {}: ".format(val_name))
            val_d = float(val_d)
            val_min = val_range[0]
            val_max = val_range[1]
            if val_d < val_min or val_d > val_max:
                raise Exception("{} out of range.".format(val_name))
        except Exception as e:
            print(e)
            print("ERROR. Please try again.")
        else:
            input_hold = False
    print()
    print("{0} is set as {1}.".format(val_name, val_d))
    print()
    return val_d

def timett():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime

    return TimeElapsed

def temp_bmp():
    temp_C = bmp280.temperature
    temp_K = temp_C + 273.15
    return temp_K

# Saving file name
def file_name(suffix):
    return DATA_NAME + "." + str(suffix)

# Saving the data
def save_data():
    h = ["Time", "Exp Distance", "Measured Time Diff", "Temperature", "Derived k_B", "Derived k_B Error"]

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
                    h[5]: kb_err_abs_arr[i]
                })

            f.close()
        print("\nData saved to {}.\n".format(file_name('csv')))
    except Exception as e:
        print(e)
    else:
        pass
    pass

# Save the plot
def save_plot(fig):
    fig_now.savefig(file_name("eps"), format='eps')
    print("\nPlot saved to {}.\n".format(file_name("eps")))

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
DIS_ERR_ABS = 0.005
TT_ERR_ABS = 4.665306263360271e-07
TEMP_ERR_ABS = 0.5

# List storing values
tt_arr = []
time_arr = []
temp_arr = []

derived_kb_arr = []
kb_err_abs_arr = []

def c_from_tt(tt, dis):
    c_sound = dis / tt
    return c_sound

def kb_from_tt(tt, temp, dis):
    c_sound = c_from_tt(tt, dis)
    kb = (c_sound ** 2) * MOLAR_MASS / (GAMMA * N_A * temp)
    return kb

# # Van der Waals Correction
# def kb_from_vdw_tt(tt, temp, pres, dis):


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

distance_d = user_input("distance in cm", (1,200))

distance_d = distance_d / 100 * 2

print()
print("NOTE: You can exit the recodring early by pressing ctrl + C.")

fig = plt.figure(1)

ax = plt.gca()
line, (bottoms, tops), verts = ax.errorbar([0], [0], yerr=0.01, capsize=3, fmt='ko', markersize=4, elinewidth=1,label="Realtime Measurement").lines

# st_lines = [plt.plot([], [], linestyle='dashed', label="Mean Measured Value")[0], plt.plot([], [], linestyle='dashed', label=r"True $k_B$")[0], plt.plot([], [], 'm', linestyle='dashed', label=r"+3$\sigma$")[0], plt.plot([], [], 'm', linestyle='dashed', label=r"-3$\sigma$")[0]]
st_lines = [plt.plot([], [], linestyle='dashed', label="Mean Measured Value")[0], plt.plot([], [], linestyle='dashed', label=r"True $k_B$")[0]]

t0 = time.perf_counter()

def plt_init():
    plt.xlabel("Time (s)")
    plt.ylabel(r"Derived $k_B$ ($10^{-23} J K^{-1}$)")
    plt.legend(loc="lower right")

    # line.set_xdata([0])
    # line.set_ydata([0])
    # bottoms.set_ydata([0])
    # tops.set_ydata([0])
    # for line in lines:
    #     line.set_data([], [])
    return line, bottoms, tops, verts, st_lines

def main_controller(frame):
    global tt_arr
    global time_arr
    global temp_arr
    global derived_kb_arr
    global kb_err_abs_arr
    try:

        tt = timett()
        temp = temp_bmp()

        c_s = c_from_tt(tt, distance_d)
        kb_d = kb_from_tt(tt, temp, distance_d)

        err_pct = err_from_tt_pct(tt, temp, distance_d)
        err_abs = err_pct * kb_d

        # Calculate time since started
        t = time.perf_counter() - t0

        # Recording data
        tt_arr.append(tt)
        time_arr.append(t)
        temp_arr.append(temp)

        derived_kb_arr.append(kb_d)
        kb_err_abs_arr.append(err_abs)

        kb_d_avg = np.mean(derived_kb_arr)

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

        # Plotting Data with Error Bars
        err_gp = err_arr_gp(time_arr, derived_kb_arr, kb_err_abs_arr)
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
        x_list = list(itertools.repeat([np.min(time_arr), np.max(time_arr)], 2))
        y_list = [[kb_d_avg , kb_d_avg], [K_B, K_B]]

        for lnum, st_line in enumerate(st_lines):
            st_line.set_data(x_list[lnum], y_list[lnum])

        fig.gca().relim()
        fig.gca().autoscale_view()

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
    GPIO.cleanup()
    print(e)

print("Exiting the program...")
GPIO.cleanup()
save_data()
save_plot(fig_now)
