import os
import time

timer = 1000
trigger_file_path = "/home/rfserver/insightzz/CSM2/code/PLC/triggerFile"
create=True
t1 = int(time.time()*1000)
while True:
    if int(time.time()*1000) - t1 > timer and create == True:
        t1 = int(time.time()*1000)
        os.system(f"touch {trigger_file_path}")
        print("triger file generate")
        create = False
    create =True