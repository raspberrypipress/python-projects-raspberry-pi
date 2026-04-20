import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Random twinkling stars."""
    name = "twinkle"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import random
        levels = [0] * num_leds
        colors_for_led = [(0, 0, 0)] * num_leds
        color_choices = colours[:5] if colours else []
        while not self.stop:
            for i in range(num_leds):
                if levels[i] == 0 and random.random() < 0.05:
                    levels[i] = 255
                    if color_choices:
                        colors_for_led[i] = random.choice(color_choices)
                    else:
                        colors_for_led[i] = (
                            random.randint(0, 255),
                            random.randint(0, 255),
                            random.randint(0, 255),
                        )
                if levels[i] > 0:
                    r, g, b = colors_for_led[i]
                    r = int(r * levels[i] / 255)
                    g = int(g * levels[i] / 255)
                    b = int(b * levels[i] / 255)
                    strip[i] = apply_brightness(r, g, b)
                    levels[i] = max(0, levels[i] - 25)
                else:
                    strip[i] = apply_brightness(0, 0, 0)
            strip.write()
            time.sleep(0.05 * factor)
            if self.stop:
                break
