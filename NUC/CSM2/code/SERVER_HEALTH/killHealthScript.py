import os
import subprocess
import pymysql
import signal
#DB credentials
import pymysql
db_user = "root"
db_pass = "insightzz123"
db_host = "localhost"
db_name = "CSM_DB"


def kill_all():
    try:
        db_fetch = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
        cur = db_fetch.cursor()
        query = "SELECT PROCESS_ID from PROCESS_ID_TABLE WHERE PROCESS_NAME IN ('ServerHealth')"
        cur.execute(query)
        data_set = cur.fetchall()
        print(data_set)
        cur.close()
        for i in range(len(data_set)):
            if data_set[i][0] > 0:
                #terminating processes
                try:
                    print(data_set[i][0])                        
                    os.kill(data_set[i][0], signal.SIGKILL)
                except Exception as e:
                    print('Exception : ',e)
                    pass
            else:
                pass
        #os.remove(lock_file_path)
    except Exception as e:
        print('Exception : ',e)

if __name__ == '__main__':
    kill_all()
