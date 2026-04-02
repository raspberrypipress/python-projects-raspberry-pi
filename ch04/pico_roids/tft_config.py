from machine import Pin, SPI
import st7789py as st7789

TFA = 0
BFA = 80
WIDE = 1
TALL = 0
SCROLL = 0      # orientation for scroll.py
FEATHERS = 1    # orientation for feathers.py

def config(rotation=0):
    """
    Configures and returns an instance of the ST7789 display driver.

    Args:
        rotation (int): The rotation of the display. Defaults to 0.

    Returns:
        ST7789: An instance of the ST7789 display driver.
    """

    return st7789.ST7789(
        SPI(0, baudrate=75_000_000, polarity=1, sck=Pin(2), mosi=Pin(3),  miso=None),
        240,
        240,
        reset=Pin(4, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(6, Pin.OUT),
        backlight=Pin(7, Pin.OUT),
        rotation=rotation,
    )

