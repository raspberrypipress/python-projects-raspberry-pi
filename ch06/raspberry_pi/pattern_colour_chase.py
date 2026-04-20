import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Simple colour chasing effect."""
    name = "colour_chase"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        colors = colours
        while not self.stop:
            for c in colors:
                for i in range(num_leds):
                    if self.stop:
                        return
                    strip[i] = apply_brightness(*c)
                    if i > 0:
                        strip[i - 1] = apply_brightness(0, 0, 0)
                    strip.write()
                    time.sleep(0.05 * factor)
                    if self.stop:
                        return
                strip[num_leds - 1] = apply_brightness(0, 0, 0)
                strip.write()
