import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Single comet with fading tail."""
    name = "comet"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        position = 0
        direction = 1
        tail = max(0, 10 * size // 100)
        r0, g0, b0 = colours[0] if colours else (255, 255, 255)
        while not self.stop:
            for i in range(num_leds):
                if tail > 0:
                    dist = abs(i - position)
                    if dist < tail:
                        brightness = max(0, 255 - (255 // tail) * dist)
                        r = r0 * brightness // 255
                        g = g0 * brightness // 255
                        b = b0 * brightness // 255
                    else:
                        r = g = b = 0
                else:
                    r = g = b = 0
                strip[i] = apply_brightness(r, g, b)
            strip.write()
            if tail > 0:
                position += direction
                if position >= num_leds - 1 or position <= 0:
                    direction *= -1
            time.sleep(0.05 * factor)
            if self.stop:
                break
