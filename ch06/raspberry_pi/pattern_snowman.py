import time
from pattern_base import BasePattern


class Pattern(BasePattern):
    """Simple snowman made of three white sections with black eyes."""
    name = "snowman"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        section = num_leds // 3
        eyes = [section + section // 3, section + 2 * section // 3]
        while not self.stop:
            for i in range(num_leds):
                if i in eyes:
                    strip[i] = apply_brightness(0, 0, 0)
                else:
                    strip[i] = apply_brightness(255, 255, 255)
            strip.write()
            time.sleep(0.5 * factor)
            if self.stop:
                break
