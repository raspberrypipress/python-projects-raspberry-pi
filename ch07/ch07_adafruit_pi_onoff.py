import board
import busio
import digitalio
import time
from Adafruit_IO import MQTTClient

from adafruit_bme280 import basic as adafruit_bme280
collecting = True

ADAFRUIT_AIO_USERNAME = "xyz"
ADAFRUIT_AIO_KEY      = "XYZ"

aio = MQTTClient(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)

def message(client, feed_id, payload):
    global collecting
    print('Feed {0} received new value: {1}'.format(
          feed_id, payload))
    if payload == 'ON':
        collecting = True
    if payload == 'OFF':
        collecting = False
    
aio.on_message = message

aio.connect()
aio.subscribe('onoff')

aio.loop_background()

spi = busio.SPI(board.D11, MISO=board.D9, MOSI=board.D10)
cs = digitalio.DigitalInOut(board.D22)
bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)

counter = 0
while True:
    if counter == 5:
        print(collecting)
        if collecting:
            print("\nTemperature: %0.1f C" % bme280.temperature)
            print("Humidity: %0.1f %%" % bme280.humidity)
            aio.publish("temp", bme280.temperature)
            aio.publish("humidity", bme280.humidity)
        counter = 0
    counter = counter+1

    time.sleep(1)