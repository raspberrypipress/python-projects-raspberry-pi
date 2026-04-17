import machine
import time

button = machine.Pin(3, machine.Pin.IN, machine.Pin.PULL_UP)

while True:
    if not button.value():
        print('Button pressed!')
        time.sleep(0.5)