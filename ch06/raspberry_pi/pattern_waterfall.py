import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Waterfall-like flow of blue light."""
    name = "waterfall"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import random
        pixels = []
        while not self.stop:
            pixels.insert(0, (0, 0, random.randint(100, 255)))
            if len(pixels) > num_leds:
                pixels.pop()
            for i, (r, g, b) in enumerate(pixels):
                strip[i] = apply_brightness(r, g, b)
            strip.write()
            time.sleep(0.05 * factor)


