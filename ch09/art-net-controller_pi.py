import socket
import struct
import time
import gc

ARTNET_PORT = 6454
DEFAULT_IP = "192.168.1.244"
BROADCAST_IP  = "192.168.1.255"

class RemoteNeopixel:
    def __init__(self, universe, num_pixels=170, 
                 ip=DEFAULT_IP, port=ARTNET_PORT):
        if num_pixels < 1 or num_pixels > 170:
            raise ValueError("num_pixels must be between 1 " +
                "and 170 for a single DMX universe (512/3)")
        self.universe = universe
        self.num_pixels = num_pixels
        self.ip = ip
        self.port = port
        self.dmx = [0] * (num_pixels * 3)
        self.sock = socket.socket(socket.AF_INET, 
                        socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, 
            socket.SO_BROADCAST, 1)
        self.sock.setblocking(False)

    def __setitem__(self, pixel, rgb):
        if 0 <= pixel < self.num_pixels:
            if not (isinstance(rgb, tuple) and len(rgb) == 3):
                raise ValueError("Value must be a (r,g,b) tuple")
            r, g, b = [max(0, min(255, int(x))) for x in rgb]
            idx = pixel * 3
            self.dmx[idx] = r
            self.dmx[idx + 1] = g
            self.dmx[idx + 2] = b
        else:
            raise IndexError(f"Pixel must be > 0 &"
                             f" < {self.num_pixels-1}")

    def __getitem__(self, pixel):
        if 0 <= pixel < self.num_pixels:
            idx = pixel * 3
            return tuple(self.dmx[idx:idx + 3])
        else:
            raise IndexError(f"Pixel must be > 0 &"
                             f" < {self.num_pixels-1}")

    def write(self):
        # Pad DMX data to minimum 2 bytes as per Art-Net spec 
        dmx_data = self.dmx + [0] * max(0, 2 - len(self.dmx))
        packet = self.artdmx_packet(self.universe, dmx_data)
        self.sock.sendto(packet, (self.ip, self.port))

    @staticmethod
    def artdmx_packet(universe, dmx_data):
        ID = b'Art-Net\x00'
        OpCode = struct.pack('<H', 0x5000)
        ProtVer = struct.pack('>H', 14)
        Sequence = struct.pack('B', 0)
        Physical = struct.pack('B', 0)
        Universe = struct.pack('<H', universe)
        Length = struct.pack('>H', len(dmx_data))
        packet = ID + OpCode + ProtVer + Sequence + \
                 Physical + Universe + Length + bytes(dmx_data)
        return packet
        
    @staticmethod
    def artpoll_packet():
        """Construct an ArtPoll packet."""
        ID = b'Art-Net\x00'
        OpCode = struct.pack('<H', 0x2000)  
        ProtVer = struct.pack('>H', 14)
        TalkToMe = struct.pack('B', 0b00001100)  
        Priority = struct.pack('B', 0x10)       
        return ID + OpCode + ProtVer + TalkToMe + Priority
        
    @staticmethod
    def get_ip_from_universe(nodes, universe):
        for node in nodes:
            if node['universe'] == universe:
                return node['ip']
        return None
    @staticmethod
    def scan_for_universe(target_universe=0, timeout=1.0,
           broadcast_ip=BROADCAST_IP, port=ARTNET_PORT):
        sock = socket.socket(socket.AF_INET, 
                   socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(timeout)
        sock.bind(('', ARTNET_PORT))
        
        # Send ArtPoll
        poll = RemoteNeopixel.artpoll_packet()
        sock.sendto(poll, (broadcast_ip, port))
        
        found_nodes = []
        start = time.time()
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                print(data, addr)
                # Check it's an ArtPollReply
                if data.startswith(b'Art-Net\x00') and \
                       data[8:10] == struct.pack('<H', 0x2100):
                    print("got reply")
                    ip = addr[0]
                    # Port is at offset 26-27, universe at offset 14
                    universes = [data[190 + i] for i in range(4)]
                    universe = universes[0] # just have one per node
                    print("target universe: ", target_universe)
                    # This is just one universe per reply
                    shortname = data[26:44].decode(
                             'ascii', errors='replace').strip('\0')
                    longname = data[44:108].decode(
                             'ascii', errors='replace').strip('\0')
                    found_nodes.append({'ip': ip, 
                             'shortname': shortname, 
                             'longname': longname, 
                             'universe': universe})
                    print(f"Found node: IP={ip}, "
                            "ShortName='{shortname}', "
                            "LongName='{longname}', "
                            "Universe={universe}")
            except socket.timeout:
                break
            
            except Exception as e:
                print("Error parsing ArtPollReply:", e)
            if time.time() - start > timeout:
                break
        sock.close()
        return found_nodes
        
def wheel(pos):
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)

def rainbow_cycle(remote, wait=0.02):
    while True:
        for j in range(256):
            for i in range(remote.num_pixels):
                remote[i] = wheel(
                     (int(i * 256 / remote.num_pixels) + j) % 256)
            remote.write()
            gc.collect()
            time.sleep(wait)

if __name__ == "__main__":
    nodes = RemoteNeopixel.scan_for_universe(target_universe=1,
                                             timeout=10)
    if not nodes:
        print("No Art-Net nodes found")
    else:
        print(f"Found {len(nodes)} Art-Net node(s)")
        for node in nodes:
            print(node)
            
    print("running a rainbow on universe 1")
    
    ip_addr = RemoteNeopixel.get_ip_from_universe(nodes, 1)
            
    print(ip_addr)
    
    NUM_PIXELS = 10  # Set to your number of pixels
    remote = RemoteNeopixel(universe=1, 
                            num_pixels=NUM_PIXELS, 
                            ip=ip_addr)
    print("Running rainbow_cycle! Press Ctrl+C to exit.")
    try:
        rainbow_cycle(remote, wait = 0.01)
    except KeyboardInterrupt:
        print("\nStopped.")
