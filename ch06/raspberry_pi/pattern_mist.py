import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Soft, slow-changing mist effect."""
    name = "mist"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import random
        active_leds = max(0, min(num_leds, num_leds * size // 100))
        levels = [0] * num_leds
        r0, g0, b0 = colours[0] if colours else (80, 80, 80)
        while not self.stop:
            active_set = (
                set(random.sample(range(num_leds), active_leds)) if active_leds > 0 else set()
            )
            for i in range(num_leds):
                if i in active_set:
                    levels[i] = min(80, levels[i] + random.randint(5, 15))
                else:
                    levels[i] = max(0, levels[i] - random.randint(5, 15))
                r = r0 * levels[i] // 80
                g = g0 * levels[i] // 80
                b = b0 * levels[i] // 80
                strip[i] = apply_brightness(r, g, b)
            strip.write()
            time.sleep(0.1 * factor)
            if self.stop:
                break
