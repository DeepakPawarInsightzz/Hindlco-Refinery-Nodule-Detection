# from tendo import singleton
# me = singleton.SingleInstance()

import cv2
import time
import os
import threading
import logging
from pypylon import pylon
import traceback
import multiprocessing as mp
#for recording time limit
import queue
import shutil
import datetime
import pymysql
import signal
import subprocess

img_number=-1
async_q=queue.Queue()
grab_state=True
frame_ctr=0
mv_logger = None
frame_logger = None

topcam = "40267929"
top2cam = "40271836"
s1cam = "40271846"

exposure_topcam = 15000
exposure_top2cam = 15000
exposure_s1cam = 15000

fpsFloat = 1.00


processID = os.getpid()
print("This process has the PID", processID)


db_user = 'root'
db_pass = 'insightzz123'
db_host = '169.254.0.31'
db_name = 'Refinary3_CSM2'

savePath = "/home/nuc-ctrl/insightzz/code/FRAME_CAPTURE/"
restartFrameCapturePath = "/home/rfserver/insightzz/CSM2/code/SHELL_SCRIPT/restartFrameScript.sh"

class mvrecordingObj:
    global grab_state,mv_logger
    logging.basicConfig(filename="MV_RECORD_ACT_.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    mv_logger=logging.getLogger("MV_RECORD_ACT_")
    mv_logger.setLevel(logging.DEBUG)
    mv_logger.debug("CODE STARTED")    
    def __init__(self,vid_save_loc,vid_fl_prefx,vid_duration):
        global grab_state,mv_logger
        grab_state=True
        self.clear_raw_frames()
        processID = os.getpid()
        print("This process has the PID", processID)
        self.updateProcessId(processID)
        
        self.update_cam_health("CAM1","OK")
        self.update_cam_health("CAM2","OK")
        self.update_cam_health("CAM3","OK")
    
    def __del__(self):
        self.update_cam_health("CAM1","NOTOK")
        self.update_cam_health("CAM2","NOTOK")
        self.update_cam_health("CAM3","NOTOK")
        
    #================================== UPDATE PROCESS ID FUN ===================================================#
    def updateProcessId(self, processId):
        try:
            db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
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
    
    def update_cam_health(self,CAM,HEALTH_STATUS):
        db_fetch = pymysql.connect(host = db_host,
                                    user = db_user,
                                    password = db_pass,
                                    db = db_name)
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

    def init_cam(self):
        try:
            # Pypylon get camera by serial number
            top_cam = None
            top2_cam = None
            s1_cam = None

            for i in pylon.TlFactory.GetInstance().EnumerateDevices():
                if i.GetSerialNumber() == topcam:
                    try:
                        top_cam = i
     
                    except Exception as e:
                        print("top error: "+str(e))
                        mv_logger.debug("top error: "+str(e))
                        self.update_cam_health("CAM1","NOTOK")
                        
                elif i.GetSerialNumber() == top2cam:
                    try:
                        top2_cam = i
                        
                    except Exception as e:
                        print("in error: "+str(e))
                        mv_logger.debug("top2 error: "+str(e))
                        self.update_cam_health("CAM2","NOTOK")
                        
                elif i.GetSerialNumber() == s1cam:
                    try:
                        s1_cam = i
                    except Exception as e:
                        print("s1 error: "+str(e))
                        mv_logger.debug("s1 error: "+str(e))                        
                        self.update_cam_health("CAM3","NOTOK")
   
            self.startframegrabing(top_cam, top2_cam, s1_cam)
            
        except Exception as e:
            print("main() Exception : ", e)
            mv_logger.debug("main() Exception : "+str(e))
    
    def startframegrabing(self,top_cam,top2_cam, s1_cam):
        global FRAME_LOCATION
        try:
            image_no_counter = 1
            # VERY IMPORTANT STEP! To use Basler PyPylon OpenCV viewer you have to call .Open() method on you camera
            if top_cam is not None:
                try:
                    camera_top_cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(top_cam))
                    camera_top_cam.Open()
                    camera_top_cam.GevSCPSPacketSize.SetValue(1500)          
                    camera_top_cam.GevSCPD.SetValue(1000)          
                    camera_top_cam.GevSCFTD.SetValue(1000)          
                    camera_top_cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                    camera_top_cam.AcquisitionFrameRateEnable=True
                    camera_top_cam.AcquisitionFrameRateAbs=fpsFloat
                    camera_top_cam.ExposureTimeAbs.SetValue(exposure_topcam)                
                    camera_top_cam.ExposureTimeRaw.SetValue(exposure_topcam)             
                except Exception as e:
                    print("top error : "+str(e))
                    mv_logger.debug("top error : "+str(e))
                    self.update_cam_health("CAM1","NOTOK")

            if top2_cam is not None:
                try:
                    camera_top2_cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(top2_cam))
                    camera_top2_cam.Open()
                    camera_top2_cam.GevSCPSPacketSize.SetValue(1500)          
                    camera_top2_cam.GevSCPD.SetValue(1000)          
                    camera_top2_cam.GevSCFTD.SetValue(1000)          
                    camera_top2_cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                    camera_top2_cam.AcquisitionFrameRateEnable=True
                    camera_top2_cam.AcquisitionFrameRateAbs=fpsFloat
                    camera_top2_cam.ExposureTimeAbs.SetValue(exposure_top2cam)                
                    camera_top2_cam.ExposureTimeRaw.SetValue(exposure_top2cam)             
                except Exception as e:
                    print("top error : "+str(e))
                    mv_logger.debug("top error : "+str(e))
                    self.update_cam_health("CAM2","NOTOK")
                
            if s1_cam is not None:
                try:
                    camera_s1_cam = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(s1_cam))
                    camera_s1_cam.Open()
                    camera_s1_cam.GevSCPSPacketSize.SetValue(1500)          
                    camera_s1_cam.GevSCPD.SetValue(1000)          
                    camera_s1_cam.GevSCFTD.SetValue(1000)          
                    camera_s1_cam.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
                    camera_s1_cam.AcquisitionFrameRateEnable=True
                    camera_s1_cam.AcquisitionFrameRateAbs=fpsFloat
                    camera_s1_cam.ExposureTimeAbs.SetValue(exposure_s1cam)                
                    camera_s1_cam.ExposureTimeRaw.SetValue(exposure_s1cam)           
                except Exception as e:
                    print("s1 error : "+str(e))
                    mv_logger.debug("s1 error : "+str(e))
                    self.update_cam_health("CAM3","NOTOK")
                
                
            converter = pylon.ImageFormatConverter()
            converter.OutputPixelFormat = pylon.PixelType_BGR8packed
            converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
            
            top_once1 = True
            top_once2 = True

            top2_once1 = True
            top2_once2 = True

            s1_once1 = True
            s1_once2 = True

            while True:
                ############# CAM1 Post ###################
                total_t = int(time.time()*1000)
                try:
                    t1 = int(time.time()*1000) 
                    if camera_top_cam.IsGrabbing():
                        grabResult = camera_top_cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                    if grabResult.GrabSucceeded():
                        # Access the image data
                        image = converter.Convert(grabResult)
                        img = image.GetArray()
                        img = cv2.resize(img, (1280, 1024))
                        #img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                        #cv2.imshow("img", img)
                        #cv2.putText(img,str(time.time())[8:-5], (20, 80),
                                    #cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)
                        cv2.imwrite(f"{savePath}CAM1/IMG_"+str(image_no_counter)+".jpg",img)
                        if image_no_counter == 1:
                            shutil.move(f"{savePath}CAM1/IMG_"+str(image_no_counter)+".jpg", f"{savePath}CAM1/TMP/IMG_"+str(image_no_counter)+".jpg")                
                    if(top_cam is not None):
                        grabResult.Release()
                    #print("time for camera_top_cam frame : ", int(time.time()*1000) - t1) 
                    top_once1 = True
                    if top_once2:
                        top_once2 = False
                except Exception as e:
                    if top_once1:
                        top_once2 = True
                        print("Exception cam1 ", e)
                        mv_logger.debug("Exception cam1 "+str(e))  
                        top_once1 = False
                        # self.update_cam_health("CAM1","NOTOK")
                    subprocess.call(["sh", restartFrameCapturePath])
                
                ############# CAM2 Post ###################
                total_t = int(time.time()*1000)
                try:
                    t1 = int(time.time()*1000) 
                    if camera_top2_cam.IsGrabbing():
                        grabResult = camera_top2_cam.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                    if grabResult.GrabSucceeded():
                        # Access the image data
                        image = converter.Convert(grabResult)
                        img = image.GetArray()
                        #img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                        #cv2.imshow("img", img)
                        #cv2.putText(img,str(time.time())[8:-5], (20, 80),
                                    #cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)
                        cv2.imwrite(f"{savePath}CAM2/IMG_"+str(image_no_counter)+".jpg",img)
                        if image_no_counter == 1:
                            shutil.move(f"{savePath}CAM2/IMG_"+str(image_no_counter)+".jpg", f"{savePath}CAM2/TMP/IMG_"+str(image_no_counter)+".jpg")                
                    if(top2_cam is not None):
                        grabResult.Release()
                    #print("time for camera_top_cam frame : ", int(time.time()*1000) - t1) 
                    top2_once1 = True
                    if top2_once2:
                        top2_once2 = False
                except Exception as e:
                    if top2_once1:
                        top2_once2 = True
                        print("Exception cam2 ", e)
                        mv_logger.debug("Exception cam2 "+str(e))  
                        top2_once1 = False
                        # self.update_cam_health("CAM2","NOTOK")
                    subprocess.call(["sh", restartFrameCapturePath])
                
                ############## CAM3 ###################
                try:
                    t1 = int(time.time()*1000) 
                    if camera_s1_cam.IsGrabbing():
                        grabResult = camera_s1_cam.RetrieveResult(10000, pylon.TimeoutHandling_ThrowException)
                    if grabResult.GrabSucceeded():
                        # print("s1 succed")
                        # Access the image data
                        image = converter.Convert(grabResult)
                        img = image.GetArray()
                        #img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                        #img = img[455:755, 0:1440]                        
                        #cv2.imshow("img", img)
                        #cv2.putText(img,str(time.time())[8:-5], (20, 80),
                                    #cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2, cv2.LINE_AA)
                        cv2.imwrite(f"{savePath}CAM3/IMG_"+str(image_no_counter)+".jpg",img)
                        if image_no_counter == 1:
                            shutil.move(f"{savePath}CAM3/IMG_"+str(image_no_counter)+".jpg", f"{savePath}CAM3/TMP/IMG_"+str(image_no_counter)+".jpg")                
                    if(s1_cam is not None):
                        grabResult.Release()
                    #print("time for camera_s1_cam frame : ", int(time.time()*1000) - t1) 
                    s1_once1 = True
                    if s1_once2:
                        s1_once2 = False
                except Exception as e:
                    if s1_once1:
                        s1_once2 = True
                        print("Exception cam3 ", e)
                        mv_logger.debug("Exception in cam3 "+str(e))  
                        s1_once1 = False
                        # self.update_cam_health("CAM3","NOTOK")
                    subprocess.call(["sh", restartFrameCapturePath])

                # print(f"total time at {datetime.datetime.now()} : ", int(time.time()*1000) - total_t) 
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            if(camera_top_cam is not None):
                camera_top_cam.StopGrabbing()
                camera_top_cam.close() 
            if(camera_top2_cam is not None):
                camera_top2_cam.StopGrabbing()
                camera_top2_cam.close()            
            if(camera_s1_cam is not None):
                camera_s1_cam.StopGrabbing()
                camera_s1_cam.close() 
        except Exception as e:
            print("after while  Exception : ", e)
            mv_logger.debug("after while  Exception : "+str(e))
            threading.Timer(10.0,self.init_cam()).start()
            
    def clear_raw_frames(self):
        pass
            
        
    def run_module(self):
        #mv_logger.debug("MV Record Process Started")
        self.init_cam()
        #mv_logger.debug("Process ended")      

def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper

def call_error(cam_pos):
    print("Error in function my function "+str(cam_pos))

if __name__=="__main__":
    obj1=mvrecordingObj(os.getcwd(), "FNL_TST", 60)
    obj1.run_module()
