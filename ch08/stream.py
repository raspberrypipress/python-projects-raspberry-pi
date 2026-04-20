from time import sleep, ticks_ms
import board
import busio
import adafruit_lsm303_accel
import adafruit_lis2mdl
import machine

button = machine.Pin(0, machine.Pin.IN, machine.Pin.PULL_UP)

i2c = busio.I2C(board.GP17, board.GP16)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

while True:
    print(
        ticks_ms(),
        accel.acceleration[0],
        accel.acceleration[1],
        accel.acceleration[2],
        button.value(), 
        sep=",")
    sleep(0.1)