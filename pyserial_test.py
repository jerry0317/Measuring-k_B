import serial
import time
import json

ser = serial.Serial('/dev/cu.usbmodem14201', 9600)

while True:
    l = ser.readline()
    l = l.decode('utf-8')
    try:
        l_json = json.loads(l)
    except Exception as e:
        print(e)
    else:
        print(l_json)
    time.sleep(0.2) # Delay for one tenth of a second
