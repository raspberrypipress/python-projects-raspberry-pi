from flask import Flask, render_template, request, redirect, url_for, abort, jsonify, Response
from flask_login import (
    LoginManager,
    UserMixin,
    login_required,
    login_user,
    logout_user,
)
import threading
import time
import json
import glob
import importlib.util

import os
import sys

from rpi5_ws2812.ws2812 import Color, WS2812SpiDriver
from pattern_base import BasePattern



app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-me")

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, username: str):
        self.id = username


USERS = {
    os.environ.get("APP_USERNAME", "admin"): os.environ.get(
        "APP_PASSWORD", "password"
    )
}


@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None


STATE_FILE = "state.json"
PRESET_DIR = "presets"

pattern = "rainbow_fade"

num_leds = 100
max_brightness = 100
speed = 50
size = 100

# Default colours (hex strings) for user selection
colours = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ffffff"]

# Holds the colours the strip is currently set to display
current_leds = []


def load_state():
    global pattern, num_leds, max_brightness, colours, speed, size

    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
            pattern = data.get("pattern", pattern)
            num_leds = data.get("num_leds", num_leds)
            max_brightness = data.get("max_brightness", max_brightness)
            colours = data.get("colours", colours)
            speed = data.get("speed", speed)
            size = data.get("size", size)


def save_state():
    data = {
        "pattern": pattern,
        "num_leds": num_leds,
        "max_brightness": max_brightness,
        "colours": colours,
        "speed": speed,
        "size": size,
    }
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


def _preset_path(name: str) -> str:
    """Return the filesystem path for a preset name."""
    safe_name = os.path.basename(name)
    return os.path.join(PRESET_DIR, f"{safe_name}.json")


def list_presets():
    """Return a list of available preset names."""
    if not os.path.isdir(PRESET_DIR):
        return []
    return [
        os.path.splitext(os.path.basename(p))[0]
        for p in glob.glob(os.path.join(PRESET_DIR, "*.json"))
    ]


def save_preset(name: str):
    """Save the current state to a preset file."""
    os.makedirs(PRESET_DIR, exist_ok=True)
    path = _preset_path(name)
    data = {
        "pattern": pattern,
        "num_leds": num_leds,
        "max_brightness": max_brightness,
        "colours": colours,
        "speed": speed,
        "size": size,
    }
    with open(path, "w") as f:
        json.dump(data, f)


def load_preset(name: str):
    """Load state values from a preset file and apply them."""
    global pattern, num_leds, max_brightness, colours, speed, size
    path = _preset_path(name)
    with open(path, "r") as f:
        data = json.load(f)
    pattern = data.get("pattern", pattern)
    num_leds = data.get("num_leds", num_leds)
    max_brightness = data.get("max_brightness", max_brightness)
    colours = data.get("colours", colours)
    speed = data.get("speed", speed)
    size = data.get("size", size)
    setup_strip()
    if not paused:
        start_pattern()
    save_state()


def delete_preset(name: str):
    """Remove a preset file if it exists."""
    path = _preset_path(name)
    if os.path.exists(path):
        os.remove(path)


load_state()

strip = None
pattern_thread = None
active_pattern = None
paused = False
# Holds the last runtime error from a pattern, if any
last_run_error = None

# dictionary for dynamically loaded pattern implementations
loaded_patterns = {}


def load_external_patterns():
    """Discover and load pattern classes from pattern_*.py files.

    Returns a list of error strings for any files that could not be loaded.
    """
    errors = []
    for path in glob.glob("pattern_*.py"):
        module_name = os.path.splitext(os.path.basename(path))[0]
        if module_name in loaded_patterns:
            # already loaded
            continue
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            errors.append(f"Error loading {path}: {e}")
            continue
        if hasattr(module, "Pattern") and issubclass(module.Pattern, BasePattern):
            obj = module.Pattern()
            name = getattr(obj, "name", module_name.replace("pattern_", ""))
            loaded_patterns[name] = obj
    return errors


def color_to_hex(color) -> str:
    """Convert a colour representation to a '#RRGGBB' string."""
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
    """Wrapper around the real strip that records colours for display."""

    def __init__(self, real_strip, led_count: int):
        self.real_strip = real_strip
        self.colors = ["#000000"] * led_count

    def __setitem__(self, idx: int, color):
        if 0 <= idx < len(self.colors):
            self.colors[idx] = color_to_hex(color)
        if self.real_strip is not None:
            self.real_strip.set_pixel_color(idx,color)

    def write(self):
        if self.real_strip is not None:
            self.real_strip.show()


