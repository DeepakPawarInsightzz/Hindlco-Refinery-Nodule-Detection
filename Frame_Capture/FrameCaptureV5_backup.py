from pypylon import pylon as py
import numpy as np
import cv2
import shutil
import time
import os
import subprocess
logPath = "/home/rfserver/insightzz/FRAME_CAPTURE/"
import logging
logPath = "/home/rfserver/insightzz/FRAME_CAPTURE/"
logging.basicConfig(filename=f"{logPath}MV_RECORD_ACT_.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
mv_logger=logging.getLogger("MV_RECORD_ACT_")
mv_logger.setLevel(logging.DEBUG)
mv_logger.debug("CODE STARTED") 

        
NUM_CAMERAS = 6
processID = os.getpid()
print("This process has the PID", processID)

restartFrameCapture="/home/rfserver/insightzz/FRAME_CAPTURE/restartFrameScript.sh"


csm1frontcam = "40271839"
csm1s1cam = "40271837"
csm1s2cam = "40271844"

csm2frontcam = "40267929"
csm2s1cam = "40271836"
csm2s2cam = "40271846"

savePath1 = "/home/rfserver/insightzz/CSM1/code/FRAME_CAPTURE/"
savePath2 = "/home/rfserver/insightzz/CSM2/code/FRAME_CAPTURE/"

import pymysql
db_user = "root"
db_pass = "insightzz123"
db_host = "localhost"
db_name1 = "Refinary3_CSM1"
db_name2 = "Refinary3_CSM2"


  #================================== UPDATE PROCESS ID FUN ===================================================#
def updateProcessId(processId):
        try:
            db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name1)
            cur = db_update.cursor()
            query = f"UPDATE PROCESS_ID_TABLE set PROCESS_ID = {str(processId)} where PROCESS_NAME = 'FRAME_CAPTURE_CAM1'"
            cur.execute(query)
            db_update.commit()
            cur.close()
            db_update.close()
            #print(data_set)
        except Exception as e:
            print(f"Exception in update process id : {e}")
            cur.close()

def update_cam_health1(CAM,HEALTH_STATUS):
        db_fetch = pymysql.connect(host = db_host,
                                    user = db_user,
                                    password = db_pass,
                                    db = db_name1)
        cur = db_fetch.cursor()
        query= f"update SYSTEM_HEALTH_TABLE set HEALTH = '{HEALTH_STATUS}' where ITEM = '{CAM}'"
        print(query)
        try:
            cur.execute(query)
            cur.close()
            db_fetch.commit()
            
        except Exception as e:
                print(str(e))
                return   

def update_cam_health2(CAM,HEALTH_STATUS):
    db_fetch = pymysql.connect(host = db_host,
                                user = db_user,
                                password = db_pass,
                                db = db_name2)
    cur = db_fetch.cursor()
    query= f"update SYSTEM_HEALTH_TABLE set HEALTH = '{HEALTH_STATUS}' where ITEM = '{CAM}'"
    print(query)
    try:
        cur.execute(query)
        cur.close()
        db_fetch.commit()
        
    except Exception as e:
            print(str(e))
            return  

def setup_cameras():
    try:
        # get the transport layer factory
        tlf = py.TlFactory.GetInstance()
        
        # create an empty list to store cameras
        cameras = []
        
        # create a device filter for Basler GigE cameras
        di = py.DeviceInfo()
        di.SetDeviceClass("BaslerGigE")
        
        # get all available Basler GigE cameras
        devices = tlf.EnumerateDevices([di,])
        
        # create an instant camera array with the desired number of cameras
        cam_array = py.InstantCameraArray(NUM_CAMERAS)
        
        # attach each camera to the instant camera array
        for i in range(NUM_CAMERAS):
                      
            camera = py.InstantCamera(tlf.CreateDevice(devices[i]))
            camera.Open()
            cameras.append(camera)
            camera_id = camera.GetDeviceInfo().GetSerialNumber()
            #-------------------------CSM1------------------
            if camera_id == csm1frontcam:
                    try:
                        update_cam_health1("CAM1","OK")
                    except Exception as e:
                        print("csm1Front error: "+str(e))
                        mv_logger.debug("csm1Front error: "+str(e))
                        update_cam_health1("CAM1","NOTOK")
            if camera_id == csm1s1cam:
                    try:
                        update_cam_health1("CAM2","OK")
                    except Exception as e:
                        print("csm1second error: "+str(e))
                        mv_logger.debug("csm1second error: "+str(e))
                        update_cam_health1("CAM2","NOTOK")
            if camera_id == csm1s2cam:
                    try:
                        update_cam_health1("CAM3","OK")
                    except Exception as e:
                        print("csm1Front error: "+str(e))
                        mv_logger.debug("csm1second error: "+str(e))
                        update_cam_health1("CAM3","NOTOK")

            #-----------------------CSM2-----------------------------------
            if camera_id == csm2frontcam:
                    try:
                        update_cam_health2("CAM1","OK")
                    except Exception as e:
                        print("csm2Front error: "+str(e))
                        mv_logger.debug("csm2Front error: "+str(e))
                        update_cam_health2("CAM1","NOTOK")
            if camera_id == csm2s1cam:
                    try:
                        update_cam_health2("CAM2","OK")
                    except Exception as e:
                        print("csm2second error: "+str(e))
                        mv_logger.debug("csm2second error: "+str(e))
                        update_cam_health2("CAM2","NOTOK")
            if camera_id == csm2s2cam:
                    try:
                        update_cam_health2("CAM3","OK")
                    except Exception as e:
                        print("csm2Front error: "+str(e))
                        mv_logger.debug("csm2second error: "+str(e))
                        update_cam_health2("CAM3","NOTOK")
        return cameras
    except Exception as e:
        mv_logger.debug("setup_cameras error: "+str(e))
        subprocess.call(["sh", restartFrameCapture])


