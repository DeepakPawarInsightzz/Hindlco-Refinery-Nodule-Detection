from tendo import singleton
me = singleton.SingleInstance()


from cgi import test
import cv2
import os
os.environ['CUDA_VISIBLE_DEVICES']='1'
from matplotlib.pyplot import draw
import numpy as np
import time
import datetime
import glob
import logging
import json
from io import StringIO
from numpy import number, real_if_close 
from skimage import io
import PIL
import numpy
import multiprocessing 


#for maskrcnn
# import some common detectron2 utilities
from detectron2.utils.logger import setup_logger
from torch import mm
setup_logger()
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog, DatasetCatalog
from detectron2.structures import BoxMode
from detectron2.engine import DefaultTrainer
from detectron2.utils.visualizer import Visualizer, ColorMode
from detectron2.data.datasets import register_coco_instances

#getting path from configurations file
#============================= Getting data from xml ==========================================#
config_path = os.path.join("/home/rfserver/insightzz/CSM1/code/DETECTION/detection_cam2.xml")
import ast
import xml.etree.ElementTree as ET
config_parse = ET.parse(config_path)
config_root = config_parse.getroot()
code_path = config_root[0].text

#DB credentials
import pymysql
db_user = config_root[1].text
db_pass = config_root[2].text
db_host = config_root[3].text
db_name = config_root[4].text

#model configurations
CONFIG_PATH = config_root[5].text
model_file = config_root[6].text
thr_acc = float(config_root[7].text)
mask_model_path = config_root[8].text
class_json = config_root[9].text

#image path and defected image folder path
im1_path = config_root[10].text
im2_path = config_root[11].text
im3_path = config_root[12].text
defect_image_dir = config_root[13].text

#=========== frame check =================#
total_frame = int(config_root[14].text)
check_frame = int(config_root[15].text)

#======== inspected_region x =============#
max_x = 603
min_x = 310

# logging.basicConfig(filename=code_path+"DEFECTLOG_.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.basicConfig(filename=os.path.join(code_path, "cam3Detect.log"),filemode='a',format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
dalogger=logging.getLogger("cam3Detect")
dalogger.setLevel(logging.CRITICAL) #CRITICAL #DEBUG

dataSavePath = "/home/rfserver/insightzz/CSM1/code/DETECTION/DataReview/cam1Data/"

processID = os.getpid()
print("This process has the PID", processID)

textFilePath = "/home/rfserver/insightzz/CSM1/code/DETECTION/tempCam"
trigger_file_path = "/home/rfserver/insightzz/CSM1/code/PLC/triggerFile"

#for file transfer of processed images
import pysftp
Hostname = "169.254.0.32"
Username = "nuc-ctrl"
Password = "hindalco@123"
try:
    cnopts = pysftp.CnOpts()
    cnopts.hostkeys.load("/home/rfserver/insightzz/CSM1/code/DETECTION/id_rsa")
    sftp = pysftp.Connection(host=Hostname, username=Username, password=Password,cnopts=cnopts)
except Exception as e:
    print(f"Exception in sftp connection : {e}")
    dalogger.critical(f"Exception in sftp connection : {e}")
imgPath = "/home/rfserver/insightzz/CSM1/code/NUCCTRL_TRANSFER/CAM3/TMP.jpg"
remotePath = "/home/nuc-ctrl/insightzz/code/PROCESSED_IMAGES/CAM3/TMP.jpg"

#================================== UPDATE PROCESS ID FUN ===================================================#
def updateProcessId(processId):
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                     user=db_user,         # your username
                     passwd=db_pass,  # your password
                     db=db_name)
        cur = db_update.cursor()
        query = f"UPDATE PROCESS_ID_TABLE set PROCESS_ID = {str(processId)} where PROCESS_NAME = 'ALGORITHM_CAM3'"
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()
        #print(data_set)
    except Exception as e:
        print(f"Exception in update process id : {e}")
        cur.close()

#================================== getting last Defect_size information ===================================================#
def get_config_info():
    try:
        db_fetch = pymysql.connect(host=db_host,    # your host, usually localhost
                     user=db_user,         # your username
                     passwd=db_pass,  # your password
                     db= db_name)
        cur = db_fetch.cursor()
        query = f"select ID, DEFECT_SIZE  from Refinary3_CSM1.CONFIGURATIONS_Test  order by ID desc limit 1;"
        cur.execute(query)
        data_set = cur.fetchall()
        cur.close()
        db_fetch.close()
        return data_set[0][1]
    except Exception as e:
        print(e)
        dalogger.critical(f"Exception in get Auto: {e}")

