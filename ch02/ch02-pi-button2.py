from gpiozero import DigitalInputDevice
import time

button = DigitalInputDevice(3, pull_up=True)

while True:
    time.sleep(0.1)
    if button.value:
        print("Button pressed!")