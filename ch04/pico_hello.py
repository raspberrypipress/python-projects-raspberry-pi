import random
import vga2_bold_16x32 as font
from machine import Pin, SPI
import st7789py as st7789


tft=st7789.ST7789(
        SPI(0, baudrate=75_000_000, polarity=1, sck=Pin(2), mosi=Pin(3), miso=None),
        240,
        240,
        reset=Pin(4, Pin.OUT),
        cs=Pin(5, Pin.OUT),
        dc=Pin(6, Pin.OUT),
        backlight=Pin(7, Pin.OUT),
        rotation=2,
    )


text = "Hello World!"
tft.fill(0)
col_max = tft.width - font.WIDTH * len(text)
row_max = tft.height - font.HEIGHT

tft.text(
    font,
    text,
    col_max//2,
    row_max //2,
    st7789.color565(255,0,0), #foreground
    st7789.color565(0,255,0), #background
)


