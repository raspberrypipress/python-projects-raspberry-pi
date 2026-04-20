import time
from pattern_base import BasePattern


class Pattern(BasePattern):
    """Green base with a twinkling yellow star."""
    name = "christmas_tree"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import random
        while not self.stop:
            for i in range(num_leds):
                strip[i] = apply_brightness(0, 255, 0)
            star = random.randint(0, num_leds - 1)
            strip[star] = apply_brightness(255, 255, 0)
            strip.write()
            time.sleep(0.5 * factor)
            if self.stop:
                break
