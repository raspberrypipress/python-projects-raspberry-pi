import board
import busio
import time
import digitalio
import os

#do I want to set the RTC?
#might be nice
# Grab the one from the bread proofing
# gives a bit more reason to use I2C as well.

from adafruit_bme280 import basic as adafruit_bme280

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

