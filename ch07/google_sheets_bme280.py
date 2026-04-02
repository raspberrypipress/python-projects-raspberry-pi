import board
import busio
import time
import digitalio
import gspread
import datetime


gc = gspread.service_account()

sh = gc.open("pi_data")
worksheet = sh.get_worksheet(0)

from adafruit_bme280 import basic as adafruit_bme280

spi = busio.SPI(board.D11, MISO=board.D9, MOSI=board.D10)
cs = digitalio.DigitalInOut(board.D22)
bme280 = adafruit_bme280.Adafruit_BME280_SPI(spi, cs)

while True:
    print("\nTemperature: %0.1f C" % bme280.temperature)
    print("Humidity: %0.1f %%" % bme280.humidity)
    worksheet.append_row([str(datetime.datetime.now()),bme280.temperature,bme280.humidity])
    time.sleep(1)
