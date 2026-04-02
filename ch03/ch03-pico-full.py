import board
import busio
import time
import digitalio
import os
import simple_ntp
from adafruit_bme280 import basic as adafruit_bme280
from secrets import secrets
import network
from machine import UART, Pin
import struct

data_format = ">BBHHHHHHHHHHHHHHH"
mode_passive = b'\xe1\x00\x00'
command_read = b'\xe2\x00\x00'
start_of_frame = bytearray(b'\x42\x4d')

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets['ssid'], secrets['password'])

set_passive_command = bytearray()
set_passive_command.extend(start_of_frame)
set_passive_command.extend(mode_passive)
set_passive_command.extend(sum(set_passive_command).to_bytes(2, "big"))

read_command = bytearray()
read_command.extend(start_of_frame)
read_command.extend(command_read)
read_command.extend(sum(read_command).to_bytes(2, "big"))

timeout = 200 # in ms

uart = UART(0,9600, tx=Pin(12), rx=Pin(13))
uart.write(set_passive_command)

def read_pms5003():
    uart.write(read_command)
    
    time.sleep(0.1)
    
    raw_data = bytes()
    got_data = False
    while uart.any() > 0:
        #need to loop through to avoid timeout
        last_data = time.ticks_ms()
        while time.ticks_ms() < last_data + timeout:
            if uart.any():
                raw_data += uart.read(1)
        got_data = True
       
    if got_data:
        try:
            data = struct.unpack(data_format, raw_data)
        except ValueError:
            print("data malformed")
            return (-1,-1,-1)
    return(data[6],data[7],data[8])

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
    f.write("Time, Temperature, Humidity, Pressure, PM1, PM2.5, PM10 \n")
    f.close()
    
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
            pm1, pm25, pm10 = read_pms5003()
            timestring="%04d-%02d-%02d %02d:%02d:%02d"%(timestamp[0:3] +
                                                timestamp[4:7])
            file.write(
                    timestring + ","
                    + str(bme280.temperature)
                    + "," + str(bme280.humidity)
                    + "," + str(bme280.pressure)
                    + "," + str(pm1)
                    + "," + str(pm25)
                    + "," + str(pm10)
                    +"\n")
            print("writing data")
    
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)
    
    time.sleep(10)