#================================== getting last Auto information ===================================================#
def get_Auto_info():
    try:
        db_fetch = pymysql.connect(host=db_host,    # your host, usually localhost
                     user=db_user,         # your username
                     passwd=db_pass,  # your password
                     db= db_name)
        cur = db_fetch.cursor()
        query = f"select ID, Status from Auto order by ID desc limit 1;"
        cur.execute(query)
        data_set = cur.fetchall()
        cur.close()
        db_fetch.close()
        return data_set[0][1]
    except Exception as e:
        print(e)
        dalogger.critical(f"Exception in get Auto: {e}")
#================================== getting last configurations ===================================================#
def get_configid():
    try:
        db_fetch = pymysql.connect(host=db_host,    # your host, usually localhost
                     user=db_user,         # your username
                     passwd=db_pass,  # your password
                     db= db_name)
        cur = db_fetch.cursor()
        query = f"select ID, DEFECT_SIZE, NUMBER_OF_DEFECTS from CONFIGURATIONS order by ID desc limit 1"
        cur.execute(query)
        data_set = cur.fetchall()
        cur.close()
        db_fetch.close()
        return data_set[0][0],data_set[0][1], data_set[0][2] 
    except Exception as e:
        print(e)
        dalogger.critical(f"get config id function : {e}")    # out.release()

def updateTotalCount():
    total = 0
    #================== checking date of last inserted row in count table =================#
    try:
        db_fetch = pymysql.connect(host=db_host,    # your host, usually localhost
                     user=db_user,         # your username
                     passwd=db_pass,  # your password
                     db=db_name)
        cur = db_fetch.cursor()
        query = f"select ID, TOTAL from COUNT_TABLE order by ID desc limit 1"
        cur.execute(query)
        # print(query)
        data_set = cur.fetchall()
        cur.close()
        db_fetch.close()
        last_id = data_set[0][0]
        total_prev = data_set[0][1]
    except Exception as e:
        print(e)
        dalogger.critical(f"update count table function : {e}")    # out.release()
    #adding one to total
    total = total_prev+1
    #updating the count table
    #=================== updating count table =================#
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                    user=db_user,         # your username
                    passwd=db_pass,  # your password
                    db=db_name)
        cur = db_update.cursor()
        query = f"UPDATE COUNT_TABLE set TOTAL={total} where ID = {last_id}"
        # print(query)
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()
    except Exception as e:
        print(f"Exception in update process id : {e}")
        dalogger.critical(f"update count table function : {e}")    # out.release()

def updatePassCount():
    passed = 0
    #================== checking date of last inserted row in count table =================#
    try:
        db_fetch = pymysql.connect(host=db_host,    # your host, usually localhost
                     user=db_user,         # your username
                     passwd=db_pass,  # your password
                     db=db_name)
        cur = db_fetch.cursor()
        query = f"select ID, PASSED from COUNT_TABLE order by ID desc limit 1"
        cur.execute(query)
        data_set = cur.fetchall()
        cur.close()
        db_fetch.close()
        last_id = data_set[0][0]
        passed_prev = data_set[0][1]
    except Exception as e:
        print(e)
        dalogger.critical(f"update count table function : {e}")    # out.release()
    #adding one to total
    passed = passed_prev+1
    #updating the count table
    #=================== updating count table =================#
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                    user=db_user,         # your username
                    passwd=db_pass,  # your password
                    db=db_name)
        cur = db_update.cursor()
        query = f"UPDATE COUNT_TABLE set PASSED={passed} where ID = {last_id}"
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()
    except Exception as e:
        print(f"Exception in update process id : {e}")
        dalogger.critical(f"update count table function : {e}")    # out.release()

def updateRejectCount():
    rejected = 0
    #================== checking date of last inserted row in count table =================#
    try:
        db_fetch = pymysql.connect(host=db_host,    # your host, usually localhost
                     user=db_user,         # your username
                     passwd=db_pass,  # your password
                     db=db_name)
        cur = db_fetch.cursor()
        query = f"select ID, REJECTED from COUNT_TABLE order by ID desc limit 1"
        cur.execute(query)
        data_set = cur.fetchall()
        cur.close()
        db_fetch.close()
        last_id = data_set[0][0]
        rejected_prev = data_set[0][1]
    except Exception as e:
        print(e)
        dalogger.critical(f"update count table function : {e}")    # out.release()
    #adding one to total
    rejected = rejected_prev+1
    #updating the count table
    #=================== updating count table =================#
    try:
        db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                    user=db_user,         # your username
                    passwd=db_pass,  # your password
                    db=db_name)
        cur = db_update.cursor()
        query = f"UPDATE COUNT_TABLE set REJECTED={rejected} where ID = {last_id}"
        cur.execute(query)
        db_update.commit()
        cur.close()
        db_update.close()
    except Exception as e:
        print(f"Exception in update process id : {e}")
        dalogger.critical(f"update count table function : {e}")    # out.release()

