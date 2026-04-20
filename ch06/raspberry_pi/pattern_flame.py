import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Flickering orange flame effect."""
    name = "flame"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import random
        while not self.stop:
            for i in range(num_leds):
                r = random.randint(150, 255)
                g = random.randint(0, 100)
                b = 0
                strip[i] = apply_brightness(r, g, b)
            strip.write()
            time.sleep(0.05 * factor)
            if self.stop:
                break
