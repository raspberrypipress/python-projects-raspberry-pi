from rp2 import PIO, StateMachine, asm_pio
from machine import Pin
import time

@asm_pio(set_init=PIO.OUT_LOW)
def led_off():
    set(pins, 0)
    
@asm_pio(set_init=PIO.OUT_LOW)
def led_on():
    set(pins, 1)
        
sm1 = StateMachine(1, led_off, freq=20000, set_base=Pin(25))
sm2 = StateMachine(2, led_on, freq=20002, set_base=Pin(25))
sm1.active(1)
sm2.active(1)
