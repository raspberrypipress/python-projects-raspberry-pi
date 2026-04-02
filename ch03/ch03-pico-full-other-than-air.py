import board
import busio
import time
import digitalio
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
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

simple_ntp.set_time()

print("time set")

i2c=busio.I2C(board.GP1, board.GP0)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

#check if the file exists and if it doesn't, create it with the right headings
try:
    f = open("data.csv", "r")
except OSError:  # open failed
    f = open("data.csv", "w")
    f.write("Temperature, Humidity, Pressure \n")
    f.close()
    
#set RTC from DS3231?
rtc=machine.RTC()
   

while True:
    #check free space
    #if enough:
    stat = os.statvfs("/")
    freespace = stat[0] * stat[3]
    print("Free Space: ", freespace)
    if freespace > 1000: #at least 1Kb left. this is probably overkill, but no point in emptying it
        with open('data.csv', 'a') as file:
            timestamp=rtc.datetime()
            timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] +
                                                timestamp[4:7])
            file.write(timestring + "," + str(bme280.temperature) + "," + str(bme280.humidity) + "," + str(bme280.pressure)+"\n")
            print("writing data")
    
    
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)
    
    time.sleep(10)

