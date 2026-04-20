import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Multiple balls bouncing back and forth."""
    name = "bouncing_balls"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import random
        ball_count = 3
        positions = [random.uniform(0, num_leds - 1) for _ in range(ball_count)]
        velocities = [random.choice([-0.5, 0.5]) for _ in range(ball_count)]
        colors = colours
        while not self.stop:
            for i in range(num_leds):
                strip[i] = apply_brightness(0, 0, 0)
            for idx in range(ball_count):
                positions[idx] += velocities[idx]
                if positions[idx] < 0 or positions[idx] >= num_leds:
                    velocities[idx] *= -1
                    positions[idx] = max(0, min(num_leds - 1, positions[idx]))
                r, g, b = colors[idx % len(colors)]
                strip[int(positions[idx])] = apply_brightness(r, g, b)
            strip.write()
            time.sleep(0.05 * factor)
            if self.stop:
                break
