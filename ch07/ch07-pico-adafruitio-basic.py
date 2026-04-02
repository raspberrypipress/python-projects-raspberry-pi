import network
import time
from umqtt.robust import MQTTClient
from secrets import secrets

mqtt_host = "io.adafruit.com"
aio_feedname = "test1"
mqtt_topic = secrets['aio_username']+"/feeds/"+aio_feedname

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

counter = 0
mqtt_client.connect()
while True:
    counter += 1
    print("publishing: ", counter)
    mqtt_client.publish(mqtt_topic, str(counter))
    time.sleep(5)
