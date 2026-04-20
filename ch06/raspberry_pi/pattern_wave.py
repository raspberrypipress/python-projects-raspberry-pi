import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Blue brightness sine wave."""
    name = "wave"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import math
        phase = 0
        while not self.stop:
            for i in range(num_leds):
                brightness = int((math.sin(2 * math.pi * (i / num_leds) + phase) + 1) / 2 * 255)
                strip[i] = apply_brightness(0, 0, brightness)
            strip.write()
            phase += 0.2
            time.sleep(0.05 * factor)
            if self.stop:
                break
