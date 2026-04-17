from gpiozero import PWMLED
from signal import pause
led = PWMLED(2)
led.pulse()
pause()