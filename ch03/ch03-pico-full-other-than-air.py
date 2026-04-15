import board
import busio
import time
import os
import simple_ntp
from adafruit_bme280 import basic as adafruit_bme280
from secrets import secrets
import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets['ssid'], secrets['password'])

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('Waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('Network connection failed.')
else:
    print('Connected.')
    status = wlan.ifconfig()
    print('IP = ' + status[0])

simple_ntp.set_time()

print("Time set.")

i2c = busio.I2C(board.GP1, board.GP0)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

# Create the CSV file if it doesn’t already exist
try:
    f = open("data-bme280.csv", "r")
except OSError:  # open failed
    f = open("data-bme280.csv", "w")
    f.write("Time,Temperature,Humidity,Pressure\n")
f.close()
    
rtc=machine.RTC()

while True:
    # Check free space
    stat = os.statvfs("/")
    freespace = stat[0] * stat[3]
    print("Free Space: ", freespace)
    if freespace > 1000: # At least 1Kb left.
        with open('data-bme280.csv', 'a') as file:
            timestamp = rtc.datetime()
            timestring = "%04d-%02d-%02d %02d:%02d:%02d" % \
                         (timestamp[0:3] + timestamp[4:7])
            file.write(
                    timestring + ","
                    + str(bme280.temperature)
                    + "," + str(bme280.humidity)
                    + "," + str(bme280.pressure)
                    +"\n")
            print("Wrote data.")
    
    time.sleep(10)