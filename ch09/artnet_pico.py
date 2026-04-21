import network
import socket
import neopixel
import machine
import time
from secrets import secrets

LED_PIN = 0          # Pin connected to the WS2812b
NUM_LEDS = 16        # Number of LEDs in the string
ARTNET_PORT = 6454   # Standard Art-Net port
UNIVERSE_PINS = [1, 5, 18, 13, 22]  # [LSB, ..., MSB]
universe = 0
for i, pin_num in enumerate(UNIVERSE_PINS):
    pin = machine.Pin(pin_num, machine.Pin.IN, machine.Pin.PULL_UP)
    # Pins pulled low mean "0", left floating or high mean "1"
    bit = not pin.value()  # Pin reads 0 if pulled low, so invert
    universe |= (bit << i)
UNIVERSE = universe
print("Selected Art-Net universe:", UNIVERSE)

# Connect to WiFi (with 30 second timeout)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets['ssid'], secrets['password'])

timeout = 60  
start_time = time.time()

while not wlan.isconnected():
    if time.time() - start_time > timeout:
        print("Failed to connect to WiFi in 30 seconds. Giving up.")
        break
    time.sleep(0.1)

if wlan.isconnected():
    print('Connected to WiFi:', wlan.ifconfig())
else:
    raise RuntimeError("WiFi connection failed.")

# Set up NeoPixels
np = neopixel.NeoPixel(machine.Pin(LED_PIN), NUM_LEDS)

# Listen for Art-Net
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', ARTNET_PORT))

print("Listening for Art-Net...")

def parse_artnet_packet(packet):
    # Art-Net DMX packets start with "Art-Net\0"
    if packet[:8] != b'Art-Net\x00':
        return None
    # OpCode for ArtDMX: 0x5000 (little endian)
    if packet[8] != 0x00 or packet[9] != 0x50:
        return None
    # Universe (little endian)
    universe = packet[14] + (packet[15] << 8)
    if universe != UNIVERSE:
        return None
    # Data l    g endian)
    dlen = (packet[16] << 8) | packet[17]
    data = packet[18:18+dlen]
    return data

while True:
    pkt, addr = sock.recvfrom(1024)
    data = parse_artnet_packet(pkt)
    if data:
        print("Received Art-Net DMX data:", list(data))
        # Art-Net DMX data is just a stream of bytes
        for i in range(NUM_LEDS):
            offset = i*3
            if offset + 3 <= len(data):
                np[i] = (data[offset], data[offset+1], 
                         data[offset+2])
        np.write()