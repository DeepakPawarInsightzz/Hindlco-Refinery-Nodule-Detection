# import keyboard

# IN this code we can read the  value of register i.e 0 or 1 
#  And also write register and value to give as an input function
from pymodbus.client import ModbusTcpClient


def init_modbus():
    client = ModbusTcpClient("169.254.0.35", port=502, timeout=3)
    client.connect()
    return client

 # Read PLC function
def readFromPLC(client,address):
    # here we can put address i.e register value that we want to read on address directly
    result = client.read_holding_registers(address = address,count =2,unit=1)
    print("current register value is :",result.getRegister(0))
 
 # Write PLC function

def writeToPLC(client,address,value):
    client.write_register(address = address,value=value)
    print("VALUE WRITTEN :"+str(value))


client=init_modbus()
while(True):
    # address=int(input("ENTER REGISTER VALUE :  "))
    # value=int(input("ENTER VALUE TO WRITE :  "))
    # writeToPLC(client,address,value)
   
    # Read PLC function
    readFromPLC(client,4099)
    # here 4099 is register value in readFromPLC function 
