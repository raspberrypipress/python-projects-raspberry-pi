# MicroPython version of basic_start.py for Raspberry Pi Pico 2 W
# Uses the microdot framework and NeoPixel driver for WS2812 LEDs.

from microdot.microdot import Microdot, Response
from microdot.utemplate import Template
import os
import time
import _thread
from machine import Pin
from neopixel import NeoPixel
import network
from pattern_base import BasePattern
from secrets import secrets

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets['ssid'], secrets['password'])

# Wait for connect or fail
max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

# Handle connection error
if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )
    
    
app = Microdot()
Response.default_content_type = 'text/html'

# Default configuration values
pattern = 'rainbow_fade'
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
thread_running = False
current_pattern = None


def load_patterns() -> None:
    """Load pattern classes from pattern_*.py files."""
    print(os.listdir())
    for filename in os.listdir():
        if filename.startswith('pattern_') and filename.endswith('.py'):
            print(filename)
            module_name = filename[:-3]
            module = __import__(module_name)
            if hasattr(module, 'Pattern') and issubclass(module.Pattern, BasePattern):
                obj = module.Pattern()
                name = getattr(obj, 'name', module_name.replace('pattern_', ''))
                loaded_patterns[name] = obj


def apply_brightness(r: int, g: int, b: int):
    """Scale an RGB tuple based on the current maximum brightness."""
    scale = max_brightness / 100.0
    return int(r * scale), int(g * scale), int(b * scale)


def setup_strip(pin: int = 0) -> None:
    """Initialise the LED strip for the current number of LEDs."""
    global strip
    strip = NeoPixel(Pin(pin, Pin.OUT), num_leds)


def connect_wifi(ssid: str, password: str):
    """Connect to a Wi-Fi network and return the active WLAN interface."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(ssid, password)
        # Wait for connection with a simple timeout
        for _ in range(20):
            if wlan.isconnected():
                break
            print("waiting for connection...")
            time.sleep_ms(500)
    if not wlan.isconnected():
        raise RuntimeError("Failed to connect to Wi-Fi")
    print("network config:", wlan.ifconfig())
    return wlan


def _pattern_runner(target, args):
    global thread_running
    target(*args)
    thread_running = False


def start_pattern() -> None:
    """Stop the current pattern and start the selected one."""
    global thread_running, current_pattern
    if strip is None:
        return
    if thread_running and current_pattern is not None:
        current_pattern.stop = True
        while thread_running:
            time.sleep_ms(50)
    if pattern in loaded_patterns:
        obj = loaded_patterns[pattern]
        obj.stop = False
        current_pattern = obj
        args = (strip, num_leds, apply_brightness, colours, speed, size)
        thread_running = True
        _thread.start_new_thread(_pattern_runner, (obj.run, args))


@app.route('/', methods=['GET', 'POST'])
def index(request):
    """Render the start page and handle pattern selection."""
    global pattern, num_leds
    if request.method == 'POST':
        pattern = request.form.get('pattern')
        try:
            num_leds = int(request.form.get('num_leds'))
            setup_strip()
            start_pattern()
        except Exception:  # ValueError or TypeError
            error = 'Invalid number of LEDs'
    return Template(
        'start_mp.html'
    ).render(patterns=sorted(loaded_patterns.keys()),
        current_pattern=pattern,
        num_leds=num_leds)

load_patterns()
setup_strip()
start_pattern()
app.run(port=80)


