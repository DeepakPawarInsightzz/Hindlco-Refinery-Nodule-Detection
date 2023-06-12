#DB credentials
import pymysql
import datetime
db_user = "root"
db_pass = "insightzz123"
db_host = "localhost"
db_name = "Refinary3_CSM2"
def ChangePLCStatus():
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
        cur = db_update.cursor()
        PLC_Start_Time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query=f"INSERT INTO `Refinary3_CSM2`.`Auto` (`Status`, `Start_Time`) VALUES ('Auto', '{PLC_Start_Time}');"
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()
        print("update query")
    except Exception as e:
        print(f"Exception in update process id : {e}")

ChangePLCStatus()
         