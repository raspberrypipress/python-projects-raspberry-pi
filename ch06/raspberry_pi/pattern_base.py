"""Base class for LED strip patterns.

This project previously relied on :mod:`abc` to define an abstract base class
for patterns.  The patterns are straightforward, so a simple base class that
raises ``NotImplementedError`` is sufficient and avoids the additional
complexity of ``abc``.
"""


class BasePattern:
    """Base class for all LED strip patterns."""

    #: Optional human-readable name for the pattern
    name: str = "base"

    #: Flag to indicate the pattern should stop
    stop: bool = False

    def run(self, strip, num_leds, apply_brightness, colours, speed, size):
        """Run the pattern.

        Subclasses must implement this method to draw on ``strip`` using the
        provided parameters.
        """
        raise NotImplementedError("Subclasses must implement 'run'")
