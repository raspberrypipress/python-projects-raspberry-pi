import board
import busio
import time

from adafruit_bme280 import basic as adafruit_bme280

i2c=busio.I2C(board.D3, board.D2)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)

while True:
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.humidity)
    print("Pressure: %0.1f hPa" % bme280.pressure)
    time.sleep(1)

