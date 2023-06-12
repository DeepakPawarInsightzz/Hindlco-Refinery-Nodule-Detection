import time

import serial

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
        except:
            pass
1
while True:
    #print(ser.read())
    try:
        def ledon_13():
            ser.write(b'1')
        def ledoff_13():
            ser.write(b'0')
        x = int(input("Enter \n 0 for turning off 13 \n 1 for turning on RED \n 2 for ALARM \n 3 for break: "))
        if x == 1:
            ledon_13()
        if x == 0:
            ledoff_13()
        if x == 2:
            ser.write(b'2')
        if x == 3:
            break
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

