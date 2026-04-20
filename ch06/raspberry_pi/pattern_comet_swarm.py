import time
from pattern_base import BasePattern

class Pattern(BasePattern):
    """Multiple random moving coloured blocks that fade out."""
    name = "comet_swarm"

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        if strip is None:
            return
        factor = max(0.01, (100 - speed) / 50)
        import random
        block_len = max(1, size // 20 + 1)
        blocks = []
        while not self.stop:
            for i in range(num_leds):
                strip[i] = apply_brightness(0, 0, 0)
            if random.random() < 0.2:
                colour = random.choice(colours) if colours else (255, 255, 255)
                pos = random.randint(0, num_leds - 1)
                direction = random.choice([-1, 1])
                blocks.append({"pos": pos, "dir": direction, "colour": colour, "life": 255})
            new_blocks = []
            for blk in blocks:
                r0, g0, b0 = blk["colour"]
                life = blk["life"]
                for j in range(block_len):
                    p = blk["pos"] + j * blk["dir"]
                    if 0 <= p < num_leds:
                        r = r0 * life // 255
                        g = g0 * life // 255
                        b = b0 * life // 255
                        strip[int(p)] = apply_brightness(r, g, b)
                blk["pos"] += blk["dir"]
                blk["life"] -= 15
                if blk["life"] > 0 and -block_len < blk["pos"] < num_leds + block_len:
                    new_blocks.append(blk)
            blocks = new_blocks
            strip.write()
            time.sleep(0.05 * factor)
            if self.stop:
                break