#==================== Logging into mysql ================================#
def logDefectsDetailsInDB(CONFIG_ID, CAMERA, IMAGE_LINK, DEFECT_TYPE, DEFECT_SIZE, NO_OF_DEFECTS, IS_RECORD_DEFECTED):
    # print("Inside logDefectsDetailsInDB")
    p1 = multiprocessing.Process(target=logDefectsDetailsInDBInThread, args=(
        CONFIG_ID, CAMERA, IMAGE_LINK, DEFECT_TYPE, DEFECT_SIZE, NO_OF_DEFECTS, IS_RECORD_DEFECTED,))
    p1.start()

def logDefectsDetailsInDBInThread(CONFIG_ID, CAMERA, IMAGE_LINK, DEFECT_TYPE, DEFECT_SIZE, NO_OF_DEFECTS, IS_RECORD_DEFECTED):
    #=================== checking if the image has been already logged or not ======================#
    try:
        db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                     user=db_user,         # your username
                     passwd=db_pass,  # your password
                     db=db_name)
        cur = db_select.cursor()
        query = f"select ID, IMAGE_LINK from PROCESSING_TABLE order by ID desc limit 1"
        cur.execute(query)
        data_set = cur.fetchall()
        # print(len(data_set))
        # print(data_set)
        cur.close()
        db_select.close()
    except Exception as e:
        print(e)
        dalogger.critical(f"logdefect function : {e}")    # out.release()

    if len(data_set) == 0 or data_set[0][1] != IMAGE_LINK:
    #===================== inserting defect row =============================#
        try:
            db_insert = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
            cur = db_insert.cursor()
            query = f"insert into PROCESSING_TABLE \
            (CONFIG_ID, CAMERA, IMAGE_LINK, DEFECT_TYPE, DEFECT_SIZE, NO_OF_DEFECTS, IS_RECORD_DEFECTED)\
            values ({CONFIG_ID},'{CAMERA}','{IMAGE_LINK}','{DEFECT_TYPE}','{DEFECT_SIZE}',{NO_OF_DEFECTS},{IS_RECORD_DEFECTED})"
            # print(query)
            cur.execute(query)
            db_insert.commit()
            cur.close()
            db_insert.close()
        except Exception as e:
            print(e)
            dalogger.critical(f"logdefect function : {e}")    # out.release()

    else:
        #==================== update the last row ==============================#
        try:
            db_update = pymysql.connect(host=db_host,    # your host, usually localhost
                        user=db_user,         # your username
                        passwd=db_pass,  # your password
                        db=db_name)
            cur = db_update.cursor()
            query = f"update PROCESSING_TABLE set CONFIG_ID={CONFIG_ID}, CAMERA='{CAMERA}', DEFECT_TYPE='{DEFECT_TYPE}',\
                DEFECT_SIZE='{DEFECT_SIZE}', NO_OF_DEFECTS={NO_OF_DEFECTS} where IMAGE_LINK='{IMAGE_LINK}'"
            # print(query)
            cur.execute(query)
            db_update.commit()
            cur.close()
            db_update.close()
        except Exception as e:
            print(e)
            dalogger.critical(f"logdefect function : {e}")    # out.release()

