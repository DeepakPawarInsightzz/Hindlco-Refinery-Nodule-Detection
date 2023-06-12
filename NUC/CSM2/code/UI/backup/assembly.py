from tendo import singleton
me = singleton.SingleInstance()

import os
from shutil import ExecError
import sys
#import cv2
from numpy import number
import datetime
from datetime import timedelta
import time
import threading
import shutil
import subprocess

config_path = "/home/nuc-ctrl/insightzz/code/UI/config.xml"
# config_path = "/home/pratik/insightzz/project/Hindalco/CODE/REFINERY/REFINERY3/code/UI/config.xml"

import ast
import xml.etree.ElementTree as ET
config_parse = ET.parse(config_path)
config_root = config_parse.getroot()
UI_CODE_PATH = config_root[0].text
#DB credentials
import pymysql
db_user = config_root[1].text
db_pass = config_root[2].text
db_host = config_root[3].text
db_name = config_root[4].text

DOWNLOAD_PATH = config_root[5].text

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui ,QtWidgets, uic
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 

#For logging error
import logging
import traceback
#Logging module
uilogger = None
logging.basicConfig(filename=UI_CODE_PATH+"UI_RECORD_ACT_.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
uilogger=logging.getLogger("UI_RECORD_ACT_")
uilogger.setLevel(logging.CRITICAL) #CRITICAL #DEBUG

NO_IMAGE_PATH = UI_CODE_PATH+"no-image-found.png"

CAM1_IMAGE_LINK = "/home/nuc-ctrl/insightzz/code/PROCESSED_IMAGES/CAM1/TMP.jpg"
CAM2_IMAGE_LINK = "/home/nuc-ctrl/insightzz/code/PROCESSED_IMAGES/CAM2/TMP.jpg"
CAM3_IMAGE_LINK = "/home/nuc-ctrl/insightzz/code/PROCESSED_IMAGES/CAM3/TMP.jpg"

startHealthScriptNUC = "/home/nuc-ctrl/insightzz/code/SERVER_HEALTH/startHealthScript.sh"
killHealthScriptNUC = "/home/nuc-ctrl/insightzz/code/SERVER_HEALTH/killHealthScript.sh"
#startHealthScriptServer = "/home/nuc-ctrl/insightzz/code/SHELL_SCRIPT/start_health_script.sh"
#killHealthScriptServer = "/home/nuc-ctrl/insightzz/code/SHELL_SCRIPT/kill_health_script.sh"

#start_algo_sh = "/home/nuc-ctrl/insightzz/code/SHELL_SCRIPT/start_script.sh"
#kill_algo_sh = "/home/nuc-ctrl/insightzz/code/SHELL_SCRIPT/kill_script.sh"

arduino_service_start_sh = ""#"/home/nuc-ctrl/insightzz/code/ARDUINO/start_arduino.sh"
arduino_service_kill_sh = ""#"/home/nuc-ctrl/insightzz/code/ARDUINO/kill_arduino.sh"

class mainwindow(QtWidgets.QMainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(mainwindow, self).__init__(*args, **kwargs)      
        uic.loadUi(UI_CODE_PATH+"main.ui", self)  
        self.setWindowTitle("MainWindow")

        self.update_cam_health()
        self.timer_health=QTimer(self)
        self.timer_health.timeout.connect(self.update_cam_health)
        self.timer_health.start(5000)

        self.add_config_button.clicked.connect(self.add_config)
        self.view_config_button.clicked.connect(self.openconfigwindow)
        self.add_prev_config()

        self.update_count()
        self.timer_count=QTimer(self)
        self.timer_count.timeout.connect(self.update_count)
        self.timer_count.start(2000)

        subprocess.call(["sh", startHealthScriptNUC])
        #subprocess.call(["sh", startHealthScriptServer])

        # subprocess.call(["sh", arduino_service_start_sh])
        #self.start_algo_button.clicked.connect(self.start_process)
        self.Auto.clicked.connect(self.start_PLC_process)

        self.imageView_button1.clicked.connect(self.post_button_1)
        self.imageView_button2.clicked.connect(self.post_button_2)
        self.imageView_button3.clicked.connect(self.post_button_3)
        self.imageView_button4.clicked.connect(self.post_button_4)
        self.imageView_button5.clicked.connect(self.post_button_5)

        self.imageView_button1_2.clicked.connect(self.post_real_button_1)
        self.imageView_button2_2.clicked.connect(self.post_real_button_2)
        self.imageView_button3_2.clicked.connect(self.post_real_button_3)
        self.imageView_button4_2.clicked.connect(self.post_real_button_4)
        self.imageView_button5_2.clicked.connect(self.post_real_button_5)

        self.show_processed_data()
        self.timer_processed_data=QTimer(self)
        self.timer_processed_data.timeout.connect(self.show_processed_data)
        self.timer_processed_data.start(2000)

        self.update_image()
        self.timer_img=QTimer(self)
        self.timer_img.timeout.connect(self.update_image)
        self.timer_img.start(200)

        self.history_button.clicked.connect(self.show_datarecord_windwo)        
        self.reset_alarm_button.clicked.connect(stopPLC)
        self.reset_count_button.clicked.connect(self.reset_count)

        self.defect_size_label.hide()
        self.defect_size_lineEdit.hide()

    def show_datarecord_windwo(self):
        data_record_object.show()

    def reset_count(self):
        try:
            db_insert = pymysql.connect(host=db_host,    # your host, usually localhost
                         user=db_user,         # your username
                         passwd=db_pass,  # your password
                         db=db_name)
            cur = db_insert.cursor()
            query = f"insert into COUNT_TABLE (TOTAL, REJECTED, PASSED) values ({0},{0},{0})"
            cur.execute(query)
            db_insert.commit()
            cur.close()
            db_insert.close()
            self.show_message("Count reset done!")
        except Exception as e:
            print(e)

    def openconfigwindow(self):
        config_object.load_prev_config()
        config_object.show()

    def ClosePLC(self):
        try:
            db_insert = pymysql.connect(host=db_host,    # your host, usually localhost
                user=db_user,         # your username
                passwd=db_pass,  # your password
                db=db_name)
            cur = db_insert.cursor()
            self.PLC_Manual_start_Time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.PLC_status="Manual"
            query=f"INSERT INTO `Refinary3_CSM2`.`Auto` (`Status`, `Start_Time`) VALUES ('{self.PLC_status}', '{self.PLC_Manual_start_Time}');"
            cur.execute(query)
            db_insert.commit()
            cur.close()
            db_insert.close()
        except Exception as e:
            print(e)
    def closeEvent(self, event):
        quit_msg = "Are you sure you want to close the program?"
        reply = QtWidgets.QMessageBox.question(self, 'Message', 
                         quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
            self.ClosePLC()
            subprocess.call(["sh", killHealthScriptNUC])
            #subprocess.call(["sh", killHealthScriptServer])
            subprocess.call(["sh", arduino_service_kill_sh])
            #subprocess.call(["sh", kill_algo_sh])
        else:
            event.ignore()

    def show_message(self, message):
        choice = QMessageBox.information(self, 'Message!',message)

    #=================================== Count ======================================================#
    def update_count(self):
        try:
            db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                         user=db_user,         # your username
                         passwd=db_pass,  # your password
                         db=db_name)
            cur = db_select.cursor()
            query = f"select ID, TOTAL, REJECTED, PASSED from COUNT_TABLE order by ID desc limit 1"
            cur.execute(query)
            data_set = cur.fetchall()
            cur.close()
            db_select.close()
            self.totalcount_label.setText(str(data_set[0][1]))
            self.rejectedcount_label.setText(str(data_set[0][2]))
            self.passedcount_label.setText(str(data_set[0][3]))
        except Exception as e:
            print(e)
    
    def update_query(self,Status,time):
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
        
    def start_PLC_process(self):
        db_insert = pymysql.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
        cur = db_insert.cursor()
        query = "SELECT Status FROM `Refinary3_CSM2`.`Auto` ORDER BY ID DESC LIMIT 1"
        cur.execute(query)
        data_set = cur.fetchall()
        status = data_set[0][0]  # Retrieve the status from the first row of the result

        if status == "Auto":
            self.Auto.setChecked(False)  # Set the toggle button to Auto mode
        elif status == "Manual":
            self.Auto.setChecked(True)  # Set the toggle button to Manual mode

        if self.Auto.isChecked():
            buttonReply = QMessageBox.question(self, 'Message', "Do you want to start Auto processing?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.PLC_Start_Time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.PLC_status = "Auto"
                query = f"INSERT INTO `Refinary3_CSM2`.`Auto` (`Status`, `Start_Time`) VALUES ('{self.PLC_status}', '{self.PLC_Start_Time}');"
                cur.execute(query)
                db_insert.commit()
                cur.close()
                db_insert.close()
                self.update_query(Status="Manual", time=self.PLC_Start_Time)
                self.show_message("It will take around 10-15 seconds to start")
                self.Auto.setStyleSheet("background-color: rgb(255, 0, 0);")
                self.Auto.setText(QtCore.QCoreApplication.translate("MainWindow", "Manual"))
        else:
            buttonReply = QMessageBox.question(self, 'Message', "Do you want to stop Auto processing?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.PLC_Manual_start_Time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.update_query(Status="Auto", time=self.PLC_Manual_start_Time)
                self.PLC_status = "Manual"
                query = f"INSERT INTO `Refinary3_CSM2`.`Auto` (`Status`, `Start_Time`) VALUES ('{self.PLC_status}', '{self.PLC_Manual_start_Time}');"
                cur.execute(query)
                db_insert.commit()
                cur.close()
                db_insert.close()
                self.Auto.setStyleSheet("background-color: rgb(0, 170, 255)")
                self.Auto.setText(QtCore.QCoreApplication.translate("MainWindow", "Auto"))

    #=================================== configurations =============================================#
    def add_prev_config(self):
        try:        
            db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                         user=db_user,         # your username
                         passwd=db_pass,  # your password
                         db=db_name)
            cur = db_select.cursor()
            query = f"select * from CONFIGURATIONS order by ID desc limit 1"
            cur.execute(query)
            data_set = cur.fetchall()
            cur.close()
            db_select.close()
            batch_no = data_set[0][1]
            defect_size = data_set[0][3]
            number_of_defect = data_set[0][4]
            crop_number = data_set[0][5]
            self.batch_lineEdit.setText(str(batch_no))
            self.defect_size_lineEdit.setText(str(defect_size))
            self.number_defect_lineEdit.setText(str(number_of_defect))
            self.crop_number_comboBox.setCurrentText(str(crop_number))
        except Exception as e:
            print(e)

    def add_config(self):
        batch_number = self.batch_lineEdit.text()
        try:
            defect_size = float(self.defect_size_lineEdit.text())
        except:
            self.show_message("defect size must be a number")
        try:
            number_of_defects = int(self.number_defect_lineEdit.text())
        except:
            self.show_message("defect size must be a number")
        crop_number = int(self.crop_number_comboBox.currentText())

        #=============== getting previous section number to compare ======================#
        try:
            db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                         user=db_user,         # your username
                         passwd=db_pass,  # your password
                         db=db_name)
            cur = db_select.cursor()
            query = f"select BATCH_NUMBER from CONFIGURATIONS order by ID desc limit 1"
            cur.execute(query)
            data_set = cur.fetchall()
        except Exception as e:
            print(e)
        prev_sect = data_set[0][0]

        #================== resetting count if section number changed ======================#
        if batch_number != prev_sect:
            self.reset_count()

        #=========================== adding configuration ==================================#
        try:
            db_insert = pymysql.connect(host=db_host,    # your host, usually localhost
                         user=db_user,         # your username
                         passwd=db_pass,  # your password
                         db=db_name)
            cur = db_insert.cursor()
            query = f"insert into CONFIGURATIONS (BATCH_NUMBER, DEFECT_SIZE, NUMBER_OF_DEFECTS, CROP_NUMBER) values ('{batch_number}',{defect_size},{number_of_defects},{crop_number})"
            cur.execute(query)
            db_insert.commit()
            cur.close()
            db_insert.close()
            self.show_message("Configurations saved successfully")
        except Exception as e:
            print(e)

    #=================================== updating health =============================================#
    def update_cam_health(self):
        try:
            db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                         user=db_user,         # your username
                         passwd=db_pass,  # your password
                         db=db_name)
            cur = db_select.cursor()
            query = "SELECT ITEM,HEALTH FROM SYSTEM_HEALTH_TABLE"
            cur.execute(query)
            data_set = cur.fetchall()
            cur.close()
            for cam_pos in data_set:
                if cam_pos[0] == "CAM1" and cam_pos[1] == "OK":
                    self.cam1_health.setText("Cam 1 : ACTIVE")
                    self.cam1_health.setStyleSheet("background-color: rgb(0, 170, 0);")                
                elif cam_pos[0] == "CAM1" and cam_pos[1] == "NOTOK":
                    print("CAM1 is not connnected")
                    uilogger.critical("CAM1 is not connnected")
                    self.cam1_health.setText("Cam 1 : INACTIVE")
                    self.cam1_health.setStyleSheet("background-color: rgb(255, 1, 1);")

                if cam_pos[0] == "CAM2" and cam_pos[1] == "OK":
                    self.cam2_health.setText("Cam 2 : ACTIVE")
                    self.cam2_health.setStyleSheet("background-color: rgb(0, 170, 0);")                
                elif cam_pos[0] == "CAM2" and cam_pos[1] == "NOTOK":
                    print("CAM2 is not connnected")
                    uilogger.critical("CAM2 is not connnected")
                    self.cam2_health.setText("Cam 2 : INACTIVE")
                    self.cam2_health.setStyleSheet("background-color: rgb(255, 1, 1);")

                if cam_pos[0] == "CAM3" and cam_pos[1] == "OK":
                    self.cam3_health.setText("Cam 3 : ACTIVE")
                    self.cam3_health.setStyleSheet("background-color: rgb(0, 170, 0);")                
                elif cam_pos[0] == "CAM3" and cam_pos[1] == "NOTOK":
                    print("CAM3 is not connnected")
                    uilogger.critical("CAM3 is not connnected")
                    self.cam3_health.setText("Cam 3 : INACTIVE")
                    self.cam3_health.setStyleSheet("background-color: rgb(255, 1, 1);")

                if cam_pos[0] == "NUC1" and cam_pos[1] == "OK":
                    self.csm_health.setText("CSM2 System : ACTIVE")
                    self.csm_health.setStyleSheet("background-color: rgb(0, 170, 0);")                
                elif cam_pos[0] == "NUC1" and cam_pos[1] == "NOTOK":
                    print("CSM System is not connnected")
                    uilogger.critical("CSM2 System is not connnected")
                    self.csm_health.setText("CSM2 System : INACTIVE")
                    self.csm_health.setStyleSheet("background-color: rgb(255, 1, 1);")

                if cam_pos[0] == "PLC" and cam_pos[1] == "OK":
                    self.plc_health.setText("PLC : ACTIVE")
                    self.plc_health.setStyleSheet("background-color: rgb(0, 170, 0);")                
                elif cam_pos[0] == "PLC" and cam_pos[1] == "NOTOK":
                    print("PLC is not connnected")
                    uilogger.critical("PLC is not connnected")
                    self.plc_health.setText("PLC : INACTIVE")
                    self.plc_health.setStyleSheet("background-color: rgb(255, 1, 1);")
        except Exception as e:
            print('Exception : ',e)
            uilogger.critical(f"update cam health : "+ str(e))

        try:
            db_select = pymysql.connect(host='localhost',    # your host, usually localhost
                         user=db_user,         # your username
                         passwd=db_pass,  # your password
                         db='CSM_DB')
            cur = db_select.cursor()
            query = "SELECT ITEM,HEALTH FROM SYSTEM_HEALTH_TABLE"
            cur.execute(query)
            data_set = cur.fetchall()
            cur.close()
            for cam_pos in data_set:
                if cam_pos[0] == "SERVER" and cam_pos[1] == "OK":
                    self.server_health.setText("Server : ACTIVE")
                    self.server_health.setStyleSheet("background-color: rgb(0, 170, 0);")                
                elif cam_pos[0] == "SERVER" and cam_pos[1] == "NOTOK":
                    print("Server is not connnected")
                    uilogger.critical("Server is not connnected")
                    self.server_health.setText("Server : INACTIVE")
                    self.server_health.setStyleSheet("background-color: rgb(255, 1, 1);")
        except Exception as e:
            print('Exception : ',e)
            uilogger.critical(f"update cam health : "+ str(e))            
    
    #================================= updating defect data ====================================#
    #==============for showing image starts===========================#
    def show_image(self,image_link):
        print(image_link)
        os.system(f"scp -i ~/.ssh/id_rsa rfserver@169.254.0.31:{image_link} /home/nuc-ctrl/insightzz/code/UI/TEMP_IMG/TMP.jpg")
        image_link = "/home/nuc-ctrl/insightzz/code/UI/TEMP_IMG/TMP.jpg"
        if os.path.exists(image_link):
            imagewindow_object.setWindowTitle(image_link.split("/")[-1])
            imagewindow_object.loadImage(image_link)
        else:
            image_link = NO_IMAGE_PATH
            imagewindow_object.setWindowTitle(image_link.split("/")[-1])
            imagewindow_object.loadImage(image_link)
    
    #========================= Detected Image Links =============================================#
    def post_button_1(self):
        #=======change to default color===========#
        self.imageView_button1.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button1.setStyleSheet("background-color : blue")
        image_link = self.imageList[0]
        self.show_image(image_link)
        
    def post_button_2(self):
        #=======change to default color===========#
        self.imageView_button1.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button2.setStyleSheet("background-color : blue")
        image_link = self.imageList[1]
        self.show_image(image_link)
        
    def post_button_3(self):
        #=======change to default color===========#
        self.imageView_button1.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button3.setStyleSheet("background-color : blue")
        image_link = self.imageList[2]
        self.show_image(image_link)
        
    def post_button_4(self):
        #=======change to default color===========#
        self.imageView_button1.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button4.setStyleSheet("background-color : blue")
        image_link = self.imageList[3]
        self.show_image(image_link)
        
    def post_button_5(self):
        #=======change to default color===========#
        self.imageView_button1.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button5.setStyleSheet("background-color : blue")
        image_link = self.imageList[4]
        self.show_image(image_link)


    #========================= Real Image Links =============================================#
    def post_real_button_1(self):
        #=======change to default color===========#
        self.imageView_button1_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5_2.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button1_2.setStyleSheet("background-color : blue")
        image_link = self.real_imageList[0]
        self.show_image(image_link)
        
    def post_real_button_2(self):
        #=======change to default color===========#
        self.imageView_button1_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5_2.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button2_2.setStyleSheet("background-color : blue")
        image_link = self.real_imageList[1]
        self.show_image(image_link)
        
    def post_real_button_3(self):
        #=======change to default color===========#
        self.imageView_button1_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5_2.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button3_2.setStyleSheet("background-color : blue")
        image_link = self.real_imageList[2]
        self.show_image(image_link)
        
    def post_real_button_4(self):
        #=======change to default color===========#
        self.imageView_button1_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5_2.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button4_2.setStyleSheet("background-color : blue")
        image_link = self.real_imageList[3]
        self.show_image(image_link)
        
    def post_real_button_5(self):
        #=======change to default color===========#
        self.imageView_button1_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button2_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button3_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button4_2.setStyleSheet("background-color: rgb(223, 223, 223);")
        self.imageView_button5_2.setStyleSheet("background-color: rgb(223, 223, 223);")

        #========change the selected button color=======#
        self.imageView_button5_2.setStyleSheet("background-color : blue")
        image_link = self.real_imageList[4]
        self.show_image(image_link)

    def show_processed_data(self):
        try:
            db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                    user=db_user,         # your username
                    passwd=db_pass,  # your password
                    db=db_name)
            cur = db_select.cursor()
            query = "SELECT ID, CAMERA, NO_OF_DEFECTS,DEFECT_SIZE,DATE_TIME,IMAGE_LINK FROM PROCESSING_TABLE order by ID desc limit 5"
            cur.execute(query)
            data_set = cur.fetchall()
            cur.close()
            db_select.close()

            self.imageView_button1.hide()
            self.imageView_button2.hide()
            self.imageView_button3.hide()
            self.imageView_button4.hide()
            self.imageView_button5.hide()

            self.tableWidget.setRowCount(len(data_set))
            self.imageList = []
            self.real_imageList = []
            counter = 1

            for row in range(0,len(data_set)):
                if data_set[row][1] == "CAM1":
                    side = "FRONT"
                else:
                    side = "BACK"

                self.tableWidget.setItem(row, 0,QTableWidgetItem(side))
                self.tableWidget.setItem(row, 1,QTableWidgetItem(str(data_set[row][2])))
                self.tableWidget.setItem(row, 2,QTableWidgetItem(str(data_set[row][4])))
                self.imageList.append(data_set[row][5])
                real_image_link = f"{data_set[row][5][:-4]}_real.jpg"
                self.real_imageList.append(real_image_link)

                if counter == 1:
                    self.imageView_button1.show()
                elif counter == 2:
                    self.imageView_button2.show()
                elif counter == 3:
                    self.imageView_button3.show()
                elif counter == 4:
                    self.imageView_button4.show()
                elif counter == 5:
                    self.imageView_button5.show()
                counter = counter +1

        except Exception as e:
            print('Exception : ',e)
            uilogger.critical(f"update cam health : "+ str(e))

    def update_cam1_image(self):
        if os.path.exists(CAM1_IMAGE_LINK):
            self.cam1_defect_image.setPixmap(QtGui.QPixmap(CAM1_IMAGE_LINK))
        else:
            self.cam1_defect_image.setPixmap(QtGui.QPixmap(NO_IMAGE_PATH))
    def update_cam2_image(self):
        if os.path.exists(CAM2_IMAGE_LINK):
            self.cam2_defect_image.setPixmap(QtGui.QPixmap(CAM2_IMAGE_LINK))
        else:
            self.cam2_defect_image.setPixmap(QtGui.QPixmap(NO_IMAGE_PATH))
    def update_cam3_image(self):
        if os.path.exists(CAM3_IMAGE_LINK):
            self.cam3_defect_image.setPixmap(QtGui.QPixmap(CAM3_IMAGE_LINK))
        else:
            self.cam3_defect_image.setPixmap(QtGui.QPixmap(NO_IMAGE_PATH))

    def update_image(self):
        self.update_cam1_image()
        self.update_cam2_image()
        self.update_cam3_image()

class ConfigWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(ConfigWindow, self).__init__(*args, **kwargs)
        uic.loadUi(UI_CODE_PATH+"config.ui", self)
        self.setWindowTitle("Config Window")
    def load_prev_config(self):
        try:
            db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                            user=db_user,         # your username
                            passwd=db_pass,  # your password
                            db=db_name)
            cur = db_select.cursor()
            query = f"select BATCH_NUMBER, DATE_TIME, DEFECT_SIZE, NUMBER_OF_DEFECTS, CROP_NUMBER from CONFIGURATIONS order by ID desc"
            cur.execute(query)
            data_set = cur.fetchall()
            cur.close()
            db_select.close()
            #================= creating table ==================#
            config_object.tableWidget.setRowCount(len(data_set))
            for row in range(0,len(data_set)):
                batch_number = str(data_set[row][0])
                date_time = str(data_set[row][1])
                defect_size = str(data_set[row][2])
                number_of_defect = str(data_set[row][3])
                crop_number = str(data_set[row][4])
                config_object.tableWidget.setItem(row, 0, QTableWidgetItem(batch_number))
                config_object.tableWidget.setItem(row, 1, QTableWidgetItem(crop_number))
                config_object.tableWidget.setItem(row, 2, QTableWidgetItem(defect_size))
                config_object.tableWidget.setItem(row, 3, QTableWidgetItem(number_of_defect))
                config_object.tableWidget.setItem(row, 4, QTableWidgetItem(date_time))

                header = config_object.tableWidget.horizontalHeader()
                header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
                header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        except Exception as e:
            print(e)

