import machine
i2c = machine.I2C(1,scl=Pin(3), sda=Pin(2))

print('Scan i2c bus...')
devices = i2c.scan()

if len(devices) == 0:
  print("No i2c device !")
else:
  print('i2c devices found:',len(devices))

  for device in devices:  
    print("Decimal address: ",device," | Hex address: ",hex(device))
