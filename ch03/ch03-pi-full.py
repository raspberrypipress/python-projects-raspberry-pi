import board
import busio
import time
import os
from adafruit_bme280 import basic as adafruit_bme280
from ch03_pms5003 import read_pms5003, init_pms5003
import serial
import datetime

uart = serial.Serial('/dev/ttyUSB0')
init_pms5003(uart)

i2c = busio.I2C(board.D3, board.D2)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# Create the CSV file if it doesn’t already exist
try:
    f = open("data.csv", "r")
except OSError:  # open failed
    f = open("data.csv", "w")
    f.write("Time,Temperature,Humidity,Pressure,PM1,PM2.5,PM10\n")
f.close()
    

while True:
    # Check free space
    stat = os.statvfs("/")
    freespace = stat[0] * stat[3]
    print("Free Space: ", freespace)
    if freespace > 1000: # at least 1Kb left. 
        with open('data.csv', 'a') as file:
            timestamp=datetime.datetime.now()
            pm1, pm25, pm10 = read_pms5003(uart)
            timestring = timestamp.strftime("%Y-%m-%0d %H:%M:%S")
            file.write(
                    timestring + ","
                    + str(bme280.temperature)
                    + "," + str(bme280.humidity)
                    + "," + str(bme280.pressure)
                    + "," + str(pm1)
                    + "," + str(pm25)
                    + "," + str(pm10)
                    +"\n")
            print("Wrote data.")
    
    time.sleep(10)