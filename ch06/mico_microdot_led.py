import network
import socket
import time
from microdot.microdot import Microdot
from secrets import secrets

from machine import Pin, ADC

analogue = ADC(Pin(26))

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets['ssid'], secrets['password'])

led_state=False
led = Pin("LED", Pin.OUT)
led.value(led_state)


def generate_html():
    return f"""<!DOCTYPE html>
            <html>
            <head> <title>Pico W</title> </head>
            <body> <h1>Pico W</h1>
            <p>The LED is {led_state}</p>
            </body>
            </html>
            """



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
@app.route('/')
def index(request):
    return generate_html(), {'Content-Type': 'text/html'}

@app.route('/on')
def on(request):
    global led_state
    led_state = True
    led.value(led_state)
    return generate_html(), {'Content-Type': 'text/html'}

@app.route('/off')
def on(request):
    global led_state
    led_state = False
    led.value(led_state)
    return generate_html(), {'Content-Type': 'text/html'}
    

app.run(port=80)
