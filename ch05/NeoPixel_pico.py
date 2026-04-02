import array, time
from machine import Pin
import rp2

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 3
    T2 = 3
    T3 = 4
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()
    
#delay here is the reset time. You need a pause to reset the LED strip back to the initial LED
#however, if you have quite a bit of processing to do before the next time you update the strip
#you could put in delay=0 (or a lower delay)
class neopixel:
    def __init__(self, num_leds, state_machine, pin, delay=0.001):
        self.pixels = array.array("I", [0 for _ in range(num_leds)])
        self.sm = rp2.StateMachine(state_machine, ws2812, freq=8000000, sideset_base=Pin(pin))
        self.sm.active(1)
        self.num_leds = num_leds
        self.delay = delay
        self.brightnessvalue = 255

    def __setitem__(self, pixel_num, colour):
        # Adjust color values with brightnesslevel
        self.pixels[pixel_num] = colour[2] | colour[0] << 8 | colour[1] << 16

    def show(self):
        for i in range(self.num_leds):
            self.sm.put(self.pixels[i],8)
        time.sleep(self.delay)
        
if __name__ == "__main__":
    strip = neopixel(10,0,0)
    strip[0] = (100,0,0)
    strip[1] = (0,10,0)
    strip[2] = (0,0,100)
    strip.show()
    

