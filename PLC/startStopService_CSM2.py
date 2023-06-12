from tendo import singleton
me = singleton.SingleInstance()
import datetime
import os
import time

processID = os.getpid()
print("This process has the PID", processID)


#DB credentials
import pymysql
db_user = "root"
db_pass = "insightzz123"
db_host = "localhost"
db_name = "Refinary3_CSM2"

from pymodbus.client.sync import ModbusTcpClient
import subprocess

#For logging error
import logging
import traceback
#Logging module
uilogger = None
folder_path = "/home/rfserver/insightzz/CSM2/code/PLC/"
logging.basicConfig(filename=folder_path+"startStopService.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
uilogger=logging.getLogger("startStopService")
uilogger.setLevel(logging.CRITICAL) #CRITICAL #DEBUG

#healthScriptPath
startHealthShPath = "/home/rfserver/insightzz/CSM2/code/HEALTH_MONITORING/check_lan_health.sh"
killHealthShPath = "/home/rfserver/insightzz/CSM2/code/HEALTH_MONITORING/kill_health_script.sh"
#rejectServicePath
rejectStartPath = "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/startPlcCode.sh"
rejectStopPath = "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/killPlcCode.sh"
# #frameCapture
# frameCaptureStartPath = "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/startFrameScript_CSM2.sh"
# frameCaptureStopPath = "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/killFrameScript_CSM2.sh"
#detectionScriptPath
detectionStartPath = "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/startDetectionScript_CSM2.sh"
detectionStopPath = "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/killDetectionScript_CSM2.sh"

# subprocess.call(["sh", startHealthScriptServer])

class PLC():
    def __init__(self):
        print("Inside initSerial")
        try:
            self.client = ModbusTcpClient("169.254.0.35", port=502, timeout=3)
            self.client.connect()
        except Exception as e:
            print(e)
            uilogger.critical("Exception in init PLC : "+str(e))            

    def writeToPLC(self,address,value):
        self.client.write_register(address = address,value=value)
        print("VALUE WRITTEN :"+str(value))

    def readFromPLC(self,regAddress):
        read=self.client.read_holding_registers(address = regAddress ,count =1,unit=1)
        return read.registers[0]


def updateProcessId(processId):
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
        cur = db_update.cursor()
        query = f"UPDATE PROCESS_ID_TABLE set PROCESS_ID = {str(processId)} where PROCESS_NAME = 'STARTSTOP_SERVICE'"
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()
    except Exception as e:
        print(f"Exception in update process id : {e}")
        uilogger.critical("Exception in update process id : "+str(e)) 

def update_query(Status,time):
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                         user=db_user,         # your username
                         passwd=db_pass,  # your password
                         db=db_name)
        cur = db_update.cursor()
        query=f"UPDATE `Refinary3_CSM2`.`Auto` SET End_Time = '{time}'  where Status = '{Status}'  ORDER BY End_Time asc limit 1;"
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()

def ChangePLCStatus():
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
        cur = db_update.cursor()
        PLC_Start_Time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        update_query("Manual",PLC_Start_Time)
        query=f"INSERT INTO `Refinary3_CSM2`.`Auto` (`Status`, `Start_Time`) VALUES ('Auto', '{PLC_Start_Time}');"
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()
    except Exception as e:
        print(f"Exception in update process id : {e}")
        uilogger.critical("Exception in update process id : "+str(e))             


def main():
    try:
        updateProcessId(processID)
        config_timer = 2000
        config_time = int(time.time()*1000)
        plcObject = PLC()
        boolVal1 = True
        boolVal2 = True
        while True:
            if int(time.time()*1000) - config_time > config_timer:
                config_time = int(time.time()*1000)
                registerVal = plcObject.readFromPLC(4099)
                if registerVal == 1 and boolVal1 == True:
                    boolVal1 = False
                    boolVal2 = True
                    print("machine on")
                    uilogger.critical("machine on")              
                    plcObject.writeToPLC(4097,1)
                    ChangePLCStatus()
                    subprocess.call(["sh", startHealthShPath])
                    subprocess.call(["sh", rejectStartPath])
                    subprocess.call(["sh", detectionStartPath])
                elif registerVal == 0 and boolVal2 == True:
                    boolVal1 = True
                    boolVal2 = False
                    print("machine off")
                    uilogger.critical("machine off") 
                    #ChangePLCStatus()           
                    plcObject.writeToPLC(4097,0)
                    subprocess.call(["sh", killHealthShPath])
                    subprocess.call(["sh", rejectStopPath])
                    subprocess.call(["sh", detectionStopPath])
                    # plcObject.writeToPLC(4097,0)
    except Exception as e:
        print(f"Exception in main : {e}")
        uilogger.critical("Exception in main : "+str(e))            

if __name__ == '__main__':
    main()    