class PhotoViewer(QtWidgets.QGraphicsView):
    photoClicked = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def hasPhoto(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.hasPhoto():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.fitInView()

    def wheelEvent(self, event):
        if self.hasPhoto():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if self._photo.isUnderMouse():
            self.photoClicked.emit(self.mapToScene(event.pos()).toPoint())
        super(PhotoViewer, self).mousePressEvent(event)


class ImageWindow(QtWidgets.QWidget):
    def __init__(self):
        super(ImageWindow, self).__init__()
        self.viewer = PhotoViewer(self)
        # 'Load image' button
        
        self.viewer.photoClicked.connect(self.photoClicked)
        # Arrange layout
        VBlayout = QtWidgets.QVBoxLayout(self)
        VBlayout.addWidget(self.viewer)
        HBlayout = QtWidgets.QHBoxLayout()
        HBlayout.setAlignment(QtCore.Qt.AlignLeft)
        VBlayout.addLayout(HBlayout)
        self.imagepath = ""        

    def show_message(self, message):
        choice = QMessageBox.information(self, 'Message!',message)

    def loadImage(self, imagelink):
        self.close()        
        self.setGeometry(100, 100, 800, 600)
        self.show()
        self.imagepath = imagelink        
        self.viewer.setPhoto(QtGui.QPixmap(imagelink))

    def pixInfo(self):
        self.viewer.toggleDragMode()

    def photoClicked(self, pos):
        if self.viewer.dragMode()  == QtWidgets.QGraphicsView.NoDrag:
            self.editPixInfo.setText('%d, %d' % (pos.x(), pos.y()))

class DataRecord_Window(QtWidgets.QMainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(DataRecord_Window, self).__init__(*args, **kwargs)
        uic.loadUi(UI_CODE_PATH+"history.ui", self)

        self.setWindowTitle("Data Record Window")
        self.from_date.setCalendarPopup(True)
        self.to_date.setCalendarPopup(True)
        current_date = datetime.date.today()
        d = QDate(current_date.year, current_date.month, current_date.day) 
        dd = QDate(current_date.year, current_date.month, current_date.day) 
        self.from_date.setDate(dd)
        self.to_date.setDate(d)

        self.enter_button.clicked.connect(self.show_data)
        self.download_button.clicked.connect(self.download_data)

    def fetch_data(self):
        summaryStr = "Please wait. The data is getting Fetched"
        self.summary_data_lable.setText(summaryStr)
        batch_number = self.batch_no_lineEdit.text()
        from_temp_var = self.from_date.date()
        to_temp_var = self.to_date.date()

        if to_temp_var.toPyDate() < from_temp_var.toPyDate():
            self.show_message("To date should be greater than from date")
            return
        startDate = str(from_temp_var.toPyDate())+" 00:00:00"
        endDate = str(to_temp_var.toPyDate())+" 23:59:00"        

        if batch_number != "":
            try:
                db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                user=db_user,         # your username
                                passwd=db_pass,  # your password
                                db=db_name)
                cur = db_select.cursor()
                query = f"select proctab.CAMERA, proctab.CONFIG_ID ,configtab.ID, configtab.BATCH_NUMBER, proctab.NO_OF_DEFECTS,\
                        proctab.DEFECT_SIZE, proctab.DATE_TIME, proctab.IMAGE_LINK \
                        from PROCESSING_TABLE proctab, CONFIGURATIONS configtab \
                        where proctab.CONFIG_ID = configtab.ID and \
                        date(proctab.DATE_TIME) >= date('{startDate}') and date(proctab.DATE_TIME) <= date('{endDate}') and \
                        configtab.BATCH_NUMBER={batch_number}"

                cur.execute(query)
                data_set = cur.fetchall()
                cur.close()
                db_select.close()
            except Exception as e:
                print(e)
                uilogger.critical(f"data record : "+ str(e))
        else:
            try:
                db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                user=db_user,         # your username
                                passwd=db_pass,  # your password
                                db=db_name)
                cur = db_select.cursor()
                query = f"select proctab.CAMERA, proctab.CONFIG_ID ,configtab.ID, configtab.BATCH_NUMBER, proctab.NO_OF_DEFECTS,\
                        proctab.DEFECT_SIZE, proctab.DATE_TIME, proctab.IMAGE_LINK \
                        from PROCESSING_TABLE proctab, CONFIGURATIONS configtab \
                        where proctab.CONFIG_ID = configtab.ID and \
                        date(proctab.DATE_TIME) >= date('{startDate}') and date(proctab.DATE_TIME) <= date('{endDate}')"

                cur.execute(query)
                data_set = cur.fetchall()
                cur.close()
                db_select.close()
            except Exception as e:
                print(e)
                uilogger.critical(f"data record : "+ str(e))
        return data_set

    def show_data(self):
        data_set = self.fetch_data()
        defects_number = len(data_set)
        self.summary_data_lable.setText(f"Total defect : {defects_number}")
        self.tableWidget.setRowCount(defects_number)
        for row, datadict in enumerate(data_set):
            camera = datadict[0]
            batch_number = datadict[3]
            number_of_defects = str(datadict[4])
            defect_size = datadict[5]
            date_time = str(datadict[6])
            imagelink = datadict[7]
            self.tableWidget.setItem(row,0, QTableWidgetItem(camera))
            self.tableWidget.setItem(row,1, QTableWidgetItem(batch_number))
            self.tableWidget.setItem(row,2, QTableWidgetItem(number_of_defects))
            self.tableWidget.setItem(row,3, QTableWidgetItem(defect_size))
            self.tableWidget.setItem(row,4, QTableWidgetItem(date_time))
            header = self.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

            qSelectButton = QPushButton("Select")
            qSelectButton.clicked.connect(lambda checked, arg1=imagelink
                                            : self.show_image(arg1))
            self.tableWidget.setCellWidget(row,5, qSelectButton)                

    def show_image(self,image_link):
        os.system(f"scp -i ~/.ssh/id_rsa rfserver@169.254.0.31:{image_link} /home/nuc-ctrl/insightzz/code/UI/TEMP_IMG/TMP.jpg")
        image_link = "/home/nuc-ctrl/insightzz/code/UI/TEMP_IMG/TMP.jpg"
        if os.path.exists(image_link):
            imagewindow_object.setWindowTitle(image_link.split("/")[-1])
            imagewindow_object.loadImage(image_link)
        else:
            image_link = NO_IMAGE_PATH
            imagewindow_object.setWindowTitle(image_link.split("/")[-1])
            imagewindow_object.loadImage(image_link)

    def download_data(self):
        self.show_data()
        data_set = self.fetch_data()

        defects_number = len(data_set)
        self.summary_data_lable.setText(f"Total defect : {defects_number}")

        foldername = DOWNLOAD_PATH+datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        f = open(foldername+'.xlsx','w')
        dataStr = "SR NO"+','+"CAMERA"+','+"BATCH NUMBER"+','+"NUMBER OF DEFECTS"+','+"DEFECT SIZE"+','+"DATE TIME"+','+"IMAGELINK"
        f.write(dataStr + '\n')

        for row, datadict in enumerate(data_set):
            camera = datadict[0]
            batch_number = datadict[3]
            number_of_defects = str(datadict[4])
            defect_size = datadict[5].replace(",","|")
            date_time = str(datadict[6])
            imagelink = datadict[7]
            imagename = imagelink.split("/")[-1]
            dataStr = f"{row},{camera},{batch_number},{number_of_defects},{defect_size},{date_time},{imagename}"        
            f.write(dataStr + '\n')

            if os.path.isdir(foldername) is not True:    
                os.makedirs(foldername)
            print(f"scp -i ~/.ssh/id_rsa rfserver@169.254.0.31:{imagelink} {foldername}/")
            os.system(f"scp -i ~/.ssh/id_rsa rfserver@169.254.0.31:{imagelink} {foldername}/")
            # shutil.copy(imagelink, f"{foldername}/{imagename}")

