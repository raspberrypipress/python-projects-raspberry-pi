import rp2
from machine import Pin
import array
import time


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_HIGH, out_init=rp2.PIO.OUT_HIGH, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
def uart_tx():
    wrap_target()
    pull()                  .side(1) [7] 
    set(x, 7)               .side(0) [7] 
    label("tx_loop")
    out(pins, 1)                          
    jmp(x_dec, "tx_loop")            [6] 
    nop()      .side(1)              [6]
    wrap()
    
    
@rp2.asm_pio(
    autopush=True,push_thresh=8,in_shiftdir=rp2.PIO.SHIFT_RIGHT,fifo_join=rp2.PIO.JOIN_RX)
def uart_rx():
    wrap_target()
    wait(0, pin, 0)                       
    set(x, 7)                         [10] 
    label("rx_loop")
    in_(pins, 1)                         
    jmp(x_dec, "rx_loop")             [6]  
    wrap()


class UART:
    def __init__(self, gpio_tx, gpio_rx, baud):
        self.sm_tx = rp2.StateMachine(0, uart_tx, freq=8*baud, out_base=gpio_tx, sideset_base=gpio_tx)
        self.sm_rx = rp2.StateMachine(1, uart_rx, freq=8*baud, in_base=gpio_rx)
        self.sm_tx.active(1)
        self.sm_rx.active(1)
        
    def send(self, data):
        print("puttin: ", data)
        self.sm_tx.put(data)
        
    def read(self):
        data = []
        while (self.sm_rx.rx_fifo() > 0):
            print(self.sm_rx.rx_fifo())
            data.append(chr(self.sm_rx.get() >> 24))
        return data
    
if __name__ == "__main__":
    uart = UART(2,3,9600)
    data = array.array("I", [72, 69, 76,76, 79])
    while True:
        uart.send(data)
        print(uart.read())
        time.sleep(1)