class maskRCNN:
    def __init__(self):
        global mask_model_path
        self.predictor=None
        self.mrcnn_config_fl=CONFIG_PATH
        self.mrcnn_model_loc= mask_model_path
        self.mrcnn_model_fl= model_file
        self.detection_thresh= thr_acc
        self.register_modeldatasets()

    def __loadLablMap__(self):
        #load labelmap
        with open(class_json,"r") as fl:
            self.labelMap=json.load(fl)
        return self.labelMap

    def register_modeldatasets(self):
        d="test"
        self.labelMap = self.__loadLablMap__()
        self.class_list=list(self.labelMap.values())
        MetadataCatalog.get("brake_" + d).set(thing_classes=self.class_list)
        self.railway_metadata = MetadataCatalog.get("brake_test")
        #Start config for inf
        cfg = get_cfg()
        cfg.merge_from_file(self.mrcnn_config_fl)
        # cfg.merge_from_list(["MODEL.DEVICE", "cpu"])
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = len(self.labelMap)  # only has one class (ballon)
        cfg.OUTPUT_DIR=self.mrcnn_model_loc
        cfg.MODEL.WEIGHTS =os.path.join(cfg.OUTPUT_DIR,self.mrcnn_model_fl)
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = self.detection_thresh
        self.predictor = DefaultPredictor(cfg)

    def sort_x(self, labellist):
        #=========== sorting according to xmin in ascending order starts ==================#
        len_labellist = len(labellist)
        for numbi in range(0, len_labellist):
            for numbj in range(0, len_labellist - numbi -1):
                if (int(labellist[numbj][7])) > int(labellist[numbj+1][7]):
                    tempo = labellist[numbj]
                    labellist[numbj] = labellist[numbj+1]
                    labellist[numbj+1] = tempo
        return labellist

    def run_inference(self,img):
        try:
            output = self.predictor(img)
            predictions=output["instances"].to("cpu")
            classes = predictions.pred_classes.numpy()

            #for counting number of items
            class_list = []
            for i in classes:
                class_list.append(self.railway_metadata.get("thing_classes")[i])
            class_dict = {} 
            for item in class_list: 
                if (item in class_dict): 
                    class_dict[item] += 1
                else: 
                    class_dict[item] = 1        
            
            boxes_surface = output["instances"].pred_boxes.tensor.to("cpu").numpy()
            pred_class_surface = output["instances"].pred_classes.to("cpu").numpy()
            scores_surface = output["instances"].scores.to("cpu").numpy()
            mask_surface = output['instances'].pred_masks.to("cpu").numpy()

            if predictions.has("pred_masks"):
                masks = predictions.pred_masks.numpy()

            labellist = []
            for i,box in enumerate(boxes_surface):
                class_name = self.railway_metadata.get("thing_classes")[pred_class_surface[i]]

                mask = masks[i]
                mask = mask.astype(int)
                mask = np.array(mask).astype('uint8')
                mask_true = np.where(mask == 1)

                # Threshold the grayscale image to create a binary mask
                ret, thresh = cv2.threshold(mask, 0, 1, cv2.THRESH_BINARY)
                # Find the contours of the binary mask
                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                score = scores_surface[i]
                box = boxes_surface[i]
                ymin = int(box[1])
                xmin = int(box[0])
                ymax = int(box[3])
                xmax = int(box[2])
                cx, cy = get_centroid(xmin, xmax, ymin, ymax)
                labellistsmall = []
                labellistsmall.append(score)
                labellistsmall.append(ymin)
                labellistsmall.append(ymax)
                labellistsmall.append(xmin)
                labellistsmall.append(xmax)
                labellistsmall.append(class_name)
                labellistsmall.append(cy)
                labellistsmall.append(cx)
                labellistsmall.append([xmax-xmin,ymax-ymin])
                labellistsmall.append(mask_true)
                labellistsmall.append(contours)
                labellist.append(labellistsmall)

            out_img=img.copy()
            # visualizer = Visualizer(out_img[:, :, ::-1], metadata=self.railway_metadata, scale=1, instance_mode=ColorMode.IMAGE)
            # out_img = visualizer.draw_instance_predictions(output["instances"].to("cpu"))
            # img = np.array(out_img.get_image()[:, :, ::-1])
            labellist = self.sort_x(labellist)
            return img, labellist
        except Exception as e:
            print(f"Exception in run inference : {e}")
            dalogger.critical(f"Exception run inference : {e}")

def get_mm_from_pixel(x,y):
    mm_per_pixel = 1000/700
    return int(x*mm_per_pixel), int(y*mm_per_pixel)

def get_centroid(xmin, xmax, ymin, ymax):
    cx = int((xmin + xmax) / 2.0)
    cy = int((ymin + ymax) / 2.0)
    return(cx, cy)

def draw_rectangle(img_rd, class_name, ymin, ymax, xmin, xmax, score, color, defect_size):
    # class_name = class_name+" "+str(score)[:4] 
    class_name = str(defect_size) 

    fontsize_x = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][0]
    fontsize_y = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0][1]
    # cv2.rectangle(img_rd, (xmin,ymin), (xmax,ymax),( int(color[0]),int(color[1]),int(color[2])),2)   
    cv2.rectangle(img_rd, (xmin,ymin), ((xmin+fontsize_x),int(ymin-15)), ( int(color[0]),int(color[1]),int(color[2])),-1)
    cv2.putText(img_rd, class_name,(xmin,int(ymin)) ,cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.FILLED)
    return img_rd

def getimagelink(parentdir):
    try:
        dirname = datetime.datetime.now().strftime('%Y-%m-%d')+"/CAM3"
        dirpath = os.path.join(parentdir, dirname)
        imagename = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')+".jpg"
        real_imagename = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')+"_real.jpg"

        imagepath = os.path.join(dirpath,imagename)
        real_imagepath = os.path.join(dirpath,real_imagename)
        return dirpath, imagepath, real_imagepath
    except Exception as e:
        print(e)

