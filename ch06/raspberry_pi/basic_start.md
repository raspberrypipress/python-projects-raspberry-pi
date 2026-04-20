# `basic_start.py` Detailed Overview

`basic_start.py` exposes a small Flask site for selecting LED patterns and manages the hardware that drives the strip. Below is a line‑by‑line walkthrough of the script's behaviour.

## Global configuration
- `pattern` – name of the currently selected pattern; defaults to `"rainbow_fade"`.
- `num_leds` – number of LEDs on the strip, initially `100`.
- `max_brightness` – brightness percentage used to scale RGB values.
- `strip` – handle to the WS2812 strip obtained from the SPI driver.
- `loaded_patterns` – dictionary mapping pattern names to their `Pattern` objects.
- `pattern_thread` – background thread running the current pattern.
- `stop_event` – `threading.Event` used to signal a pattern to finish before another starts.

## Loading pattern modules
`load_patterns()` searches the working directory for modules named `pattern_*.py`. For each file it:
1. Loads the module with `importlib.util`.
2. Instantiates its `Pattern` class if present.
3. Records the instance in `loaded_patterns` under either the object's `name` attribute or the filename with the `pattern_` prefix removed.

This allows new pattern modules to be dropped into the directory without modifying `basic_start.py`.

## Brightness scaling
`apply_brightness(r, g, b)` converts a raw RGB triple into a `Color` understood by the `WS2812SpiDriver`. The function:
1. Calculates a scaling factor from `max_brightness`.
2. Multiplies each component and casts to `int` to avoid floats.
3. Returns a `Color` object that the driver can transmit to the LEDs.

## LED strip initialisation
`setup_strip()` configures the `WS2812SpiDriver` for the current `num_leds` using SPI bus 0 and device 0. The driver's `get_strip()` method produces an object stored in the global `strip` variable; subsequent pattern functions operate on this object.

## Starting and stopping patterns
`start_pattern()` performs coordinated pattern switching:
1. If a pattern thread is active, `stop_event` is set and the thread is joined, giving the running pattern a chance to exit gracefully.
2. A fresh `Event` is created for the next pattern.
3. The selected pattern object is retrieved from `loaded_patterns`.
4. A daemon thread is spawned to run the object's `run` method. Arguments include the LED `strip`, `num_leds`, the `stop_event`, `apply_brightness`, an empty colour palette, and two timing values (`50` and `100`) which patterns may interpret as delays.

Using a daemon thread ensures the program can exit even if a pattern does not terminate on its own.

## Flask web interface
The `/` route is defined by `index()` and serves `templates/start.html`:
- **GET requests** display a form listing available patterns and the current LED count.
- **POST requests** update the chosen pattern and LED count based on form data. The function validates the LED number, calls `setup_strip()` to reconfigure the driver, and then `start_pattern()` to launch the new pattern. Invalid input produces an error message displayed on the page.

The template receives the sorted pattern names, the active pattern, the LED count, and any error string.

## Program start‑up
When the module is executed directly, the following sequence runs:
1. `load_patterns()` discovers all pattern modules.
2. `setup_strip()` prepares the driver with the default LED count.
3. `start_pattern()` launches the default pattern in a background thread.
4. `app.run(host="0.0.0.0", port=5000)` starts the Flask development server so the interface is reachable on the local network.

Together these steps allow the script to automatically load available animations and present a web UI for managing them without further configuration.
