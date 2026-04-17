import machine
import time
from random import uniform
button = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)
led = machine.Pin(2, machine.Pin.OUT)

random_time = uniform(3, 7)
time.sleep(random_time)
start_time = time.ticks_ms()

led.value(1)

while button.value():
    pass

print("your reaction time is: ", (time.ticks_ms()-start_time)/1000)

led.value(0)