import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Random exploding fireworks."""
    name = "fireworks"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import random
        bursts = []
        color_choices = colours

        # Determine how many pixels should be lit at the peak of a burst. The
        # size parameter is a percentage, so use it to work out a number of
        # pixels relative to the total LED count. Ensure at least one pixel so
        # that the pattern still appears even for a size of 0.
        burst_pixels = max(1, num_leds * size // 100)

        while not self.stop:
            for i in range(num_leds):
                strip[i] = apply_brightness(0, 0, 0)

            # Randomly start a new burst. Each burst grows until it reaches a
            # radius that lights ``burst_pixels`` LEDs in total.
            if random.random() < 0.05:
                if color_choices:
                    color = random.choice(color_choices)
                else:
                    color = (
                        random.randint(0, 255),
                        random.randint(0, 255),
                        random.randint(0, 255),
                    )
                bursts.append(
                    {
                        "center": random.randint(0, num_leds - 1),
                        "radius": 0,
                        "color": color,
                        # Maximum radius based on desired number of lit pixels
                        "max_radius": max(1, (burst_pixels - 1) // 2),
                    }
                )

            new_bursts = []
            for b in bursts:
                step = max(1, 255 // (b["max_radius"] + 1))
                brightness = max(0, 255 - b["radius"] * step)
                for offset in range(-b["radius"], b["radius"] + 1):
                    pos = b["center"] + offset
                    if 0 <= pos < num_leds:
                        r, g, bc = b["color"]
                        r = int(r * brightness / 255)
                        g = int(g * brightness / 255)
                        bc = int(bc * brightness / 255)
                        strip[pos] = apply_brightness(r, g, bc)
                b["radius"] += 1
                if b["radius"] <= b["max_radius"]:
                    new_bursts.append(b)
            bursts = new_bursts
            strip.write()
            time.sleep(0.05 * factor)
            if self.stop:
                break
