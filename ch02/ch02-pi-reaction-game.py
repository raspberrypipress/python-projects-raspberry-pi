from gpiozero import Button, LED
import time
from random import uniform

button = Button(3)
led = LED(2)

random_time = uniform(3, 7)
time.sleep(random_time)

start_time = time.monotonic()
led.value = True
button.wait_for_press()
print("your reaction time is: ", (time.monotonic()-start_time))