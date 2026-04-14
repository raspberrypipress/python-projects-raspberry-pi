from ch03_pms5003 import read_pms5003, init_pms5003
import serial
import time

uart = serial.Serial('/dev/ttyUSB0')
init_pms5003(uart)

while True:
    time.sleep(5)
    pm1, pm25, pm10 = read_pms5003(uart)
    print("pm1: %d ug/m^3"% pm1)
    print("pm2.5: %d ug/m^3"% pm25)
    print("pm10: %d ug/m^3"% pm10)