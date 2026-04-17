from gpiozero import Button
import time

button = Button(3)

while True:
    time.sleep(0.1)
    if button.is_pressed:
        print("Button pressed!")