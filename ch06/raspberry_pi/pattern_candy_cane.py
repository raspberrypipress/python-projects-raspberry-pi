import time
from pattern_base import BasePattern


class Pattern(BasePattern):
    """Red and white moving candy cane stripes."""
    name = "candy_cane"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        offset = 0
        while not self.stop:
            for i in range(num_leds):
                if (i + offset) % 2 == 0:
                    strip[i] = apply_brightness(255, 0, 0)
                else:
                    strip[i] = apply_brightness(255, 255, 255)
            strip.write()
            offset = (offset + 1) % 2
            time.sleep(0.2 * factor)
            if self.stop:
                break
