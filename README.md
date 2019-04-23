# Measuring-k_B
A repo for the experiment measuring k_B (Boltzmann Constant) in Physics 13CH/CS15C of UCSB.

## Overview
Boltzmann constant is one of the most important constants in physics. Specifically, there is hardly any thermodynamics equation unrelated to Boltzmann constant. With the ideal gas law, we know that Boltzmann constant is related with speed of sound. We hope to obtain the data of sound speed in certain gas in a range of temperature, and find the value of Boltzmann constant.

## Materials
The scripts in this repository are based on python and Raspberry Pi 3 B+. The scripts are designed to be run solely on Raspberry 3 B+. The following sensors (with certain accessories like resistors) are used as follows:
  * HC-SR04 Ultrasonic Wave Detector Ranging Module
  * BMP180 Barometric Pressure, Temperature and Altitude Sensor

## Scripts
The python scripts in this repository provide useful tools to monitor the data and analyze the data obtained by the sensors.
  * `main.py` - The main script provides real-time monitoring of the measurements and plot a graph of derived Boltzmann constant with real-time updates. Automatic saving of data and plot before exiting the program.
  * `us-test.py` - A script to test the HC-SR04 Ultrasonic Wave Detector Ranging Module. It prints the distance (with sound speed of 343.0 m/s) that the sensor detects in real-time.
  * `bmp_test.py` - A script to test the BMP180 Barometric Pressure, Temperature and Altitude Sensor. Adapted from Adafruit (see Resources).

## Notes
Currently our experiment works under the atmosphere environment. We plan to increase the accuracy of the measurements by implementing the following improvements in the near future:

* Conduct our experiments in pure gas environments (Nitrogen, Oxygen, etc).
* Use BMP280 I2C or SPI Barometric Pressure and Altitude Sensor, which has 2x accuracy than the current BMP180 sensor.

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
