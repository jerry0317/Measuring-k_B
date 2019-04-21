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
import os

import random

#from wpdir import wiringpi

import RPi.GPIO as GPIO

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

#set GPIO Pins
GPIO_TRIGGER = 18
GPIO_ECHO = 24

#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


# Data Name Format
DATA_NAME = "data/{}".format(int(time.time()))

# Boxcar averaging ON/OFF
BOXCAR_AVG = False

# Boxcar Averaging Algorithm
def boxcar_avg(varset, times, b_interval, var_name = None, var_unit = None, print_results = True):
    t_n = times[-1]
    t_t = t_n - b_interval
    time_for_avg = [t for t in times if t > t_t]
    l = len(time_for_avg)
    var_to_avg = varset[-l:]
    avg_var = np.mean(var_to_avg)
    if print_results and var_name is not None:
        print("The boxcar averaged {0} is {1} {2}.".format(var_name, round(avg_temp,4), var_unit))
    return avg_var

# Module to securely prompt for a user input
def user_input(val_name, val_range = None):
    input_hold = True

    while(input_hold):
        try:
            val_d = input("Please enter an desired {}: ".format(val_name))
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
        StartTime = time.perf_counter()

    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.perf_counter()

    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime

    return TimeElapsed

# Saving file name
def file_name(suffix):
    return DATA_NAME + "." + str(suffix)

# Saving the data
def save_data():
    # global temp_arr
    # global time_arr
    # if BOXCAR_AVG:
    #     global box_temp_arr
    # try:
    #     with open(file_name("txt"), "w+") as f:
    #         if BOXCAR_AVG:
    #             f.write("Boxcar Averaging is turned on.\n")
    #             f.write("Time (s)    Temperature (°C)    Averaged T (°C)\n")
    #         else:
    #             f.write("Boxcar Averaging is turned off.\n")
    #             f.write("Time (s)    Temperature (°C)\n")
    #         try:
    #             count = len(time_arr)
    #             if len(temp_arr) != count:
    #                 raise Exception("Different list lengths.")
    #             if BOXCAR_AVG:
    #                 if len(box_temp_arr) != count:
    #                     raise Exception("Different list lengths.")
    #         except Exception as e:
    #             print(e)
    #         else:
    #             pass
    #
    #         for i in range(0, count):
    #             if BOXCAR_AVG:
    #                 f.write("{0}    {1}    {2}\n".format(round(time_arr[i], 4), round(temp_arr[i], 4), round(box_temp_arr[i], 4)))
    #             else:
    #                 f.write("{0}    {1}\n".format(round(time_arr[i], 4), round(temp_arr[i], 4)))
    #
    #     print("\nData saved to {}.\n".format(file_name('txt')))
    # except Exception as e:
    #     print(e)
    # else:
    #     pass
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

# Controller Constants
DELAY = 1.0

# List storing values
tt_arr = []
time_arr = []
temp_arr = []

derived_kb_arr = []

if BOXCAR_AVG:
    box_temp_arr = []

def c_from_tt(tt, dis):
    c_sound = dis / tt
    return c_sound

def kb_from_tt(tt, temp, dis):
    c_sound = c_from_tt(tt, dis)
    kb = (c_sound ** 2) * MOLAR_MASS / (GAMMA * N_A * temp)
    return kb

# temp_d = user_input("temperature", (30, 60))

if BOXCAR_AVG:
    boxcar_interval = user_input("boxcar time interval", (1, 1000))

t0 = time.perf_counter()
# print("\nThe {}-second temperature recording has been initiated. \n".format(TIME_ELAPSED))

distance_d = user_input("distance in cm", (1,200))

distance_d = distance_d / 100

print()
print("NOTE: You can exit the recodring early by pressing ctrl + C.")

fig = plt.figure(1)
lines = [plt.plot([], [], '.', label="Realtime Measurement", markersize=10)[0], plt.plot([], [], linestyle='dashed', label="Mean Measured Value")[0], plt.plot([], [], linestyle='dashed', label="True $k_B$")[0]]

def plt_init():
    plt.xlabel("Time (s)")
    plt.ylabel(r"Derived $k_B$ ($10^{-23}m^2 kg s^{-2} K^{-1}$)")
    plt.legend(loc="lower right")
    for line in lines:
        line.set_data([], [])
    return lines

def main_controller(frame):
    global tt_arr
    global time_arr
    global temp_arr
    global derived_kb_arr
    try:

        #tt = (random.randrange(-1000,1000))*0.01*(DISTANCE/343)*(1/1000) + (DISTANCE/343)
        #temp = (random.randrange(-1000,1000))*0.01*(293.15)*(1/1000) + (293.15)
        tt = timett()
        temp = 293.15

        c_s = c_from_tt(tt, distance_d)
        kb_d = kb_from_tt(tt, temp, distance_d)

        # Calculate time since started
        t = time.perf_counter() - t0

        # Recording data
        tt_arr.append(tt)
        time_arr.append(t)
        temp_arr.append(temp)

        derived_kb_arr.append(kb_d)

        kb_d_avg = np.mean(derived_kb_arr)

        # Print result
        print("The measured temperature is {} K.".format(temp))
        print("The derived speed of sound is {} m/s.".format(c_s))
        print("The derived k_B is {}.".format(kb_d))
        print("The averaged derived k_B is {}.".format(kb_d_avg))

        print()

        # Plotting Data
        x_list = [time_arr, [np.min(time_arr), np.max(time_arr)], [np.min(time_arr), np.max(time_arr)]]
        y_list = [derived_kb_arr, [kb_d_avg , kb_d_avg], [K_B, K_B]]

        for lnum, line in enumerate(lines):
            line.set_data(x_list[lnum], y_list[lnum])

        fig.gca().relim()
        fig.gca().autoscale_view()

    except (KeyboardInterrupt, SystemExit):
        setPWM(0)
        print()
        print("Interrupt experienced.")
    except Exception as e:
        print(e)
    finally:
        return lines


anim = animation.FuncAnimation(fig, main_controller, interval=DELAY*1000, init_func = plt_init)

try:
    print("NOTE: You can close the pyplot window to exit the program.")
    fig_now = plt.gcf()
    plt.show()
except (KeyboardInterrupt, SystemExit):
    #save_data()
    #save_plot(fig_now)
    print("Interrupt experienced. Early Exit.")
    exit()
except Exception as e:
    GPIO.cleanup()
    print(e)

print("Exiting the program...")
GPIO.cleanup()
save_data()
save_plot(fig_now)
