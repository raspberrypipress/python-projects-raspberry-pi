import network
import socket
import neopixel
import machine
import time
import struct
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

def send_artpoll_reply(dest_ip):
    print("got poll request")
    my_ip = wlan.ifconfig()[0]
    ip_parts = [int(x) for x in my_ip.split('.')]
    short_name = "MicroPy Node"
    long_name = "MicroPython ArtNet"
    short_name_bytes = bytes(short_name, 'ascii') + \
                           b'\x00' * (18 - len(short_name))
    long_name_bytes = bytes(long_name, 'ascii') + \
                          b'\x00' * (64 - len(long_name))
    node_report = b"OK" + b'\x00' * (64 - 2)
    subswitch = (UNIVERSE >> 8) & 0x0F
    netswitch = (UNIVERSE >> 12) & 0x7F
    # Build reply as fixed-length, pre-zeroed array
    reply = bytearray(239)
    reply[0:8] = b'Art-Net\x00'
    reply[8:10] = struct.pack('<H', 0x2100)
    reply[10:14] = bytes(ip_parts)
    reply[14:16] = struct.pack('>H', ARTNET_PORT)
    reply[18] = netswitch
    reply[19] = subswitch
    reply[23] = 0x80            
    reply[26:44] = short_name_bytes
    reply[44:108] = long_name_bytes
    reply[108:172] = node_report
    reply[172] = 0  
    reply[173] = 1  
    reply[174] = 0x80  # PortTypes[0] = 0x80 (DMX output)
    reply[190] = UNIVERSE & 0xFF  # SwOut[0]: universe LSB
    sock.sendto(reply, (dest_ip, ARTNET_PORT))

@micropython.native
def parse_artnet_packet(packet, addr):
    # Art-Net header
    if packet[:8] != b'Art-Net\x00':
        return
    opcode = packet[8] | (packet[9] << 8)
    if opcode == 0x5000:  # ArtDMX
        universe = packet[14] + (packet[15] << 8)
        if universe == UNIVERSE:
            np.buf[:NUM_LEDS*3] = packet[18:18+(NUM_LEDS*3)]
            np.write()
    elif opcode == 0x2000:  # ArtPoll
        send_artpoll_reply(addr[0])

while True:
    pkt, addr = sock.recvfrom(1024)
    data = parse_artnet_packet(pkt, addr)
    if data:
        print("Received Art-Net DMX data:", list(data))
        # Art-Net DMX data is just a stream of bytes
        for i in range(NUM_LEDS):
            offset = i*3
            if offset + 3 <= len(data):
                np[i] = (data[offset], data[offset+1], 
                         data[offset+2])
        np.write()