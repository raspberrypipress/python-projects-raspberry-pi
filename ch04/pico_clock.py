import random
import vga2_bold_16x32 as font
from machine import Pin, SPI
import st7789py as st7789
from secrets import secrets
import network
import socket
import time
import simple_ntp
import math

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets['ssid'], secrets['password'])

max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

print("connected")
simple_ntp.set_time()

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

now = time.localtime()
prev_mins = -1


while True:
    now = time.localtime()
    if now[4] != prev_mins: # only update if there's a change
        prev_mins = now[4]
        text = str(str(now[3]) + ":" + str(now[4]))
        col_max = tft.width - font.WIDTH * len(text)
        row_max = tft.height - font.HEIGHT
        tft.fill(0)

        tft.text(
            font,
            text,
            col_max//2,
            row_max //2,
            st7789.color565(255,0,0), #foreground
            st7789.color565(0,255,0), #background
        )
    tft.pixel(
        int(math.sin(math.radians(180+now[5]*6))*100) + 120,
        int(math.cos(math.radians(180+now[5]*6))*100) + 120,
        st7789.color565(0,0,255)
        )
        
    time.sleep(0.1)
