# from tendo import singleton
# me = singleton.SingleInstance()

import os
import time
from datetime import datetime, timedelta
import threading

#For logging error
import logging
import traceback
#Logging module

from pymodbus.client.sync import ModbusTcpClient

folder_path = "/home/rfserver/insightzz/CSM2/code/PLC/"

uilogger = None
logging.basicConfig(filename=folder_path+"rejectionCode.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
uilogger=logging.getLogger("rejectionCode")
uilogger.setLevel(logging.CRITICAL) #CRITICAL #DEBUG

trigger_file_path = "/home/rfserver/insightzz/CSM2/code/PLC/triggerFile"

#DB credentials
import pymysql
db_user = "root"
db_pass = "insightzz123"
db_host = "localhost"
db_name = "Refinary3_CSM2"

processID = os.getpid()
print("This process has the PID", processID)

def updateProcessId(processId):
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
        cur = db_update.cursor()
        query = f"UPDATE PROCESS_ID_TABLE set PROCESS_ID = {str(processId)} where PROCESS_NAME = 'PLC_SERVICE'"
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()
    except Exception as e:
        print(f"Exception in update process id : {e}")
        cur.close()

class PLC():
    def __init__(self):
        print("Inside initSerial")
        try:
            self.client = ModbusTcpClient("169.254.0.35", port=502, timeout=3)
            self.client.connect()
            self.writeToPLC(4097,1)
        except Exception as e:
            print(e)
            uilogger.debug("Exception in init PLC : "+str(e))            

    def writeToPLC(self,address,value):
        self.client.write_register(address = address,value=value)
        print("VALUE WRITTEN :"+str(value))

    def startPLC(self):
        try:
            self.writeToPLC(4098,1)
        except Exception as e:
            print("startPLC Exception is : ", e)
            uilogger.debug("startPLC Exception is : "+str(e))            

    def stopPLC(self):
        try:
            self.writeToPLC(4098,0)
        except Exception as e:
            print("stopPLC Exception is : ", e)
            uilogger.debug("stopPLC Exception is : "+str(e))            

def main():
    updateProcessId(processID)
    temp1 = False
    temp2 = False
    timer = 3000
    plcObject = PLC()
    while True:
        # print(f"temp1 , temp2 : {temp1, temp2}")
        if os.path.exists(trigger_file_path) == True and temp1 == False:
            t1 = int(time.time()*1000)
            print("start plc")
            plcObject.startPLC()
            temp1 = True
            temp2 = False
        elif os.path.exists(trigger_file_path) == False and temp2 == False:
            print("stop plc")
            plcObject.stopPLC()
            temp2 = True
            temp1 = False
        if os.path.exists(trigger_file_path) == True and temp1 == True:
            if int(time.time()*1000) - t1 > timer:
                t1 = int(time.time()*1000)
                os.system(f"rm {trigger_file_path}")


if __name__ == '__main__':
    main()    

