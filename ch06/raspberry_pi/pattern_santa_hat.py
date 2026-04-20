import time
from pattern_base import BasePattern


class Pattern(BasePattern):
    """Red background with a white dot sliding like a Santa hat."""
    name = "santa_hat"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        pos = 0
        while not self.stop:
            for i in range(num_leds):
                color = (255, 0, 0) if i != pos else (255, 255, 255)
                strip[i] = apply_brightness(*color)
            strip.write()
            pos = (pos + 1) % num_leds
            time.sleep(0.1 * factor)
            if self.stop:
                break
