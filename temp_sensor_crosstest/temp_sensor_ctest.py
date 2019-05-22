# Temperature Sensor Cross Test
#
# Written by Jerry Yan c2019

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
import datetime

import serial
import json
import threading
import serial.tools.list_ports

DATA_NAME = "data/{}".format(int(time.time()))

# Saving file name
def file_name(suffix):
    return DATA_NAME + "." + str(suffix)

# Saving the data
def save_data():
    h = ["Time", "Temp BME680", "Temp MCP9808", "Temp BMP280", "Pressure BME680", "Pressure BMP280", "Humidity BME680"]

    try:
        with open(file_name("csv"), "w+") as f:
            dict_writer = csv.DictWriter(f, h)

            dict_writer.writeheader()
            count = len(time_arr)
            for i in range(0, count):
                try:
                    dict_writer.writerow({
                        h[0]: time_arr[i],
                        h[1]: temp_arr[i],
                        h[2]: temp_p_arr[i],
                        h[3]: temp_bmp_arr[i],
                        h[4]: pres_arr[i],
                        h[5]: pres_bmp_arr[i],
                        h[6]: hum_arr[i]
                    })
                except Exception as e:
                    print(e)
                else:
                    pass

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
            if bhold is True:
                raise Exception("Failed to locate an Arduino. Check the connection.")
        except Exception as e:
            print(e)
            print("Will search again in {} seconds...".format(off_delay))
            time.sleep(off_delay)

DELAY = 1

# Arduino Serial Port Information
SERIAL_ADR = search_ard_serial_port()
SERIAL_PORT = 9600
SERIAL_DELAY = 1

# List storing values
time_arr = []
temp_arr = []
pres_arr = []
hum_arr = []
temp_p_arr = []
temp_bmp_arr = []
pres_bmp_arr = []

# t0 = time.perf_counter()

# Arduino Data Collecting Process
def data_collection_ard():
    global time_arr, temp_arr, pres_arr, hum_arr
    try:
        ser = serial.Serial(SERIAL_ADR, SERIAL_PORT)
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
            temp = l_json['temp']
            pres = l_json['pres']
            hum = l_json['hum']
            temp_p = l_json['temp_p']
            temp_bmp = l_json['temp_b']
            pres_bmp = l_json['pres_b']
        except Exception as e:
            print(e)
        else:

            # Calculate time since started
            t = datetime.datetime.now()

            # Recording data
            time_arr.append(t)
            temp_arr.append(temp)
            pres_arr.append(pres)
            hum_arr.append(hum)
            temp_p_arr.append(temp_p)
            temp_bmp_arr.append(temp_bmp)
            pres_bmp_arr.append(pres_bmp)

            print("BME680 Data:\nTemperature: {0} °C    Pressure: {1} Pa    Humidity: {2}%".format(round(temp,2), round(pres, 2), round(hum, 2)))
            print("BMP280 Data:\nTemperature: {0} °C    Pressure: {1} Pa".format(round(temp_bmp,2), round(pres_bmp, 2)))
            print("MCP9808 Data:\nTemperature: {0} °C".format(round(temp_p,4)))
            print()


        time.sleep(SERIAL_DELAY)

thread1 = threading.Thread(target=data_collection_ard, daemon=True)

thread1.start()

fig = plt.figure()

ax1 = fig.add_subplot(311)

ax2 = fig.add_subplot(312)

ax3 = fig.add_subplot(313)

lines = [ax1.plot_date([], [], 'b.', label="BME680", markersize=8)[0], ax1.plot_date([], [], 'c.', label="MCP9808", markersize=8)[0], ax1.plot_date([], [], 'g.', label="BMP280", markersize=8)[0], ax2.plot_date([], [], 'b.', label="BME680", markersize=8)[0], ax2.plot_date([], [], 'g.', label="BMP280", markersize=8)[0], ax3.plot_date([], [], 'b.', label="BME680", markersize=8)[0]]

def plt_init():

    ax1.set_ylabel(r"Temperature ($C^\circ$)")
    ax2.set_ylabel("Pressure (Pa)")
    ax3.set_ylabel("Humidity (%)")

    for ax in [ax1, ax2, ax3]:
        ax.set_xlabel("Time")
        ax.tick_params(direction="in")
        ax.legend(loc="lower right")

    return lines

def main_controller(frame):
    try:
        x_list = list(itertools.repeat(time_arr, 6))
        y_list = [temp_arr, temp_p_arr, temp_bmp_arr, pres_arr, pres_bmp_arr, hum_arr]

        for lnum, line in enumerate(lines):
            line.set_data(x_list[lnum], y_list[lnum])

        fig.gca().relim()
        fig.gca().autoscale_view()

        for ax in [ax1, ax2, ax3]:
            ax.relim()
            ax.autoscale_view()

        ax1.set_ylim([np.min(temp_arr + temp_p_arr + temp_bmp_arr) - 0.2, np.max(temp_arr + temp_p_arr+ temp_bmp_arr) + 0.2])
        ax2.set_ylim([np.min(pres_arr + pres_bmp_arr) - 5, np.max(pres_arr + pres_bmp_arr) +5])
        ax3.set_ylim([np.min(hum_arr) -1, np.max(hum_arr) + 1])
    except (KeyboardInterrupt, SystemExit):
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
    save_data()
    save_plot(fig_now)
    print("Interrupt experienced. Early Exit.")
    exit()
except Exception as e:
    print(e)

print("Exiting the program...")
save_data()
save_plot(fig_now)