#========================== module for camera health alarm starts =======================#
import serial
def generateAlert():
    print("Inside Generate Alert")
    uilogger.debug("Inside generateAlert")        
    sendSignalToPLC()

def sendSignalToPLC():
    global plcLastStoppedDateTime
    five_min = timedelta(seconds=10)
    if((datetime.now() - plcLastStoppedDateTime) > five_min):
        print("sendSignalToPLC()")
        plcLastStoppedDateTime = datetime.now()
        startPLC()
        threading.Timer(3.0, stopPLC).start()
        print("Machine Stop Signal Send at : ", datetime.now())
    else:
        # print("Top Time condition Not Satisfied", datetime.datetime.now())
        pass

def initSerial():
    print("Inside initSerial")
    global serialObject
    try:
        serialObject = serial.Serial('/dev/ttyACM0',9600,timeout = 1)
        time.sleep(3)
    except:
        try:
            serialObject = serial.Serial('/dev/ttyACM1',9600,timeout = 1)
            time.sleep(3)
        except:
            try:
                serialObject = serial.Serial('/dev/ttyACM2',9600,timeout = 1)
                time.sleep(3)
            except:
                pass
    
def startPLC():
    print("Inside startPLC")
    global serialObject, configObject
    try:
        print("alert generated")
        serialObject.write(b'0')
        serialObject.write(b'1')
        serialObject.write(b'0')
        serialObject.write(b'1')
    except Exception as e:
        print("startPLC Exception is : ", e)
        uilogger.debug("startPLC Exception is : "+str(e))            

def stopPLC():
    print("Inside stopPLC")
    global serialObject
    try:
        print("alert stopped")
        serialObject.write(b'0')
        serialObject.write(b'0')
    except Exception as e:
        print("stopPLC Exception is : ", e)
        uilogger.debug("stopPLC Exception is : "+str(e))            

if __name__ == '__main__':
    initSerial()    
    app = QtWidgets.QApplication(sys.argv)
    main_object = mainwindow()
    config_object = ConfigWindow()
    imagewindow_object= ImageWindow()
    data_record_object = DataRecord_Window()
    main_object.show()
    app.exec()