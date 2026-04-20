from flask import Flask, render_template, request
import os
import threading

from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
from pattern_base import BasePattern

app = Flask(__name__)

# Default configuration values
pattern = "rainbow_fade"
num_leds = 100
max_brightness = 100
speed = 50
size = 100

colours = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 255, 255),
]

# Global state for pattern control
strip = None
loaded_patterns = {}
pattern_thread = None
active_pattern = None

def load_patterns() -> None:
    """Load pattern classes from pattern_*.py files."""
    for filename in os.listdir():
        if filename.startswith("pattern_") and filename.endswith(".py"):
            module_name = filename[:-3]
            module = __import__(module_name)
            if hasattr(module, "Pattern") and issubclass(module.Pattern, BasePattern):
                obj = module.Pattern()
                name = getattr(obj, "name", module_name.replace("pattern_", ""))
                loaded_patterns[name] = obj

def apply_brightness(r: int, g: int, b: int):
    """Scale an RGB tuple based on the current maximum brightness."""
    scale = max_brightness / 100.0
    return Color(int(r * scale), int(g * scale), int(b * scale))


class StripWrapper:
    """Provide list-like access to the underlying LED strip.

    The WS2812 driver exposes a strip object that only supports setting
    colours via ``set_pixel_color``.  Many of the pattern scripts expect to
    assign colours using item notation (``strip[i] = color``).  This small
    wrapper bridges the two behaviours by forwarding item assignments to the
    driver's ``set_pixel_color`` method while also exposing ``write`` so that
    patterns can flush updates to the LEDs.
    """

    def __init__(self, real_strip):
        self._strip = real_strip

    def __setitem__(self, idx: int, color) -> None:
        self._strip.set_pixel_color(idx, color)

    def write(self) -> None:
        # The underlying driver uses ``write`` to push the pixel data.  If a
        # different method name is used, fall back gracefully.
        if hasattr(self._strip, "write"):
            self._strip.write()
        elif hasattr(self._strip, "show"):
            self._strip.show()

def setup_strip(spi_bus: int = 0, spi_device: int = 0) -> None:
    """Initialise the LED strip for the current number of LEDs."""
    global strip
    driver = WS2812SpiDriver(
        spi_bus=spi_bus, spi_device=spi_device, led_count=num_leds
    )
    strip = StripWrapper(driver.get_strip())

def start_pattern() -> None:
    """Stop the current pattern and start the selected one."""
    global pattern_thread, active_pattern
    if strip is None:
        return
    if pattern_thread and pattern_thread.is_alive():
        if active_pattern is not None:
            active_pattern.stop = True
        pattern_thread.join()
    if pattern in loaded_patterns:
        obj = loaded_patterns[pattern]
        obj.stop = False
        active_pattern = obj
        args = (strip, num_leds, apply_brightness, colours, speed, size)
        pattern_thread = threading.Thread(target=obj.run, args=args)
        pattern_thread.daemon = True
        pattern_thread.start()

@app.route("/", methods=["GET", "POST"])
def index():
    """Render the start page and handle pattern selection."""
    global pattern, num_leds
    error = None
    if request.method == "POST":
        pattern = request.form.get("pattern", pattern)
        try:
            num_leds = int(request.form.get("num_leds", num_leds))
            setup_strip()
            start_pattern()
        except ValueError:
            error = "Invalid number of LEDs"
    return render_template(
        "start.html",
        patterns=sorted(loaded_patterns.keys()),
        current_pattern=pattern,
        num_leds=num_leds,
        error=error,
    )

if __name__ == "__main__":
    load_patterns()
    setup_strip()
    start_pattern()
    app.run(host="0.0.0.0", port=5000)
