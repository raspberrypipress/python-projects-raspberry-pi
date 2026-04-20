from flask import Flask, render_template, request, jsonify
import threading
import json
import glob
import importlib.util
import os

from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
from pattern_base import BasePattern

app = Flask(__name__)

STATE_FILE = "state.json"
pattern = "rainbow_fade"

num_leds = 100
max_brightness = 100
speed = 50
size = 100
colours = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ffffff"]

current_leds = []


class SpeedEvent:
    def __init__(self, speed: int):
        self.speed = speed
        self._event = threading.Event()

    def set(self):
        self._event.set()

    def is_set(self):
        return self._event.is_set()

    def clear(self):
        self._event.clear()

    def wait(self, timeout=None):
        return self._event.wait(timeout)


def load_state():
    global num_leds, max_brightness, colours, speed, size

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            num_leds = data.get("num_leds", num_leds)
            max_brightness = data.get("max_brightness", max_brightness)
            colours = data.get("colours", colours)
            speed = data.get("speed", speed)
            size = data.get("size", size)


def save_state():
    data = {
        "num_leds": num_leds,
        "max_brightness": max_brightness,
        "colours": colours,
        "speed": speed,
        "size": size,
    }
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


def load_external_patterns():
    for path in glob.glob("pattern_*.py"):
        module_name = os.path.splitext(os.path.basename(path))[0]
        if module_name in loaded_patterns:
            continue
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"Error loading {path}: {e}")
            continue
        if hasattr(module, "Pattern") and issubclass(module.Pattern, BasePattern):
            obj = module.Pattern()
            name = getattr(obj, "name", module_name.replace("pattern_", ""))
            loaded_patterns[name] = obj


def color_to_hex(color) -> str:
    try:
        r, g, b = color.r, color.g, color.b  # type: ignore
    except Exception:
        if isinstance(color, (tuple, list)) and len(color) >= 3:
            r, g, b = color[0], color[1], color[2]
        elif isinstance(color, int):
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
        else:
            r = g = b = 0
    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"


class RecordingStrip:
    def __init__(self, real_strip, led_count: int):
        self.real_strip = real_strip
        self.colors = ["#000000"] * led_count

    def __setitem__(self, idx: int, color):
        if 0 <= idx < len(self.colors):
            self.colors[idx] = color_to_hex(color)
        if self.real_strip is not None:
            self.real_strip[idx] = color

    def write(self):
        if self.real_strip is not None:
            self.real_strip.write()


def apply_brightness(r, g, b):
    scale = max_brightness / 100.0
    return Color(int(r * scale), int(g * scale), int(b * scale))


def hex_to_rgb(value):
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def setup_strip():
    global strip, current_leds
    real_strip = WS2812SpiDriver(
        spi_bus=0, spi_device=0, led_count=num_leds
    ).get_strip()
    strip = RecordingStrip(real_strip, num_leds)
    current_leds = strip.colors


def start_pattern():
    global pattern_thread, stop_event, last_run_error
    if strip is None or paused:
        return
    if pattern_thread and pattern_thread.is_alive():
        stop_event.set()
        pattern_thread.join()
    stop_event = SpeedEvent(speed)
    colour_values = [hex_to_rgb(c) for c in colours]
    if pattern in loaded_patterns:
        target = loaded_patterns[pattern].run
        args = (
            strip,
            num_leds,
            stop_event,
            apply_brightness,
            colour_values,
            speed,
            size,
        )
    else:
        target = pattern_funcs.get(pattern)
        args = (stop_event,)
    if target:
        def run_wrapper():
            global last_run_error
            try:
                target(*args)
            except Exception as e:
                last_run_error = str(e)

        last_run_error = None
        pattern_thread = threading.Thread(target=run_wrapper)
        pattern_thread.daemon = True
        pattern_thread.start()


def pause_pattern():
    global paused, pattern_thread, stop_event
    if pattern_thread and pattern_thread.is_alive():
        stop_event.set()
        pattern_thread.join()
    paused = True


def resume_pattern():
    global paused
    paused = False
    start_pattern()


@app.route("/led_state")
def led_state():
    return jsonify({"leds": current_leds})


@app.route("/", methods=["GET", "POST"])
def home():
    global num_leds, max_brightness, paused, colours, speed, size

    # Reload external patterns without exposing any errors on the page.
    # Any issues will simply be logged to the server's console.
    load_external_patterns()

    prev_num_leds = num_leds
    prev_brightness = max_brightness
    prev_colours = colours.copy()
    prev_speed = speed
    prev_size = size

    if request.method == "POST":
        if "pause" in request.form:
            pause_pattern()
        elif "resume" in request.form:
            resume_pattern()
        else:
            if "num_leds" in request.form and request.form["num_leds"]:
                num_leds = int(request.form["num_leds"])
            if "max_brightness" in request.form:
                max_brightness = int(request.form["max_brightness"])
            if "speed" in request.form:
                speed = int(request.form["speed"])
            if "size" in request.form:
                size = int(request.form["size"])
            if "colour0" in request.form:
                for i in range(5):
                    key = f"colour{i}"
                    if key in request.form:
                        colours[i] = request.form[key]

    if num_leds != prev_num_leds:
        setup_strip()
        if not paused:
            start_pattern()
        save_state()
    elif (
        max_brightness != prev_brightness
        or speed != prev_speed
        or size != prev_size
    ):
        if not paused:
            start_pattern()
        save_state()
    elif colours != prev_colours:
        if not paused:
            start_pattern()
        save_state()

    return render_template(
        "basic_start_more.html",
        num_leds=num_leds,
        max_brightness=max_brightness,
        speed=speed,
        size=size,
        paused=paused,
        colours=colours,
    )


load_state()
strip = None
pattern_thread = None
stop_event = SpeedEvent(speed)
paused = False
last_run_error = None
pattern_funcs = {}
loaded_patterns = {}

setup_strip()
load_external_patterns()
start_pattern()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
