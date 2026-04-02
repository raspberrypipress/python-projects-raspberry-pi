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
aio_onoff_feed = "onoff"

mqtt_topic_temp = secrets['aio_username']+"/feeds/"+"temp"
mqtt_topic_humid = secrets['aio_username']+"/feeds/"+"humidity"
mqtt_sub_topic = secrets['aio_username']+"/feeds/"+aio_onoff_feed

# Connect to WiFi
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

spi = busio.SPI(board.GP2, MISO=board.GP4, MOSI=board.GP3)
cs = digitalio.DigitalInOut(board.GP5)

bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)


counter = 0
while True:
    counter += 1
    mqtt_client.check_msg()
    print(collecting)
    if collecting and counter > 5:
        print("Temperature: %0.1f C" % bme280.temperature)
        print("Humidity: %0.1f %%" % bme280.relative_humidity)
        mqtt_client.publish(mqtt_topic_temp, str(bme280.temperature))
        mqtt_client.publish(mqtt_topic_humid, str(bme280.relative_humidity))
        counter = 0
    time.sleep(1)


