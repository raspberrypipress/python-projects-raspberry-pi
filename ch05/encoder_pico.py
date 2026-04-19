import rp2
from machine import Pin

@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT, autopush=False,
             autopull=False, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def encoder_prog():
    jmp("update") 
    jmp("decrement") 
    jmp("increment") 
    jmp("update") 
    jmp("increment") 
    jmp("update")
    jmp("update")
    jmp("decrement")
    jmp("decrement")
    jmp("update") 
    jmp("update") 
    jmp("increment") 
    jmp("update") 
    jmp("increment") 
    label("decrement")
    jmp(y_dec, "update")
    wrap_target()
    label("update")
    mov(isr, y)
    push(noblock)
    out(isr, 2)
    in_(pins, 2)
    mov(osr, isr)
    mov(pc, isr)
    label("increment")
    mov(y, invert(y))
    jmp(y_dec, "23")
    label("23")
    mov(y, invert(y))
    wrap()
    nop() 
    nop() 
    nop()
    nop() 
    nop() 
    nop()
    nop() 
    nop() 

class Encoder:
    def __init__(self, gpio_start):
        a = Pin(gpio_start, Pin.IN, Pin.PULL_UP)
        b = Pin(gpio_start+1, Pin.IN, Pin.PULL_UP)
        self.sm = rp2.StateMachine(0,encoder_prog,freq=125_000_000,
                                   in_base=gpio_start)
        self.sm.active(1)
        self.zero_val = self.read_basic()
        
    def read_basic(self):
        loops = self.sm.rx_fifo()
        for loop in range(loops): # flush stale FIFO values
            self.sm.get()
        return self.sm.get()
        
    def read(self):
        return self.read_basic() - self.zero_val
    
    def zero(self):
        self.zero_val = self.read_basic()
        
if __name__ == "__main__":
    import time
    print("starting")
    encoder = Encoder(18)
    last_value = None
    while True:
        value = encoder.read()
        if value != last_value:
            print(value)
        last_value = value
        time.sleep(.1)