def apply_brightness(r, g, b):
    """Scale an RGB tuple based on the current maximum brightness."""
    scale = max_brightness / 100.0
    return Color(int(r * scale), int(g * scale), int(b * scale))


def hex_to_rgb(value):
    """Convert a hex colour string (e.g. '#ff0000') to an RGB tuple."""
    value = value.lstrip("#")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def setup_strip():
    """(Re)initialise the LED strip for the current number of LEDs."""
    global strip, current_leds
    real_strip = WS2812SpiDriver(
        spi_bus=0, spi_device=0, led_count=num_leds
    ).get_strip()
    strip = RecordingStrip(real_strip, num_leds)
    current_leds = strip.colors


def start_pattern():
    """Stop the current pattern (if any) and start the selected one."""
    global pattern_thread, active_pattern, last_run_error
    if strip is None or paused:
        return
    if pattern_thread and pattern_thread.is_alive():
        if active_pattern is not None:
            active_pattern.stop = True
        pattern_thread.join()
    colour_values = [hex_to_rgb(c) for c in colours]
    target = None
    args = ()
    if pattern in loaded_patterns:
        obj = loaded_patterns[pattern]
        obj.stop = False
        active_pattern = obj
        target = obj.run
        args = (strip, num_leds, apply_brightness, colour_values, speed, size)
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
    """Pause the current pattern by stopping its thread."""
    global paused, pattern_thread, active_pattern
    if pattern_thread and pattern_thread.is_alive():
        if active_pattern is not None:
            active_pattern.stop = True
        pattern_thread.join()
    paused = True


def resume_pattern():
    """Resume the current pattern if it was paused."""
    global paused
    paused = False
    start_pattern()


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if USERS.get(username) == password:
            login_user(User(username))
            return redirect(request.args.get("next") or url_for("home"))
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/led_state")
@login_required
def led_state():
    """Return the colours the LEDs should currently display."""
    return jsonify({"leds": current_leds})


@app.route("/presets/save", methods=["POST"])
@login_required
def save_preset_route():
    name = request.form.get("name", "").strip()
    if not name:
        abort(400)
    save_preset(name)
    return redirect(url_for("home"))


@app.route("/presets/load", methods=["POST"])
@login_required
def load_preset_route():
    name = request.form.get("name", "").strip()
    if not name:
        abort(400)
    try:
        load_preset(name)
    except FileNotFoundError:
        abort(404)
    return redirect(url_for("home"))


@app.route("/presets/delete", methods=["POST"])
@login_required
def delete_preset_route():
    name = request.form.get("name", "").strip()
    if not name:
        abort(400)
    delete_preset(name)
    return redirect(url_for("home"))


@app.route("/code")
@login_required
def generate_code():
    """Return a self-contained MicroPython script for the current pattern."""
    if pattern not in loaded_patterns:
        load_external_patterns()
    obj = loaded_patterns.get(pattern)
    if not obj:
        abort(404)
    module_name = obj.__class__.__module__
    pattern_path = f"{module_name}.py"
    try:
        with open("pattern_base.py", "r") as f:
            base_code = f.read()
        with open(pattern_path, "r") as f:
            pattern_code = f.read()
    except OSError:
        abort(404)
    pattern_code = pattern_code.replace("from pattern_base import BasePattern\n", "")
    colour_values = [hex_to_rgb(c) for c in colours]
    code_parts = [
        "import machine",
        "import neopixel",
        base_code,
        pattern_code,
        f"num_leds = {num_leds}",
        f"max_brightness = {max_brightness}",
        f"speed = {speed}",
        f"size = {size}",
        f"colours = {colour_values}",
        "",
        "def apply_brightness(r, g, b):",
        "    scale = max_brightness / 100.0",
        "    return int(r * scale), int(g * scale), int(b * scale)",
        "",
        "strip = neopixel.NeoPixel(machine.Pin(0), num_leds)",
        "Pattern().run(strip, num_leds, apply_brightness, colours, speed, size)",
    ]
    code = "\n".join(code_parts)
    return Response(code, mimetype="text/plain")

@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    global pattern, num_leds, max_brightness, paused, colours, speed, size

    errors = load_external_patterns()
    prev_pattern = pattern
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
            if "pattern" in request.form:
                pattern = request.form["pattern"]
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
        pattern != prev_pattern
        or max_brightness != prev_brightness
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

    pattern_options = list(loaded_patterns.keys())
    if pattern not in pattern_options:
        errors.append(
            f"Pattern '{pattern}' could not be loaded. Please select a different pattern."
        )
    return render_template(
        "main.html",
        pattern=pattern,
        num_leds=num_leds,
        max_brightness=max_brightness,
        speed=speed,
        size=size,
        paused=paused,
        pattern_options=pattern_options,
        presets=list_presets(),
        colours=colours,
        errors=errors,
    )



