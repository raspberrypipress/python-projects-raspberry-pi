import neopixel_pio
import array

class NeoPixel:
    def __init__(self, gpio, num_leds):
        self.num_leds = num_leds
        self.data = array.array("I", [0 for _ in range(num_leds)])
        self.sm = neopixel_pio.load_neopixel_sm(gpio)
        print(self.sm)
        
    def __setitem__(self, pixel, colour):
        self.data[pixel] = colour[2] << 8 | colour[0] << 16 | colour[1] << 24
        
    def write(self):
        neopixel_pio.send_neopixel_data(self.sm, self.data)

if __name__ == "__main__":        
    my_neo = NeoPixel(2, 10)
    my_neo[0] = (100,0,0)
    my_neo[1] = (0,100,0)
    my_neo[2] = (0,0,100)
    my_neo.write()
    print("Done")
