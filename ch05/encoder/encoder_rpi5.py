import encoder_pio

class Encoder:
    def __init__(self, gpio_start):
        self.sm = encoder_pio.load_encoder_sm(gpio_start)
        self.zero_val = encoder_pio.get_encoder_data(self.sm)
        
    def read(self):
        return self.zero_val - encoder_pio.get_encoder_data(self.sm)
        
    def zero(self):
        self.zero_val = encoder_pio.get_encoder_data(self.sm)
        
if __name__ == "__main__":
    import time
    
    encoder = Encoder(2)
    last_value = None
    while True:
        value = encoder.read()
        if value != last_value:
            print(value)
        last_value = value
        time.sleep(.1)