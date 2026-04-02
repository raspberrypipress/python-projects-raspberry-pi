import uart_pio
import array
import time

data = array.array("I", [72, 69, 76, 76, 79])

    
class UART:
    def __init__(self, gpio_tx, gpio_rx, baud):
        self.sm_tx = uart_pio.load_uart_tx_sm(gpio_tx, baud)
        self.sm_rx = uart_pio.load_uart_rx_sm(gpio_rx, baud)
        
    def send(self, data):
        uart_pio.send_uart_data(self.sm_tx, data)
        
    def read(self):
        return uart_pio.get_uart_data(self.sm_rx)
        
uart = UART(3,2, 100000)
while True:
    print(uart.read())
    time.sleep(1)