def returnLen(label, plate_list):
    try:
        noduleY, noduleX = label[6],label[7]
        # print(noduleY,noduleX)
        xlistArray = np.where(plate_list[0][9][1] == label[7])
        ylistArray = np.where(plate_list[0][9][0] == label[6])
        # print(np.max(xlistArray[0]),np.min(xlistArray[0]),np.max(ylistArray[0]),np.min(ylistArray[0]))
        xmaxIn, xminIn, ymaxIn, yminIn = np.max(xlistArray[0]),np.min(xlistArray[0]),np.max(ylistArray[0]),np.min(ylistArray[0])
        plateYmax, plateYmin, plateXmax, plateXmin = plate_list[0][9][0][xmaxIn],plate_list[0][9][0][xminIn],plate_list[0][9][1][ymaxIn],plate_list[0][9][1][yminIn]
        # print(plateYmax - plateYmin, plateXmax - plateXmin)
        yPixByMM = (plateYmax - plateYmin)/800
        # print(yPixByMM)
        yMM = int(label[8][1]/yPixByMM)
        xMM = int(label[8][0]/yPixByMM)
        # print(xMM, yMM)
        return xMM, yMM
    except Exception as e:
        print(f"Exception in returnLen : {e}")
            # out.release()
        return 0,0
    
def getDistFromLine(point, line1_point_1, line1_point_2, line2_point_1, line2_point_2):
    #================== for first line ===================
    # Calculate the slope of the line
    if (line1_point_2[1] - line1_point_1[1]) != 0 and (line1_point_2[0] - line1_point_1[0]) != 0:
        m1 = (line1_point_2[1] - line1_point_1[1]) / (line1_point_2[0] - line1_point_1[0])
    else:
        m1 = 0
    # Calculate the y-intercept of the line
    b = line1_point_1[1] - m1 * line1_point_1[0]
    # Given a point (x,y), calculate its y-coordinate on the line
    x = point[0]
    y1 = point[1]
    y1_line = m1 * x + b        

    #================== for Second line ===================
    # Calculate the slope of the line
    if (line2_point_2[1] - line2_point_1[1]) != 0 and (line2_point_2[0] - line2_point_1[0]) != 0:
        m2 = (line2_point_2[1] - line2_point_1[1]) / (line2_point_2[0] - line2_point_1[0])
    else:
        m2 = 0
    # Calculate the y-intercept of the line
    b = line2_point_1[1] - m2 * line2_point_1[0]
    # Given a point (x,y), calculate its y-coordinate on the line
    x = point[0]
    y2 = point[1]
    y2_line = m2 * x + b

    if m1 == 0 and y2 < y2_line:
        return True
    if y1 > y1_line and y2 < y2_line:
        return True
    if y1 > y1_line and m2 == 0:
        return True
    else:
        return False

def getAreaDictNodule(noduleListRefined, topPoints, bottomPoints, rightPoints, leftPoints):
    area1 = 0
    area2 = 0    
    area3 = 0
    area4 = 0
    area5 = 0

    pointReturn = []

    # cv2.line(im, topPoints[2],leftPoints[2],(255,0,0),1,lineType=cv2.LINE_AA)
    # cv2.line(im, topPoints[4],leftPoints[4],(255,0,0),1,lineType=cv2.LINE_AA)

    # cv2.line(im, rightPoints[1],bottomPoints[1],(255,0,0),1,lineType=cv2.LINE_AA)
    # cv2.line(im, rightPoints[3],bottomPoints[3],(255,0,0),1,lineType=cv2.LINE_AA)

    for nodule in noduleListRefined:
        point = (nodule[7],nodule[6])

        #========== FOR AREA 1 
        areaBool = getDistFromLine(point, topPoints[0].tolist(), leftPoints[0].tolist(), topPoints[2].tolist(), leftPoints[2].tolist())
        if areaBool == True:
            area1 = area1 + 1

        #========== FOR AREA 2
        areaBool = getDistFromLine(point, topPoints[2].tolist(), leftPoints[2].tolist(), topPoints[4].tolist(), leftPoints[4].tolist())
        if areaBool == True:
            area2 = area2 + 1

        #========== FOR AREA 3
        areaBool = getDistFromLine(point, topPoints[4].tolist(), leftPoints[4].tolist(), rightPoints[1].tolist(), bottomPoints[1].tolist())
        if areaBool == True:
            area3 = area3 + 1

        #========== FOR AREA 4
        areaBool = getDistFromLine(point, rightPoints[1].tolist(), bottomPoints[1].tolist(), rightPoints[3].tolist(), bottomPoints[3].tolist())
        if areaBool == True:
            area4 = area4 + 1

        #========== FOR AREA 5
        areaBool = getDistFromLine(point, rightPoints[3].tolist(), bottomPoints[3].tolist(), rightPoints[5].tolist(), bottomPoints[5].tolist())
        if areaBool == True:
            area5 = area5 + 1

    return [area1, area2, area3, area4, area5]

