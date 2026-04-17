from gpiozero import LED
from signal import pause
led = LED(2)
led.blink()
pause()