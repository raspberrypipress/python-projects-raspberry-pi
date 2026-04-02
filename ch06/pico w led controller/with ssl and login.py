import network
import time
from microdot import Microdot, redirect
import _thread
import secrets as secrets
import ssl
from microdot.session import Session
from microdot.login import Login
from pbkdf2 import generate_password_hash, check_password_hash

'''Notes
Needs (from microdot)
* helpers
*login
*microdot
*session
*__init

from not microdot:
(details here: https://microdot.readthedocs.io/en/latest/extensions.html#secure-user-sessions)
pbkdf2 (with itterations changed)
jwt
hmac

generated: -- note try different key length
cert3.der
key3.der
(openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=CommonNameOrHostname"
and
$ openssl pkey -in rsa_key.pem -out rsa_key.der -outform DER
$ openssl x509 -in rsa_cert.pem -out rsa_cert.der -outform DER
)

Also secrets.py

TODO:
* break the HTML out into external files
* and probably the LED animations as well
** If I do this well, it can be dropped in from the code from the earlier chapter? that let's us focus on the front end in this chapter.
* actually do the LED animations


'''

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

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password_hash = self.create_hash(password)

    def create_hash(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

print("here-3")


USERS = {
    'user001': User('user001', 'susan', 'hello'),
    'user002': User('user002', 'david', 'bye'),
    }


print("here-2")

app = Microdot()

print("here-1")
Session(app, secret_key='top-secret!')
login = Login()

print("here")


@login.user_loader
async def get_user(user_id):
    return USERS.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
async def login_page(request):
    if request.method == 'GET':
        return '''
            <!doctype html>
            <html>
              <body>
                <h1>Please Login</h1>
                <form method="POST">
                  <p>
                    Username<br>
                    <input name="username" autofocus>
                  </p>
                  <p>
                    Password:<br>
                    <input name="password" type="password">
                    <br>
                  </p>
                  <p>
                    <input name="remember_me" type="checkbox"> Remember me
                    <br>
                  </p>
                  <p>
                    <button type="submit">Login</button>
                  </p>
                </form>
              </body>
            </html>
        ''', {'Content-Type': 'text/html'}
    username = request.form['username']
    password = request.form['password']
    remember_me = bool(request.form.get('remember_me'))

    for user in USERS.values():
        if user.username == username:
            if user.check_password(password):
                return await login.login_user(request, user,
                                              remember=remember_me)
    return redirect('/login')

print("here 2")
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
    

@app.route('/', methods=['GET', 'POST'])
@login
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

print("nearly there")

#launch other core here to run the LEDs.
def led_control_thread():
    while True:
        time.sleep(10)
        print(pattern)

second_thread = _thread.start_new_thread(led_control_thread, ())
print("running....")
app.run(port=443, ssl=sslctx)
