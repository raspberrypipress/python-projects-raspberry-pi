import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Smooth aurora-like colour waves."""
    name = "aurora"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import math

        color = colours[0] if colours else (80, 255, 255)
        r_amp, g_amp, b_amp = color

        offset = 0
        while not self.stop:
            for i in range(num_leds):
                angle = (i + offset) / num_leds * 2 * math.pi
                r = int((math.sin(angle) + 1) / 2 * r_amp)
                g = int((math.sin(angle + 2) + 1) / 2 * g_amp)
                b = int((math.sin(angle + 4) + 1) / 2 * b_amp)
                strip[i] = apply_brightness(r, g, b)
            strip.write()
            offset += 1
            time.sleep(0.05 * factor)
            if self.stop:
                break