def getQuadPoints(approx):
    try:
        #=========== Sorting according to x 
        # Get the indices that would sort the original array
        sort_indices = np.argsort(approx[:, 0, 0])
        # Sort the original array using the indices
        sorted_array = approx[sort_indices]

        #========== getting x differences for serpating left and right Part
        diff = np.diff(sorted_array[:, :, 0], axis=0)
        maxIndex = np.argmax(diff)
        left = sorted_array[:maxIndex+1, :]
        right = sorted_array[maxIndex+1:, :]

        #=========== Sorting left array according to y  
        # Get the indices that would sort the original array
        sort_indices = np.argsort(left[:, 0, 1])
        # Sort the original array using the indices
        leftArray = left[sort_indices]

        #=========== Sorting left array according to y  
        # Get the indices that would sort the original array
        sort_indices = np.argsort(right[:, 0, 1])
        # Sort the original array using the indices
        rightArray = right[sort_indices]

        # print(f"left : {leftArray}")
        # print(f"right : {rightArray}")

        #getting y differences in left for seperating top and bottom part
        diff = np.diff(leftArray[:, :, 1], axis=0)
        maxIndex = np.argmax(diff)
        top = leftArray[:maxIndex+1, :]
        bottom = leftArray[maxIndex+1:, :]
        topLeft = top[0][0]
        bottomLeft = bottom[-1][0]

        #getting y differences in left for seperating top and bottom part
        diff = np.diff(rightArray[:, :, 1], axis=0)
        maxIndex = np.argmax(diff)
        top = rightArray[:maxIndex+1, :]
        bottom = rightArray[maxIndex+1:, :]
        topRight = top[0][0]
        bottomRight = bottom[-1][0]

        return topRight,bottomRight,bottomLeft,topLeft
    except Exception as e:
        return 0

