from pymodbus.client.sync import ModbusTcpClient

def writeToPLC(client,address,value):
    client.write_register(address = address,value=value)
    print("VALUE WRITTEN :"+str(value))

client = ModbusTcpClient("169.254.0.35", port=502, timeout=3)
client.connect()

# #light signal
# writeToPLC(client,4097,0)

# rejection signal
#writeToPLC(client,4098,1)

# # machine on/off input
# read=client.read_holding_registers(address = 4099 ,count =1,unit=1)
# print(read.registers)

lightBool = False

# read=client.read_holding_registers(address = 4098 ,count =1,unit=1)
# print(read.registers)

while True:
    read=client.read_holding_registers(address = 4099 ,count =1,unit=1)
    # print(read.registers)
    val = read.registers[0]
    if val == 0 and lightBool == False:
        #writeToPLC(client,4098,0)
        lightBool = True
        print(val)
    elif val == 1 and lightBool == True:
        #writeToPLC(client,4098,1)
        lightBool = False
        print(val)

    
