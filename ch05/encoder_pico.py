import rp2
from machine import Pin
import array

@rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT, autopush=False, autopull=False, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
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
        self.sm = rp2.StateMachine(0,encoder_prog,freq=125_000_000, in_base=gpio_start)
        self.sm.active(1)
        self.zero_val = self.read_basic()
        
    def read_basic(self):
        #self.sm.put(1) # why does it need this?
        loops = self.sm.rx_fifo()
        for loop in range(loops):
            self.sm.get()
        buf = array.array('i', [0])
        self.sm.get(buf)
        return buf[0]
        
    def read(self):
        return self.read_basic() - self.zero_val
    
    def zero(self):
        self.zero_val = self.read_basic()
        
if __name__ == "__main__":
    import time
    print("starting")
    encoder = Encoder(2)
    print("loaded")
    while True:
        for i in range(10):
            val = encoder.read()
            print(val)
            time.sleep(1)
        print("Zeroing")
        encoder.zero()

