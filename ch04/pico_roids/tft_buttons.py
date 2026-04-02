from machine import Pin

class Buttons:
    def __init__(self):
        self.name = "Pico external buttons"
        self.left = Pin(14, Pin.IN, Pin.PULL_UP)
        self.right = Pin(13, Pin.IN, Pin.PULL_UP)
        self.fire = Pin(12, Pin.IN, Pin.PULL_UP)
        self.thrust = Pin(11, Pin.IN, Pin.PULL_UP)
        self.hyper = Pin(10, Pin.IN, Pin.PULL_UP)
