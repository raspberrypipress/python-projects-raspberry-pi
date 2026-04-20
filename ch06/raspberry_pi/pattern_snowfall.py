import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Falling snowflake simulation."""
    name = "snowfall"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import random
        flakes = []
        while not self.stop:
            for i in range(num_leds):
                strip[i] = apply_brightness(0, 0, 0)
            if random.random() < 0.3:
                flakes.append(0)
            new_flakes = []
            for f in flakes:
                if f < num_leds:
                    strip[int(f)] = apply_brightness(255, 255, 255)
                    new_flakes.append(f + 1)
            flakes = new_flakes
            strip.write()
            time.sleep(0.1 * factor)
            if self.stop:
                break
