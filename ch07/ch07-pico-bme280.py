import time
import busio
import board
import digitalio
from adafruit_bme280 import basic as adafruit_bme280

import network
import time
from umqtt.robust import MQTTClient
from secrets import secrets

mqtt_host = "io.adafruit.com"
user = secrets['aio_username']
mqtt_topic_temp = f"{user}/feeds/temp"
mqtt_topic_humid = f"{user}/feeds/humidity"
mqtt_sub_topic = f"{user}/feeds/onoff"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets['ssid'], secrets['password'])
while wlan.isconnected() == False:
    print('Waiting for connection...')
    time.sleep(1)
print("Connected to WiFi")

mqtt_client = MQTTClient(
        client_id="",
        server=mqtt_host,
        user=secrets['aio_username'] ,
        password=secrets['aio_key'] ,
        ssl=True)

collecting = True

def mqtt_sub_callback(topic, message):
    global collecting
    if message == b'ON':
        collecting = True
    elif message == b'OFF':
        collecting = False
        
mqtt_client.set_callback(mqtt_sub_callback)
mqtt_client.connect()
mqtt_client.subscribe(mqtt_sub_topic)

i2c = busio.I2C(board.GP1, board.GP0)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

counter = 0
while True:
    counter += 1
    mqtt_client.check_msg()
    print(collecting)
    if collecting and counter > 5:
        print("Temperature: %0.1f C" % bme280.temperature)
        print("Humidity: %0.1f %%" % bme280.relative_humidity)
        mqtt_client.publish(mqtt_topic_temp, 
                             str(bme280.temperature))
        mqtt_client.publish(mqtt_topic_humid,
                             str(bme280.relative_humidity))
        counter = 0
    time.sleep(1)