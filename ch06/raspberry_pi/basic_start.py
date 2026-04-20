from flask import Flask, render_template, request
import glob
import importlib.util
import os
import threading

from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
from pattern_base import BasePattern

app = Flask(__name__)

pattern = "rainbow_fade"
num_leds = 100
max_brightness = 100
speed = 50
size = 100

# Default colours as RGB tuples
colours = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 255, 255),
]

strip = None
loaded_patterns = {}
pattern_thread = None
stop_event = threading.Event()


def load_patterns():
    """Load pattern classes from pattern_*.py files."""
    for path in glob.glob("pattern_*.py"):
        module_name = os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "Pattern") and issubclass(module.Pattern, BasePattern):
            obj = module.Pattern()
            name = getattr(obj, "name", module_name.replace("pattern_", ""))
            loaded_patterns[name] = obj


def apply_brightness(r, g, b):
    """Scale an RGB tuple based on the current maximum brightness."""
    scale = max_brightness / 100.0
    return Color(int(r * scale), int(g * scale), int(b * scale))


def setup_strip():
    """Initialise the LED strip for the current number of LEDs."""
    global strip
    strip = WS2812SpiDriver(spi_bus=0, spi_device=0, led_count=num_leds).get_strip()


def start_pattern():
    """Stop the current pattern and start the selected one."""
    global pattern_thread, stop_event
    if strip is None:
        return
    if pattern_thread and pattern_thread.is_alive():
        stop_event.set()
        pattern_thread.join()
    stop_event = threading.Event()
    if pattern in loaded_patterns:
        obj = loaded_patterns[pattern]
        args = (strip, num_leds, stop_event, apply_brightness, colours, speed, size)
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