def setup_camera_params(camera):
        try:
            camera.GevSCPSPacketSize.SetValue(1500)          
            camera.GevSCPD.SetValue(1000)          
            camera.GevSCFTD.SetValue(1000)          
            camera.StartGrabbing(1)
            camera.AcquisitionFrameRateEnable=True
            camera.AcquisitionFrameRateAbs=3.00
            camera.ExposureTimeAbs.SetValue(15000)                
            camera.ExposureTimeRaw.SetValue(15000)
        except Exception as e:
            mv_logger.debug("setup_cameras error: "+str(e))
    
    # # configure image acquisition
    # camera.StartGrabbingMax(1)

def grab_frames(cameras):
    try:
        t1 = int(time.time()*1000)
        # grab frames from each camera
        for i, camera in enumerate(cameras):
            try:
                grab_result = camera.RetrieveResult(1000, py.TimeoutHandling_ThrowException)
            except py.TimeoutException as e:
                print(f"TimeoutException: {e}")
                mv_logger.debug("Cameras"+str(e))
                update_cam_health1("CAM1","NOTOK")
                update_cam_health1("CAM2","NOTOK")
                update_cam_health1("CAM3","NOTOK")
                update_cam_health2("CAM1","NOTOK")
                update_cam_health2("CAM2","NOTOK")
                update_cam_health2("CAM3","NOTOK")
            else:
                try:
                    # convert the grab result to an OpenCV image
                    img = grab_result.Array
                    img = cv2.cvtColor(img, cv2.COLOR_BAYER_BG2BGR)
                    #resizing image to required resolution
                    img = cv2.resize(img, (1280, 1024))
                    
                    # save the image with the camera index as the file name
                    camera_id = camera.GetDeviceInfo().GetSerialNumber()  
                    if camera_id == csm1frontcam:
                        cv2.imwrite(f"{savePath1}CAM1/IMG_1.jpg",img)
                        shutil.move(f"{savePath1}CAM1/IMG_1.jpg", f"{savePath1}CAM1/TMP/IMG_1.jpg")                
                    elif camera_id == csm1s1cam:
                        cv2.imwrite(f"{savePath1}CAM2/IMG_1.jpg",img)
                        shutil.move(f"{savePath1}CAM2/IMG_1.jpg", f"{savePath1}CAM2/TMP/IMG_1.jpg")                
                    elif camera_id == csm1s2cam:
                        cv2.imwrite(f"{savePath1}CAM3/IMG_1.jpg",img)
                        shutil.move(f"{savePath1}CAM3/IMG_1.jpg", f"{savePath1}CAM3/TMP/IMG_1.jpg")                

                    elif camera_id == csm2frontcam:
                        cv2.imwrite(f"{savePath2}CAM1/IMG_1.jpg",img)
                        shutil.move(f"{savePath2}CAM1/IMG_1.jpg", f"{savePath2}CAM1/TMP/IMG_1.jpg")                
                    elif camera_id == csm2s1cam:
                        cv2.imwrite(f"{savePath2}CAM2/IMG_1.jpg",img)
                        shutil.move(f"{savePath2}CAM2/IMG_1.jpg", f"{savePath2}CAM2/TMP/IMG_1.jpg")                
                    elif camera_id == csm2s2cam:
                        cv2.imwrite(f"{savePath2}CAM3/IMG_1.jpg",img)
                        shutil.move(f"{savePath2}CAM3/IMG_1.jpg", f"{savePath2}CAM3/TMP/IMG_1.jpg")                

                    # file_name = f"{savePath}{camera_name}_{i+1}_frame.jpg"
                    # cv2.imwrite(file_name, img)
                    
                    # release the grab result and the camera buffer
                    grab_result.Release()
                    camera.StopGrabbing()
                    camera.StartGrabbingMax(1)
                except Exception as e:
                    print(e)
                    mv_logger.debug(" Grab Cameras"+str(e))
                    subprocess.call(["sh", restartFrameCapture])

        print(f"time for one loop : {int(time.time()*1000) - t1}")
    except Exception as e:
        mv_logger.debug(" Grab Cameras"+str(e))
         


def main():
    processID = os.getpid()
    updateProcessId(processID)
    # setup cameras
    cameras = setup_cameras()
    
    # setup camera parameters
    for camera in cameras:
        setup_camera_params(camera)
    
    # grab frames continuously
    while True:
        grab_frames(cameras)

if __name__ == "__main__":
    main()
