from tendo import singleton
me = singleton.SingleInstance()


import os
import time

#DB credentials
import pymysql
db_user = "root"
db_pass = "insightzz123"
db_host = "localhost"
db_name = "CSM_DB"

timer = 3

processID = os.getpid()
print("This process has the PID", processID)

def updateProcessId(processId):
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
        cur = db_update.cursor()
        query = f"UPDATE PROCESS_ID_TABLE set PROCESS_ID = {str(processId)} where PROCESS_NAME = 'ServerHealth'"
        cur.execute(query)
        db_update.commit()
        cur.close()
        #print(data_set)
    except Exception as e:
        print(f"Exception in update process id : {e}")
        cur.close()

def update_health(item, status):
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                     user=db_user,         # your username
                     passwd=db_pass,  # your password
                     db=db_name)
        cur = db_update.cursor()
        query = f"UPDATE SYSTEM_HEALTH_TABLE set HEALTH = '{status}' where ITEM = '{item}'"
        cur.execute(query)
        db_update.commit()
        cur.close()
        #print(data_set)
    except Exception as e:
        print(f"Exception in update process id : {e}")
        cur.close()

def main():
    updateProcessId(processID)
    t1 = int(time.time())
    while True: 
        t2 = int(time.time())
        if (t2 -t1) == timer:
            server  = True if os.system("ping -c 1 " + "169.254.0.31") is 0 else False

            #updating sql with health
            if server == True:
                update_health("SERVER","OK")
            else:
                update_health("SERVER","NOTOK")

            t1 = int(time.time())
        
if __name__ == '__main__':
    main()