@app.route("/patterns")
@login_required
def list_patterns():
    files = [os.path.basename(p) for p in glob.glob("pattern_*.py")]
    return render_template("patterns.html", files=files)


@app.route("/patterns/new", methods=["GET", "POST"])
@login_required
def create_pattern_file():
    global pattern
    errors = []
    if request.method == "POST":
        filename = request.form.get("filename", "")
        safe_name = os.path.basename(filename)
        if not safe_name.startswith("pattern_"):
            safe_name = "pattern_" + safe_name
        if not safe_name.endswith(".py"):
            safe_name += ".py"
        if os.path.exists(safe_name):
            abort(400)
        content = request.form.get("content", "")
        with open(safe_name, "w") as f:
            f.write(content)
        action = request.form.get("action")
        if action == "Create and Run":
            module_name = os.path.splitext(safe_name)[0]
            if module_name in sys.modules:
                del sys.modules[module_name]
            for name, obj in list(loaded_patterns.items()):
                if obj.__class__.__module__ == module_name:
                    del loaded_patterns[name]
            errors = load_external_patterns()
            pattern_key = None
            for name, obj in loaded_patterns.items():
                if obj.__class__.__module__ == module_name:
                    pattern_key = name
                    break
            if not errors and pattern_key:
                pattern = pattern_key
                start_pattern()
                time.sleep(0.1)
                if last_run_error:
                    errors.append(f"Runtime error: {last_run_error}")
                save_state()
            return render_template(
                "create_pattern.html",
                filename=filename,
                content=content,
                errors=errors,
            )
        return redirect(url_for("list_patterns"))
    return render_template("create_pattern.html", errors=errors)


@app.route("/patterns/<path:filename>", methods=["GET", "POST"])
@login_required
def edit_pattern_file(filename):
    global pattern
    safe_name = os.path.basename(filename)
    if not safe_name.startswith("pattern_") or not safe_name.endswith(".py"):
        abort(404)
    path = safe_name
    if request.method == "POST":
        content = request.form.get("content", "")
        action = request.form.get("action")
        if action == "Save as New File":
            new_filename = request.form.get("new_filename", "")
            new_safe = os.path.basename(new_filename)
            if not new_safe:
                errors = ["New filename required"]
                return render_template(
                    "edit_pattern.html",
                    filename=safe_name,
                    content=content,
                    errors=errors,
                )
            if not new_safe.startswith("pattern_"):
                new_safe = "pattern_" + new_safe
            if not new_safe.endswith(".py"):
                new_safe += ".py"
            if os.path.exists(new_safe):
                errors = ["File already exists"]
                return render_template(
                    "edit_pattern.html",
                    filename=safe_name,
                    content=content,
                    errors=errors,
                )
            with open(new_safe, "w") as f:
                f.write(content)
            # Redirect to the editor for the newly created file so the user
            # can immediately continue editing it.  Use a 303 redirect to
            # ensure the subsequent request is a GET, avoiding resubmission
            # of the original form data.
            return redirect(
                url_for("edit_pattern_file", filename=new_safe), code=303
            )
        with open(path, "w") as f:
            f.write(content)
        module_name = os.path.splitext(safe_name)[0]
        for name, obj in list(loaded_patterns.items()):
            if obj.__class__.__module__ == module_name:
                del loaded_patterns[name]
        if action == "Save and Run":
            if module_name in sys.modules:
                del sys.modules[module_name]
            errors = load_external_patterns()
            pattern_key = None
            for name, obj in loaded_patterns.items():
                if obj.__class__.__module__ == module_name:
                    pattern_key = name
                    break
            if not errors and pattern_key:
                pattern = pattern_key
                start_pattern()
                time.sleep(0.1)
                if last_run_error:
                    errors.append(f"Runtime error: {last_run_error}")
                save_state()
            return render_template(
                "edit_pattern.html",
                filename=safe_name,
                content=content,
                errors=errors,
            )
        return redirect(url_for("list_patterns"))
    with open(path, "r") as f:
        content = f.read()
    return render_template(
        "edit_pattern.html", filename=safe_name, content=content, errors=[]
    )


setup_strip()
load_external_patterns()
start_pattern()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

