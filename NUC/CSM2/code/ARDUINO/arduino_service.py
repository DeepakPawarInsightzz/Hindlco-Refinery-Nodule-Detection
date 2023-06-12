from tendo import singleton
me = singleton.SingleInstance()

import serial
import os
import time
from datetime import datetime, timedelta
import threading

#For logging error
import logging
import traceback
#Logging module

folder_path = "/home/refinery03/Insightzz/code/ARDUINO/"

uilogger = None
logging.basicConfig(filename=folder_path+"UI_RECORD_ACT_.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
uilogger=logging.getLogger("UI_RECORD_ACT_")
uilogger.setLevel(logging.CRITICAL) #CRITICAL #DEBUG

trigger_file_path = "/home/refinery03/Insightzz/code/ARDUINO/trigger_file"

#DB credentials
import pymysql
db_user = "root"
db_pass = "insightzz123"
db_host = "169.254.0.5"
db_name = "REFINERY_DB"


processID = os.getpid()
print("This process has the PID", processID)

def updateProcessId(processId):
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
        cur = db_update.cursor()
        query = f"UPDATE PROCESS_ID_TABLE set PROCESS_ID = {str(processId)} where PROCESS_NAME = 'ARDUINO_SERVICE'"
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()
    except Exception as e:
        print(f"Exception in update process id : {e}")
        cur.close()

class Arduino():
    def __init__(self):
        print("Inside initSerial")
        try:
            self.serialObject = serial.Serial('/dev/ttyACM0',9600,timeout = 1)
            time.sleep(3)
        except:
            try:
                self.serialObject = serial.Serial('/dev/ttyACM1',9600,timeout = 1)
                time.sleep(3)
            except:
                try:
                    self.serialObject = serial.Serial('/dev/ttyACM2',9600,timeout = 1)
                    time.sleep(3)
                except:
                    pass
    
    def startPLC(self):
        print("Inside startPLC")
        try:
            print("alert generated")
            self.serialObject.write(b'1')
        except Exception as e:
            print("startPLC Exception is : ", e)
            uilogger.debug("startPLC Exception is : "+str(e))            

    def stopPLC(self):
        print("Inside stopPLC")
        try:
            print("alert stopped")
            self.serialObject.write(b'0')
        except Exception as e:
            print("stopPLC Exception is : ", e)
            uilogger.debug("stopPLC Exception is : "+str(e))            

def main():
    updateProcessId(processID)
    temp1 = False
    temp2 = False
    timer = 3000
    while True:
        # print(f"temp1 , temp2 : {temp1, temp2}")
        if os.path.exists(trigger_file_path) == True and temp1 == False:
            t1 = int(time.time()*1000)
            print("start plc")
            arduino_object.startPLC()
            temp1 = True
            temp2 = False
        elif os.path.exists(trigger_file_path) == False and temp2 == False: 
            print("stop plc")
            arduino_object.stopPLC()
            temp2 = True
            temp1 = False
        if os.path.exists(trigger_file_path) == True and temp1 == True:
           if int(time.time()*1000) - t1 > timer:
                t1 = int(time.time()*1000)
                os.system("rm /home/refinery03/Insightzz/code/ARDUINO/trigger_file")

if __name__ == '__main__':
    arduino_object = Arduino()
    main()    


