
import network
import time
from microdot import Microdot
import _thread
import secrets as secrets
import ssl

sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
sslctx.load_cert_chain("/cert3.der", "/key3.der")

gpio = 1
pattern = "rainbow_fade"
led_num = "100"
brightness = 0.5

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.secrets['ssid'], secrets.secrets['password'])

while not wlan.isconnected() and wlan.status() >= 0:
    print("Waiting to connect:")
    time.sleep(1)
    
print(wlan.ifconfig())

html = """
<!DOCTYPE html>
<html>
<head> <title>Pico W LED Controller</title> </head>
<body>
<h1>Pico W LED Controller</h1>
<h2>Current GPIO: {gpio}</h2>
<h2>Current pattern: {pattern}</h2>
<h2>Current number of LEDs: {led_num}</h2>
<h2>Current brightness: {brightness}</h2>
<form method="POST" action="">
        GPIO Pin:
        <select name="pin" id="pin">
            <option>0</option>
            <option>1</option>
            <option>2</option>
            <option>3</option>
            <option>4</option>
            <option>5</option>
            <option>6</option>
            <option>7</option>
            <option>8</option>
            <option>9</option>
            <option>10</option>
            <option>11</option>
            <option>12</option>
            <option>13</option>
            <option>14</option>
            <option>15</option>
            <option>16</option>
        </select>
        <input type="submit" value="Set GPIO">
</form>
<form method="POST" action="">
        Pattern:
        <select name="pattern" id="pattern">
            <option>rainbow_fade</option>
            <option>colour_chase</option>
            <option>sparkle</option>
        </select>
        <input type="submit" value="Set Pattern">
</form>
<form method="POST" action="">
        Number of LEDs:
        <input type="text" id="led_num" name="led_num">
        <input type="submit" value="Set number of LEDs">
</form>
</body>
</html>
"""
    
app = Microdot()
@app.route('/', methods=['GET', 'POST'])
def index(request):
    global gpio, pattern, led_num
    print(request)
    if request.method == 'POST':
        if 'pin' in request.form:
            gpio = request.form['pin']
        if 'pattern' in request.form:
            pattern = request.form['pattern']
        if 'led_num' in request.form:
            led_num = request.form['led_num']
    response = html.format(gpio=gpio, pattern=pattern, led_num=led_num, brightness=brightness)
    return response, {'Content-Type': 'text/html'}

#launch other core here to run the LEDs.
def led_control_thread():
    while True:
        time.sleep(10)
        print(pattern)

second_thread = _thread.start_new_thread(led_control_thread, ())
app.run(port=443, ssl=sslctx)
