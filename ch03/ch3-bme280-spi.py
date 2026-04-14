import board
import busio
import time
import digitalio

from adafruit_bme280 import basic as adafruit_bme280

spi = busio.SPI(board.GP2, MISO=board.GP4, MOSI=board.GP3)
cs = digitalio.DigitalInOut(board.GP5)
bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)

while True:
    print("Temperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)
    time.sleep(1)