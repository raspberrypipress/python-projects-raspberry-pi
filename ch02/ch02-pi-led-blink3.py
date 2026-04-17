from gpiozero import LED
from time import sleep

led = LED(2)

while True:
    sleep(1)
    led.toggle()