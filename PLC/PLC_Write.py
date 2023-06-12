
import time

from pymodbus.client import ModbusTcpClient

# Home Condition Set Zero 
# Write PLC function

def home_condition_set_0():
    client = ModbusTcpClient("192.168.1.5", port=502, timeout=3)
    client.connect()
    new_value = 0
    # 4097 is the register that we want to communicate and 0 is the value given to it to write in it.
    client.write_register(address = 4097, value = new_value)

# Home Condition Set one 

def home_condition_set_1():
    client = ModbusTcpClient("192.168.1.5", port=502, timeout=3)
    client.connect()
    new_value = 1
# 4097 is the register that we want to communicate and 1 is the value given to it to write in it.

    client.write_register(address = 4097, value = new_value)

# Upward Condition Set Zero 



# home_condition_set_0()
# time.sleep(0.2)
# home_condition_set_1()
# time.sleep(0.2)
# home_condition_set_0()
# time.sleep(10)







