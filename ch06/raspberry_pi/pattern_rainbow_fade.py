import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Rainbow fade pattern loaded from an external file."""
    name = "rainbow_fade"

    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            r = pos * 3
            g = 255 - pos * 3
            b = 0
        elif pos < 170:
            pos -= 85
            r = 255 - pos * 3
            g = 0
            b = pos * 3
        else:
            pos -= 170
            r = 0
            g = pos * 3
            b = 255 - pos * 3
        return r, g, b

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        """Cycle smoothly through rainbow colours."""
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        while not self.stop:
            for j in range(256):
                if self.stop:
                    break
                for i in range(num_leds):
                    r, g, b = self.wheel((i + j) & 255)
                    strip[i] = apply_brightness(r, g, b)
                strip.write()
                time.sleep(0.02 * factor)
                if self.stop:
                    break