def main():
    try:
        updateProcessId(processID)

        #=============== GET CONFIGURATION =======================#
        config_id, defect_size_sql, number_of_defects = get_configid()
        print(config_id, defect_size_sql, number_of_defects)
        config_timer = 5000
        config_time = int(time.time()*1000)

        status = get_Auto_info()

        Defect_size=get_config_info()
        Defect_size=int(Defect_size)

        # Creating inference class object
        mask_object = maskRCNN()

        #Variables for plate counting
        plateCounter = 0
        plateAbsentCounter = 0
        plateCounterBool = True

        #Variable for couting max nodules for Given plate
        prevNoduleCount = 0

        # for detecting corrupt image
        imgsize1 = 0
        imgsize2 = 1
        image_read = False

        #defectBool for counting rejected and passed
        defectBool = False
        updateCountBool = False

        while True:
            status = get_Auto_info()
            Defect_size=get_config_info()
            Defect_size=int(Defect_size)
            #=============== UPDATE CONFIGURATIONS EVERY 5 SECONDS CONFIGURATION =======================#
            if int(time.time()*1000) - config_time > config_timer:
                config_time = int(time.time()*1000)
                config_id, defect_size_sql, number_of_defects = get_configid()
                print(config_id, defect_size_sql, number_of_defects)

            # # For checking the image is complete or not
            # with open((im3_path), 'rb') as f:
            #     f.seek(-2,2)
            #     if f.read() != b'\xff\xd9':
            #         print('Not complete image')
            #         image_read = False
            #     else:
            #         try:
            #             imgsize1 = os.path.getsize(im3_path)
            #             if imgsize1 != imgsize2:
            #                 im = cv2.imread(im3_path)
            #                 image_read = True
            #                 imgsize2 = imgsize1
            #             else:
            #                 image_read = False
            #         except cv2.error as e:
            #             print("error is ", e)
            #             image_read = False

            # #if not complete then return
            # if image_read == False:
            #     continue
            im = cv2.imread(im3_path)
                
            #Creating a copy for saving original image
            imReal = im.copy()

            #detection and getting labelist
            im, labellist = mask_object.run_inference(im)
            plate_list = []
            nodule_list = []
            noCopperList = []
            
            #getting the platelist and nodulelist
            for index, labelsmalllist in enumerate(labellist):
                if labelsmalllist[5] == "plate":
                    plate_list.append(labelsmalllist)
                elif labelsmalllist[5] == "nodule":
                    nodule_list.append(labelsmalllist)
                elif labelsmalllist[5] == "nocopper":
                    noCopperList.append(labelsmalllist)


            # #Ratio condition for removing false positive of plate
            # plate_list1 = []
            # if len(plate_list) > 1:
            #     for index, plateSmallList in enumerate(plate_list):
            #         print(plateSmallList[8][0]/plateSmallList[8][1])
            #         if plateSmallList[8][0]/plateSmallList[8][1] > 1.5:
            #                 plate_list.pop(index)
            # plate_list = []
            # plate_list = plate_list1

            #Returning if no plate detected
            if len(plate_list) > 0:
            
                #getting only single plate if multiple detection of plate happens
                plate_list = [plate_list[0]]

                # print(plate_list[0][7])

                #checking the plate position in the defined ROI
                if max_x > plate_list[0][7] > min_x:
                    #Saving the plate with no copper 
                    try:
                        for count, noCu in enumerate(noCopperList):
                            if plate_list[0][1] < noCu[6] < plate_list[0][2] and plate_list[0][3] < noCu[7] < plate_list[0][4]:
                                color = tuple(COLORS[count])
                                im = cv2.drawContours(im, plate[10], -1, (255,255,0), 2)
                                cv2.imwrite(f"{imagepath[:-4]}_noCopper.jpg", im)
                                cv2.imwrite(f"{real_imagepath[:-4]}_noCopper.jpg", imReal)
                    except Exception as e:
                        dalogger.critical(f"transfer error : {e}")    # out.release()                

                    #Condition for counting plate
                    if plateCounterBool == True:
                        plateCounter += 1
                        plateCounterBool = False
                        plateAbsentCounter += 0
                        print(plateCounter)
                        #updating total count
                        # updateTotalCount()
                        #creating path for defect image
                        dirname, imagepath, real_imagepath = getimagelink(defect_image_dir)
                        updateCountBool = False

                    #Drawing bouding box around plate
                    np.random.seed(100)
                    COLORS = np.random.randint(70, 255, size=(200, 3),dtype="uint8")
                    for countplate, plate in enumerate(plate_list):
                        color = tuple(COLORS[countplate])
                        im = draw_rectangle(im, plate[5],plate[1], plate[2], plate[3], plate[4], plate[0], color, plate[8])
                        # print(plate[8][0]/plate[8][1])

                    #Drawing bouding box around plate
                    np.random.seed(100)
                    COLORS = np.random.randint(70, 255, size=(200, 3),dtype="uint8")
                    for countplate, plate in enumerate(plate_list):
                            color = tuple(COLORS[countplate])
                            # Find the convex hull of the contour
                            hull = cv2.convexHull(plate[10][0])
                            cv2.drawContours(im, [hull], 0, (0, 255, 0), 2, lineType=cv2.LINE_AA)
                            # Approximate the contour with a quadrilateral
                            epsilon = 0.02 * cv2.arcLength(hull, True)
                            approx = cv2.approxPolyDP(hull, epsilon, True)
                            if len(approx) >= 4:
                                    try:
                                        topRight,bottomRight,bottomLeft,topLeft = getQuadPoints(approx)
                                    
                            
                                        # Get equidistant points on the right side line
                                        num_points1 = 6
                                        rightPoints = np.linspace(topRight, bottomRight, num_points1, dtype=np.int32)
                                        # Get equidistant points on the left side line
                                        num_points2 = 6
                                        leftPoints = np.linspace(topLeft, bottomLeft, num_points2, dtype=np.int32)
                                        # Get equidistant points on the top side line
                                        num_points3 = 6
                                        topPoints = np.linspace(topLeft, topRight, num_points3, dtype=np.int32)
                                        # Get equidistant points on the bottom side line
                                        num_points4 = 6
                                        bottomPoints = np.linspace(bottomLeft, bottomRight, num_points4, dtype=np.int32)
                                        cv2.line(im,tuple(topPoints[2]),tuple(leftPoints[2]),(255,0,0),1,lineType=cv2.LINE_AA)
                                        cv2.line(im, tuple( topPoints[4]),tuple(leftPoints[4]),(255,0,0),1,lineType=cv2.LINE_AA)
                                        cv2.line(im,tuple( rightPoints[1]),tuple(bottomPoints[1]),(255,0,0),1,lineType=cv2.LINE_AA)
                                        cv2.line(im, tuple(rightPoints[3]),tuple(bottomPoints[3]),(255,0,0),1,lineType=cv2.LINE_AA)

                                        #checking if nodules are in the bounding box of plate
                                        noduleListRefined = []
                                        for count, nodule  in enumerate(nodule_list):
                                            dist = cv2.pointPolygonTest(approx, (nodule[7],nodule[6]), True)
                                            if dist > 0:
                                                noduleListRefined.append(nodule)

                                        areaList = []
                                        areaList = getAreaDictNodule(noduleListRefined, topPoints, bottomPoints, rightPoints, leftPoints)
                                        # print(areaList)
                                        cv2.putText(im, f"area1: {areaList[0]}",tuple(topPoints[0]) ,cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100,0,0), 2, cv2.FILLED)
                                        cv2.putText(im, f"area2: {areaList[1]}",tuple(topPoints[2]) ,cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100,0,0), 2, cv2.FILLED)
                                        cv2.putText(im, f"area3: {areaList[2]}",tuple(topPoints[4]) ,cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100,0,0), 2, cv2.FILLED)
                                        cv2.putText(im, f"area4: {areaList[3]}",tuple(rightPoints[1]) ,cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100,0,0), 2, cv2.FILLED)
                                        cv2.putText(im, f"area5: {areaList[4]}",tuple(rightPoints[3]) ,cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100,0,0), 2, cv2.FILLED)
                                        areaString = f"a1:{areaList[0]}|a2:{areaList[1]}|a3:{areaList[2]}|a4:{areaList[3]}|a5:{areaList[4]}"
                                    except Exception as e:
                                        print(e)
                                    noduleCount = 0
                                    defectSize = []
                                    for count, nodule in enumerate(nodule_list):
                                        color = tuple(COLORS[count])
                                        xMM, yMM = returnLen(nodule,plate_list)
                                        if (yMM < 50 and xMM < 50) and (yMM > Defect_size or xMM > Defect_size):
                                            try:
                                                im = cv2.drawContours(im, nodule[10], -1, (0,0,255), 2)
                                                im = draw_rectangle(im, nodule[5],nodule[1], nodule[2], nodule[3], nodule[4],nodule[0],color,[xMM,yMM])
                                                defectSize.append(nodule[8])
                                                noduleCount += 1
                                            except Exception as e:
                                                print(f"return loop{e}")
                                

                    #Saving the plate with maximum nodules for given plate 
                    if noduleCount > prevNoduleCount and noduleCount >= number_of_defects:
                        prevNoduleCount = noduleCount
                        #Saving the image
                        if os.path.isdir(dirname) is not True:    
                            os.makedirs(dirname)
                        cv2.imwrite(imagepath, im)
                        cv2.imwrite(real_imagepath, imReal)
                        #print(areaString)
                        #Logging the defect
                        logDefectsDetailsInDBInThread(config_id, "CAM3", imagepath, "nodule", areaString, noduleCount, 1)
                        if status == "Auto":
                            #creating rejection trigger file
                            os.system(f"touch {trigger_file_path}")                        
                            #updating reject count
                            defectBool = True
                            f = open(textFilePath,"w+")
                            f.write("rejected")                    
                            f.close()
                else:
                    #conditon for counting plate
                    if plate_list[0][7] > 680:
                        prevNoduleCount = 0
                        plateAbsentCounter += 1
                        if plateAbsentCounter > 2:
                            if updateCountBool == False:
                                if os.path.exists(textFilePath) == True:
                                    #updating total count
                                    updateTotalCount()
                                    print("updating reject count ==================")
                                    updateRejectCount()
                                    os.system(f"rm {textFilePath}")
                                else:
                                    #updating total count
                                    updateTotalCount()
                                    print("updating pass count ==================")
                                    updatePassCount()
                                updateCountBool = True
                                defectBool = False
                            plateCounterBool = True

            resized = cv2.resize(im, (int(im.shape[1] * 30 / 100), int(im.shape[0] * 30 / 100)))
            # cv2.imshow("CAM3video", resized)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

            cv2.imwrite(imgPath,resized)
            try:
                # os.system("scp -i ~/.ssh/id_rsa /home/rfserver2/insightzz/code/NUCCTRL_TRANSFER/CAM3/TMP.jpg nuc-ctrl@169.254.0.28:/home/nuc-ctrl/insightzz/code/PROCESSED_IMAGES/CAM3/TMP.jpg")
                sftp.put(imgPath, remotePath)
            except Exception as e:
                dalogger.critical(f"transfer error : {e}")    # out.release()                

        # cv2.destroyAllWindows()
    except Exception as e:
        dalogger.critical(f"Exception in main : {e}")

if __name__ == '__main__':
    main()
