import time
import sys, select, os
import serial
import datetime

try:
    ser = serial.Serial('/dev/ttyACM0',9600,timeout = 1)
    time.sleep(3)
except:
    try:
        ser = serial.Serial('/dev/ttyACM1',9600,timeout = 1)
        time.sleep(3)
    except:
        try:
            ser = serial.Serial('/dev/ttyACM2',9600,timeout = 1)
            time.sleep(3)
        except Exception as e:
            print("Ardiuno Error :"+str(e))
ard_value = 0
value = 0
while True:
    #====== pressing enter will break loop ===========#
#    os.system('cls' if os.name == 'nt' else 'clear')
    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        line = raw_input()
        break
    try:
        #=========== For machine input =========#
        try:
            ard_value = int(ser.readline())
            print(ard_value)
        except:
            value = 0
            ard_value = 0
#        if ard_value == 1:
#            print("connected_"+str(datetime.datetime.now()))
#            value = 1
#        elif ard_value == 0:
#            print("not connected")            
#            pass
    except:
        try:
            ser = serial.Serial('/dev/ttyACM0',9600,timeout = 1)
            time.sleep(3)
        except:
            try:
                ser = serial.Serial('/dev/ttyACM1',9600,timeout = 1)
                time.sleep(3)
            except:
                try:
                    ser = serial.Serial('/dev/ttyACM2',9600,timeout = 1)
                    time.sleep(3)
                except Exception as e:
                    print("Ardiuno Error :"+str(e))    
