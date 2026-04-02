import serial
import struct
import time

data_format = ">BBHHHHHHHHHHHHHHH"
mode_passive = b'\xe1\x00\x00'
command_read = b'\xe2\x00\x00'
start_of_frame = bytearray(b'\x42\x4d')

set_passive_command = bytearray()
set_passive_command.extend(start_of_frame)
set_passive_command.extend(mode_passive)
set_passive_command.extend(sum(set_passive_command).to_bytes(2, "big"))

read_command = bytearray()
read_command.extend(start_of_frame)
read_command.extend(command_read)
read_command.extend(sum(read_command).to_bytes(2, "big"))

timeout = 0.2 # in ms
uart = serial.Serial('/dev/ttyUSB')

uart.write(set_passive_command)

def read_pms5003():
    uart.write(read_command)
    
    time.sleep(0.1)
    
    raw_data = bytes()
    got_data = False
    while uart.in_waiting > 0:
        #need to loop through to avoid timeout
        last_data = time.monotonic()
        while time.monotonic() < last_data + timeout:
            if uart.in_waiting:
                raw_data += uart.read(1)
        got_data = True
       
    if got_data:
        try:
            print(raw_data)
            data = struct.unpack(data_format, raw_data[:32])
            return (data[6],data[7],data[8])
        except ValueError:
            return(-1,-1,-1)
            print("data malformed")
    
    return(-1,-1,-1)

print("listenning")
while True:
    time.sleep(5)
    pm1, pm25, pm10 = read_pms5003()
    print("pm1: %d ug/m^3"% pm1)
    print("pm2.5: %d ug/m^3"% pm25)
    print("pm10: %d ug/m^3"% pm10)
