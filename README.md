# Measuring-k_B
A repo for the experiment measuring k_B (Boltzmann Constant) in Physics 13CH/CS15C of UCSB.

## Overview
Boltzmann constant is one of the most important constants in physics. Specifically, there is hardly any thermodynamics equation unrelated to Boltzmann constant. With the ideal gas law, we know that Boltzmann constant is related with speed of sound. We hope to obtain the data of sound speed in certain gas in a range of temperature, and find the value of Boltzmann constant.

## Materials
The scripts in this repository are based on python and Raspberry Pi 3 B+ or Arduino uno. The scripts are designed to be run on Raspberry 3 B+ or Arduino uno. The following sensors (with certain accessories like resistors) are used as follows:
  * HC-SR04 Ultrasonic Wave Detector Ranging Module
  * BMP280 Barometric Pressure and Temperature Sensor

## Scripts
The python scripts in this repository provide useful tools to monitor the data and analyze the data obtained by the sensors.
  * `main.py` - *(Deprecated)* The main script provides real-time monitoring of the measurements and plots a graph of derived Boltzmann constant with real-time updates. Error bars and standard error lines are included for convenience. Automatic saving of data and plot before exiting the program.
  * `us-test.py` - A script to test the HC-SR04 Ultrasonic Wave Detector Ranging Module. It prints the distance (with sound speed of 343.0 m/s) that the sensor detects in real-time.
  * `bmp_test.py` - A script to test the BMP180 Barometric Pressure, Temperature and Altitude Sensor. Adapted from Adafruit (see Resources).
  * `bmp280_test.py` - A script to test the BMP280 Barometric Pressure and Temperature Sensor. Adapted from Adafruit (see Resources).
  * `ard_code.ino` - The Arduino code to take HC-SR04 and BMP280 measurements and write JSON data to the serial ports.
  * `pyserial_test.py` - A script to test the ability of python client to receive and parse JSON data from Arduino.
  * `main_ard.py` - *(Preferred)* The client-side script (using with Arduino via code `ard_code.ino`) provides real-time monitoring of the measurements and plots a graph of derived Boltzmann constant with real-time updates. Error bars and standard error lines are included for convenience. Automatic saving of data and plot before exiting the program. All data analysis computations and plotting are done on the client side, which shall has no effect on the time-precision-sensitive measurements that are done on the Arduino side. The script utilizes the multithreading feature in Python 3, which allows the script to receive the data measurement from Arduino and generate a real-time plot simultaneously.
    * *Note: `ard_code.ino` should always be uploaded to Arduino before running `main_ard.py`.*
  * `plot.py` - A simple script to plot an existing data set. Automatic saving of plot before exiting the program.
  * `plot2.py` - A simple script to plot an existing data set, with comparison of the data with and with out Van der Waals correction. Automatic saving of plot before exiting the program.

## Notes
Currently our experiment works under the atmosphere environment. We plan to increase the accuracy of the measurements by implementing the following improvements in the near future:

* Conduct our experiments in pure gas environments (Nitrogen, Oxygen, etc). We are planning to use the glove boxes.
* Use BMP280 I2C or SPI Barometric Pressure and Altitude Sensor, which has 2x accuracy than the current BMP180 sensor. **[Implemented]**
* More accurate distance measurements with infrared (IR) distance sensor.
* Precision time measurements by replacing Raspberry Pi with Arduino. **[Implemented]**

## People
This is a project from Physics 13CH/CS15C course of UCSB. Our team members are:
  * Panyu Chen
  * Jerry Yan
  * Jiarui Zhu

and our supervisors are:
  * Andrew Jayich (Course Instructor)
  * Remi Boros (TA)
  * Craig Holliman (TA)

We want to express our appreciation for assistance from our supervisors and classmates.

## Resources
Our scripts may include knowledge/code from the following sources:
  * [Raspberry Pi Tutorials](https://tutorials-raspberrypi.com/raspberry-pi-ultrasonic-sensor-hc-sr04/) for HC-SR04
  * [Raspberry Pi Tutorials](https://tutorials-raspberrypi.com/raspberry-pi-and-i2c-air-pressure-sensor-bmp180/) for BMP180
  * [Adafruit BMP085](https://github.com/adafruit/Adafruit_Python_BMP)
  * [Adafruit BMP280 Sensor Breakout](https://learn.adafruit.com/adafruit-bmp280-barometric-pressure-plus-temperature-sensor-breakout/)
  * [PySerial](https://pyserial.readthedocs.io/en/latest/index.html)
  * [ArduinoJson](https://arduinojson.org)
  * [Arduino Guide](https://randomnerdtutorials.com/complete-guide-for-ultrasonic-sensor-hc-sr04/) for HC-SR04
