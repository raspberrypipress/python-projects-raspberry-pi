import board
import busio
import digitalio
import datetime
import time
from Adafruit_IO import Client, Feed
from adafruit_bme280 import basic as adafruit_bme280


ADAFRUIT_AIO_USERNAME = "xyz"
ADAFRUIT_AIO_KEY      = "XYZ"

aio = Client(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)
feed_temp = "temp"

def create_feed(name):
    feed = Feed(name=name)
    try:
        response = aio.create_feed(feed)
    except:
        pass
    
create_feed("temp")
create_feed("humidity")

spi = busio.SPI(board.D11, MISO=board.D9, MOSI=board.D10)
cs = digitalio.DigitalInOut(board.D22)
bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)

while True:
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.humidity)
    aio.send_data("temp", bme280.temperature)
    aio.send_data("humidity", bme280.humidity)

    time.sleep(5)
