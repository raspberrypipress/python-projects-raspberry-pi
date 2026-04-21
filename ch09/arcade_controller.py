'''
Arcade controller for SuperTuxKart

created by Ben Everard with inspiration / stolen code from the MicroPython usb.device library examples
'''
import time
import usb.device
from usb.device.hid import HIDInterface
from usb.device.keyboard import KeyboardInterface, KeyCode
from machine import Pin

current_buttons = []
last_buttons = []

buttons = [
    [Pin(2,Pin.IN,Pin.PULL_UP), KeyCode.UP],
    [Pin(3,Pin.IN,Pin.PULL_UP), KeyCode.DOWN],
    [Pin(4,Pin.IN,Pin.PULL_UP), KeyCode.RIGHT],
    [Pin(5,Pin.IN,Pin.PULL_UP), KeyCode.LEFT],
    [Pin(17,Pin.IN,Pin.PULL_UP), KeyCode.SPACE], #Fire
    [Pin(9,Pin.IN,Pin.PULL_UP), KeyCode.UP], #A second accelerate
    [Pin(21,Pin.IN,Pin.PULL_UP), KeyCode.V], #Skid
    [Pin(13,Pin.IN,Pin.PULL_UP), KeyCode.N], #Nitro
    ]

def get_buttons():
    global current_buttons
    current_buttons = []
    for i, button in enumerate(buttons):
        if not button[0].value():
            current_buttons.append(i)

def keypad_example():
    global current_buttons, last_buttons
    k = KeyboardInterface()
    usb.device.get().init(k, builtin_driver=True)
    while not k.is_open():
        time.sleep_ms(100)

    while True:
        time.sleep(0.01)
        get_buttons()
        print(current_buttons)
        change = False
        for num in current_buttons:
            if num not in last_buttons:
                change=True
        for num in last_buttons:
            if num not in current_buttons:
                change=True
        last_buttons = current_buttons
        send_keys= []
        for button in current_buttons:
            send_keys.append(buttons[button][1])
        if change:
            k.send_keys(send_keys)

keypad_example()