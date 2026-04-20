import time
from pattern_base import BasePattern


class Pattern(BasePattern):
    """Cycle through red, green, and gold like ornaments."""
    name = "ornament"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        colors = [(255, 0, 0), (0, 255, 0), (255, 215, 0)]
        index = 0
        while not self.stop:
            r, g, b = colors[index]
            for i in range(num_leds):
                strip[i] = apply_brightness(r, g, b)
            strip.write()
            index = (index + 1) % len(colors)
            time.sleep(0.5 * factor)
            if self.stop:
                break
