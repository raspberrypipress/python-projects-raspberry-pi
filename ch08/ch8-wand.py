import emlearn_trees
import array
import gc
import _thread
from time import sleep, ticks_ms
import board
import busio
import adafruit_lsm303_accel
import adafruit_lis2mdl
import neopixel
from led_helpers import hsv_to_rgb, sparkle

run_sparkle = False
np = neopixel.NeoPixel(machine.Pin(2), 10)

def core1_loop():
    global run_sparkle, np
    while True:
        while not run_sparkle:
            sleep(0.1)
        sparkle(np,10,7,3,5,0.9)
        run_sparkle = False

_thread.start_new_thread(core1_loop, ())

i2c = busio.I2C(board.GP17, board.GP16)
mag = adafruit_lis2mdl.LIS2MDL(i2c)
accel = adafruit_lsm303_accel.LSM303_Accel(i2c)

print("loading model")
model = emlearn_trees.new(300, 10000, 200)

with open('flick_model.csv', 'r') as f:
    emlearn_trees.load_model(model, f)

resout = array.array('f',[0,0])

window  =[]
for i in range(10):
    window.append(array.array('h',[0]*30))

print("running")
while True:
    for i in range(10):
        reading = accel.acceleration
        for j in range(10):
            window[i][(i+j)%10] = int(reading[0]*1000)
            window[i][(i+j)%10+10] = int(reading[1]*1000)
            window[i][(i+j)%10+20] = int(reading[2]*1000)
        sleep(0.1)
        model.predict(window[i], resout)
        if(resout[1] > 0.40):
            print("flick detected at ", ticks_ms())
            run_sparkle = True
