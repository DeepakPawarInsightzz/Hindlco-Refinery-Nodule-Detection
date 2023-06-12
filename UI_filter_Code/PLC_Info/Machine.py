from tendo import singleton
me = singleton.SingleInstance()

import os
from shutil import ExecError
import sys
import cv2
from numpy import number
import datetime
from datetime import timedelta
import time
import threading
import shutil
import subprocess
from datetime import date

import logging
import traceback
#Logging module
uilogger = None
config_path = "/home/rfserver/insightzz/CSM2/PLC_Info/config.xml"

import ast
import xml.etree.ElementTree as ET
config_parse = ET.parse(config_path)
config_root = config_parse.getroot()
UI_CODE_PATH = config_root[0].text
#DB credentials

UI_CODE_PATH = config_root[0].text
logging.basicConfig(filename=UI_CODE_PATH+"UI_RECORD_ACT_.log",filemode='a',format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
uilogger=logging.getLogger("UI_RECORD_ACT_")
uilogger.setLevel(logging.CRITICAL) #CRITICAL #DEBUG


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

DOWNLOAD_PATH ="/home/rfserver/Desktop/Download_Data/CSM1"
DOWNLOAD_PATH2 ="/home/rfserver/Desktop/Download_Data/CSM2"

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui ,QtWidgets, uic
from PyQt5.QtGui import * 
from PyQt5.QtCore import * 


class DataRecord_Window(QtWidgets.QMainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(DataRecord_Window, self).__init__(*args, **kwargs)
        uic.loadUi(UI_CODE_PATH+"Machine.ui", self)

        self.setWindowTitle("Data Record Window")
        self.from_date.setCalendarPopup(True)
        self.to_date.setCalendarPopup(True)
        current_date = datetime.date.today()
        d = QDate(current_date.year, current_date.month, current_date.day) 
        dd = QDate(current_date.year, current_date.month, current_date.day) 
        self.from_date.setDate(dd)
        self.to_date.setDate(d)
        
        self.fetch.clicked.connect(self.show_data)
        self.download_button.hide()
        self.download_button.clicked.connect(self.download_data)
        self.fetch_2.clicked.connect(self.show_ALL_data)

        self.add_config_button.clicked.connect(self.Add_config)
        self.add_config_button_2.clicked.connect(self.config_show_data)
        self.fetch_3.clicked.connect(self.config_show_All_data)

    
    def show_message(self, message):
        choice = QMessageBox.information(self, 'Message!',message)

    def fetch_data(self):
        
        summaryStr = "Please wait. The data is getting Fetched"
        self.summary_data_lable.setText(summaryStr)
        Machine_Name = self.batch_no_lineEdit.text().upper()
        from_temp_var = self.from_date.date()
        print(from_temp_var)
        to_temp_var = self.to_date.date()
        print(to_temp_var)

        if to_temp_var.toPyDate() < from_temp_var.toPyDate():
            self.show_message("To date should be greater than from date")
            return
        startDate = str(from_temp_var.toPyDate())+" 00:00:00"
        endDate = str(to_temp_var.toPyDate())+" 23:59:00"
        if Machine_Name == "CSM1":
            PLC_Status = self.batch_no_lineEdit_2.text().capitalize()
            if PLC_Status != "":
                try:
                    db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                    user=db_user,         # your username
                                    passwd=db_pass,  #your password
                                    db="Refinary3_CSM1")
                    cur = db_select.cursor()
                    #query = f"SELECT `Auto`.`ID`,`Auto`.`Status`,`Auto`.`Start_Time` FROM `Refinary3_CSM1`.`Auto` where  Status = '{PLC_Status}' or Start_Time >= '{startDate}' or Start_Time <= '{endDate}' ;"
                    query = f"SELECT `Auto`.`ID`,`Auto`.`Status`,`Auto`.`Start_Time`,`Auto`.`End_Time` FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' and Start_Time <='{endDate}' and Status = '{PLC_Status}'  order by ID  desc limit 10;" 
                    cur.execute(query)
                    data_set = cur.fetchall()
                    cur.close()
                    db_select.close()
                    return data_set
                except Exception as e:
                    print(e)
                    uilogger.critical(f"data record : "+ str(e))
            else:
                if startDate !="" and endDate != "":
                    try:
                        db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                        user=db_user,         # your username
                                        passwd=db_pass,  # your password
                                        db="Refinary3_CSM1")
                        cur = db_select.cursor()
                        #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                        query=f"SELECT `Auto`.`ID`,`Auto`.`Status`,`Auto`.`Start_Time`,`Auto`.`End_Time` FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' and Start_Time <='{endDate}'  order by Start_Time  desc limit 10;"               
                        cur.execute(query)                                                                                                    
                        data_set = cur.fetchall()
                        cur.close()
                        db_select.close()
                        return data_set
                    except Exception as e:
                        print(e)
                        uilogger.critical(f"data record : "+ str(e))
            return data_set
            
        elif Machine_Name == "CSM2":
            PLC_Status = self.batch_no_lineEdit_2.text().capitalize()
            if PLC_Status != "":
                try:
                    db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                    user=db_user,         # your username
                                    passwd=db_pass,  # your password
                                    db="Refinary3_CSM2")
                    cur = db_select.cursor()
                    query = f"SELECT `Auto`.`ID`,`Auto`.`Status`,`Auto`.`Start_Time`,`Auto`.`End_Time` FROM `Refinary3_CSM2`.`Auto` where Start_Time >= '{startDate}' and Start_Time <='{endDate}' and Status = '{PLC_Status}' order by Start_Time  desc limit 10; "
                    cur.execute(query)
                    data_set = cur.fetchall()
                    cur.close()
                    db_select.close()
                    return data_set
                except Exception as e:
                    print(e)
                    uilogger.critical(f"data record : "+ str(e))
            else:
                if startDate !="" and endDate != "":
                    try:
                        db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                        user=db_user,         # your username
                                        passwd=db_pass,  # your password
                                        db="Refinary3_CSM2")
                        cur = db_select.cursor()
                        #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                        query=f"SELECT `Auto`.`ID`,`Auto`.`Status`,`Auto`.`Start_Time`,`Auto`.`End_Time` FROM `Refinary3_CSM2`.`Auto` where Start_Time >= '{startDate}' and Start_Time <='{endDate}' order by Start_Time  desc limit 10;  "               
                        cur.execute(query)
                        data_set = cur.fetchall()
                        cur.close()
                        db_select.close()
                        
                    except Exception as e:
                        print(e)
                        uilogger.critical(f"data record : "+ str(e))
            return data_set
        elif Machine_Name == "":
            self.summary_data_lable.setText(f"Please select the Machine name ")
   
    def fetch_ALL_data(self):
        summaryStr = "Please wait. The data is getting Fetched"
        self.summary_data_lable.setText(summaryStr)
        Machine_Name = self.batch_no_lineEdit.text().upper()
        from_temp_var = self.from_date.date()
        print(from_temp_var)
        to_temp_var = self.to_date.date()
        print(to_temp_var)

        if to_temp_var.toPyDate() < from_temp_var.toPyDate():
            self.show_message("To date should be greater than from date")
            return
        startDate = str(from_temp_var.toPyDate())+" 00:00:00"
        endDate = str(to_temp_var.toPyDate())+" 23:59:00"
        if Machine_Name == "CSM1":
            try:
                db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                user=db_user,         # your username
                                passwd=db_pass,  # your password
                                db="Refinary3_CSM1")
                cur = db_select.cursor()
                #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                query=f"SELECT `Auto`.`ID`,`Auto`.`Status`,`Auto`.`Start_Time`,`Auto`.`End_Time` FROM `Refinary3_CSM1`.`Auto`  order by Start_Time  desc limit 10;"               
                cur.execute(query)
                data_set = cur.fetchall()
                cur.close()
                db_select.close()
            except Exception as e:
                print(e)
                uilogger.critical(f"data record : "+ str(e))
            return data_set
            
        elif Machine_Name == "CSM2":
            
            try:
                    db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                    user=db_user,         # your username
                                    passwd=db_pass,  # your password
                                    db="Refinary3_CSM2")
                    cur = db_select.cursor()
                    #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                    query=f"SELECT `Auto`.`ID`,`Auto`.`Status`,`Auto`.`Start_Time`,`Auto`.`End_Time` FROM `Refinary3_CSM2`.`Auto` order by Start_Time  desc limit 10;"               
                    cur.execute(query)
                    data_set = cur.fetchall()
                    cur.close()
                    db_select.close()
            except Exception as e:
                    print(e)
                    uilogger.critical(f"data record : "+ str(e))
            return data_set
        elif Machine_Name == "":
            self.summary_data_lable.setText(f"Please select the Machine name ")

    def show_data(self):
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        data_set = self.fetch_data()
        print(data_set)
        Total = len(data_set)
        self.summary_data_lable.setText(f"NO OF Data : {Total}")
        #self.tableWidget.setRowCount(Total)
        self.tableWidget.setRowCount(len(data_set))
        for row, datadict in enumerate(data_set):
            Status = str(data_set[row][1])
            Start_Time = str(data_set[row][2])
            End_time = str(data_set[row][3])
            self.tableWidget.setItem(row,0, QTableWidgetItem(Status))
            self.tableWidget.setItem(row,1, QTableWidgetItem(Start_Time))
            self.tableWidget.setItem(row,2, QTableWidgetItem(End_time))
            #self.tableWidget.setItem(row,4, QTableWidgetItem(time_duration))
            header = self.tableWidget.horizontalHeader()    
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            # if row < len(data_set)-1:
            #     end_time =  data_set[row+1][2] 
            #     print(data_set[row+1][2])
            #     End_time =end_time
            #self.tableWidget.setItem(row,2, QTableWidgetItem(End_time))
        # Configure the vertical scroll bar
        self.tableWidget.verticalScrollBar().setGeometry(QtCore.QRect(0, 0, 0, 0))

            # Add the scrollbar to the table widget        
            #Status_ID = Status_ID +1

    def show_ALL_data(self):
        self.tableWidget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        data_set = self.fetch_ALL_data()
        print(data_set)
        Total = len(data_set)
        self.summary_data_lable.setText(f"NO OF Data : {Total}")
        #self.tableWidget.setRowCount(Total)
        self.tableWidget.setRowCount(len(data_set))
        for row, datadict in enumerate(data_set):
            Status = str(data_set[row][1])
            Start_Time = str(data_set[row][2])
            End_time = str(data_set[row][3])
            self.tableWidget.setItem(row,0, QTableWidgetItem(Status))
            self.tableWidget.setItem(row,1, QTableWidgetItem(Start_Time))
            self.tableWidget.setItem(row,2, QTableWidgetItem(End_time))
            #self.tableWidget.setItem(row,4, QTableWidgetItem(time_duration))
            header = self.tableWidget.horizontalHeader()    
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
            # if row < len(data_set)-1:
            #     end_time =  data_set[row+1][2] 
            #     print(data_set[row+1][2])
            #     End_time =end_time
            #self.tableWidget.setItem(row,2, QTableWidgetItem(End_time))
        # Configure the vertical scroll bar
        self.tableWidget.verticalScrollBar().setGeometry(QtCore.QRect(0, 0, 0, 0))

    def download_data(self):
        self.show_data()
        Machine_Name = self.batch_no_lineEdit.text().upper()
        data_set = self.fetch_data()
        defects_number = len(data_set)
        self.summary_data_lable.setText(f"Total Data : {defects_number}")
        Time_File_Name = str(date.today())
        if Machine_Name == "CSM1":
            if os.path.isdir(DOWNLOAD_PATH) is not True:
                os.makedirs(DOWNLOAD_PATH)
            save_path = DOWNLOAD_PATH
            if os.path.isdir(save_path) is not True:   
                os.makedirs(save_path) 
            file_name = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')+".xlsx"
            completeName = os.path.join(save_path, file_name)
            f = open(completeName,'w')
            dataStr = "Status"+','+"Start_Time"+','+"End_Time"
            f.write(dataStr + '\n')

            for row, datadict in enumerate(data_set):
                #ID = datadict[0]
                Status = datadict[1]
                Start_Time = str(datadict[2])
                if row < len(data_set)-1:
                    end_time =  data_set[row+1][2]
                else:
                    end_time = "None"
                    
                    
                #End_Time = datadict[3]
                dataStr = f"{Status},{Start_Time},{end_time}"        
                f.write(dataStr + '\n')

                if os.path.isdir(save_path) is not True:    
                    os.makedirs(save_path)
        elif Machine_Name == "CSM2":
            if os.path.isdir(DOWNLOAD_PATH2) is not True:
                os.makedirs(DOWNLOAD_PATH2)
            save_path = DOWNLOAD_PATH2
            if os.path.isdir(save_path) is not True:   
                os.makedirs(save_path) 
            file_name = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')+".xlsx"
            completeName = os.path.join(save_path, file_name)
            f = open(completeName,'w')
            dataStr = "Status"+','+"Start_Time"+','+"End_Time"
            f.write(dataStr + '\n')

            for row, datadict in enumerate(data_set):
                print(data_set)
                #ID = datadict[0]
                Status = datadict[1]
                Start_Time = str(datadict[2])
                if row < len(data_set)-1:
                    end_time =  data_set[row+1][2]
                else:
                    end_time = "None"
                    
                    
                #End_Time = datadict[3]
                dataStr = f"{Status},{Start_Time},{end_time}"        
                f.write(dataStr + '\n')

                if os.path.isdir(save_path) is not True:    
                    os.makedirs(save_path)

 #------------------------------  Defect_size config-------------------------------
    def Add_config(self):
        Machine_Name = self.batch_no_lineEdit.text().upper()
        temp_var = self.from_date.date()
        Date = str(temp_var.toPyDate())+" 00:00:00"
        try:
            number_of_defects = float(self.batch_no_lineEdit_3.text())
        except:
            self.show_message("defect size must be a number")
        if Machine_Name == "CSM1":
            try:
                db_insert = pymysql.connect(host=db_host,    # your host, usually localhost
                            user=db_user,         # your username
                            passwd=db_pass,  # your password
                            db=db_name)
                cur = db_insert.cursor()
                query = f"insert into CONFIGURATIONS_Test (DEFECT_SIZE) values ('{number_of_defects}')"
                cur.execute(query)
                db_insert.commit()
                cur.close()
                db_insert.close()
                self.show_message("Configurations saved successfully")
            except Exception as e:
                print(e)
                uilogger.critical(f"Add_config CSM1: "+ str(e))
        elif Machine_Name == "CSM2":
            try:
                db_insert = pymysql.connect(host=db_host,    # your host, usually localhost
                            user=db_user,         # your username
                            passwd=db_pass,  # your password
                            db="Refinary3_CSM2")
                cur = db_insert.cursor()
                query = f"insert into CONFIGURATIONS_Test (DEFECT_SIZE) values ('{number_of_defects}')"
                cur.execute(query)
                db_insert.commit()
                cur.close()
                db_insert.close()
                self.show_message("Configurations saved successfully")
            except Exception as e:
                print(e)
                uilogger.critical(f"Add_config CSM2: "+ str(e))
        elif Machine_Name == "":
            self.summary_data_lable.setText(f"Please select the Machine name ")

       


    def fetch_config(self):
        summaryStr = "Please wait. The data is getting Fetched"
        self.summary_data_lable.setText(summaryStr)
        Machine_Name = self.batch_no_lineEdit.text().upper()
        from_temp_var = self.from_date.date()
        print(from_temp_var)
        to_temp_var = self.to_date.date()
        print(to_temp_var)

        if to_temp_var.toPyDate() < from_temp_var.toPyDate():
            self.show_message("To date should be greater than from date")
            return
        startDate = str(from_temp_var.toPyDate())+" 00:00:00"
        endDate = str(to_temp_var.toPyDate())+" 23:59:00"
        if Machine_Name == "CSM1":
            if startDate !="" and endDate != "":
                try:
                    db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                    user=db_user,         # your username
                                    passwd=db_pass,  # your password
                                    db="Refinary3_CSM1")
                    cur = db_select.cursor()
                    #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                    query=f"select ID, DEFECT_SIZE,DATE_TIME from Refinary3_CSM1.CONFIGURATIONS_Test where DATE_TIME >= '{startDate}' and DATE_TIME <='{endDate}'  order by DATE_TIME desc limit 10 ;"               
                    cur.execute(query)   
                    data_set = cur.fetchall()
                    print(data_set)
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
                                    db="Refinary3_CSM1")
                    cur = db_select.cursor()
                    #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                    query=f"select ID, DEFECT_SIZE,DATE_TIME from Refinary3_CSM1.CONFIGURATIONS_Test order by DATE_TIME desc limit 10;"               
                    cur.execute(query)
                    data_set = cur.fetchall()
                    cur.close()
                    db_select.close()
                    print(data_set)
                except Exception as e:
                    print(e)
                    uilogger.critical(f"data record : "+ str(e))
            return data_set
            
        elif Machine_Name == "CSM2":
            if startDate !="" and endDate != "":
                try:
                    db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                    user=db_user,         # your username
                                    passwd=db_pass,  # your password
                                    db="Refinary3_CSM2")
                    cur = db_select.cursor()
                    #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                    query=f"select ID, DEFECT_SIZE,DATE_TIME from Refinary3_CSM2.CONFIGURATIONS_Test where DATE_TIME >= '{startDate}' and DATE_TIME <='{endDate}'  order by DATE_TIME desc limit 10;"                
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
                                    db="Refinary3_CSM1")
                    cur = db_select.cursor()
                    #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                    query=f"select ID, DEFECT_SIZE,DATE_TIME from Refinary3_CSM2.CONFIGURATIONS_Test order by DATE_TIME desc limit 10;"               
                    cur.execute(query)
                    data_set = cur.fetchall()
                    cur.close()
                    db_select.close()
                except Exception as e:
                    print(e)
                    uilogger.critical(f"data record : "+ str(e))
            return data_set
        elif Machine_Name == "":
            self.summary_data_lable.setText(f"Please select the Machine name ")

    def config_show_data(self):
        data_set = self.fetch_config()
        Total = len(data_set)
        self.summary_data_lable.setText(f"NO OF Data : {Total}")
        self.tableWidget_2.setRowCount(Total)
        for row, datadict in enumerate(data_set):
            #print("row",row)
            ID = str(data_set[row][0])
            Defect_Size = str(data_set[row][1])
            Time = str(data_set[row][2]) 
            #End_time = str(datadict[3])
            #self.tableWidget_2.setItem(row,0, QTableWidgetItem(ID))
            self.tableWidget_2.setItem(row,0, QTableWidgetItem(Defect_Size))
            self.tableWidget_2.setItem(row,1, QTableWidgetItem(Time))
            #self.tableWidget.setItem(row,4, QTableWidgetItem(time_duration))
            header = self.tableWidget_2.horizontalHeader()
           #header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            #header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            #header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            # if row < len(data_set)-1:
            #     end_time =  data_set[row+1][2] 
            #     End_time =str(end_time)
            #     self.tableWidget_2.setItem(row,3, QTableWidgetItem(End_time))
    

    def fetch_ALL_config(self):
        summaryStr = "Please wait. The data is getting Fetched"
        self.summary_data_lable.setText(summaryStr)
        Machine_Name = self.batch_no_lineEdit.text().upper()
        from_temp_var = self.from_date.date()
        print(from_temp_var)
        to_temp_var = self.to_date.date()
        print(to_temp_var)

        if to_temp_var.toPyDate() < from_temp_var.toPyDate():
            self.show_message("To date should be greater than from date")
            return
        startDate = str(from_temp_var.toPyDate())+" 00:00:00"
        endDate = str(to_temp_var.toPyDate())+" 23:59:00"
        if Machine_Name == "CSM1":
            try:
                    db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                    user=db_user,         # your username
                                    passwd=db_pass,  # your password
                                    db="Refinary3_CSM1")
                    cur = db_select.cursor()
                    #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                    query=f"select ID, DEFECT_SIZE,DATE_TIME from Refinary3_CSM1.CONFIGURATIONS_Test order by DATE_TIME desc limit 10;"               
                    cur.execute(query)
                    data_set = cur.fetchall()
                    cur.close()
                    db_select.close()
                    print(data_set)
            except Exception as e:
                    print(e)
                    uilogger.critical(f"data record : "+ str(e))
            return data_set
            
        elif Machine_Name == "CSM2":
            try:
                    db_select = pymysql.connect(host=db_host,    # your host, usually localhost
                                    user=db_user,         # your username
                                    passwd=db_pass,  # your password
                                    db="Refinary3_CSM1")
                    cur = db_select.cursor()
                    #query = f"SELECT * FROM `Refinary3_CSM1`.`Auto` where Start_Time >= '{startDate}' or End_Time <= '{endDate}';"
                    query=f"select ID, DEFECT_SIZE,DATE_TIME from Refinary3_CSM2.CONFIGURATIONS_Test order by DATE_TIME desc limit 10;"               
                    cur.execute(query)
                    data_set = cur.fetchall()
                    cur.close()
                    db_select.close()
            except Exception as e:
                    print(e)
                    uilogger.critical(f"data record : "+ str(e))
            return data_set
        elif Machine_Name == "":
            self.summary_data_lable.setText(f"Please select the Machine name ")
    

    def config_show_All_data(self):
        data_set = self.fetch_ALL_config()
        Total = len(data_set)
        self.summary_data_lable.setText(f"NO OF Data : {Total}")
        self.tableWidget_2.setRowCount(Total)
        for row, datadict in enumerate(data_set):
            #print("row",row)
            ID = str(data_set[row][0])
            Defect_Size = str(data_set[row][1])
            Time = str(data_set[row][2]) 
            #End_time = str(datadict[3])
            #self.tableWidget_2.setItem(row,0, QTableWidgetItem(ID))
            self.tableWidget_2.setItem(row,0, QTableWidgetItem(Defect_Size))
            self.tableWidget_2.setItem(row,1, QTableWidgetItem(Time))
            #self.tableWidget.setItem(row,4, QTableWidgetItem(time_duration))
            header = self.tableWidget_2.horizontalHeader()
           #header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
            #header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            #header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
            # if row < len(data_set)-1:
            #     end_time =  data_set[row+1][2] 
            #     End_time =str(end_time)
            #     self.tableWidget_2.setItem(row,3, QTableWidgetItem(End_time))
   

                    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    data_record_object = DataRecord_Window()
    data_record_object.show()
    
    app.exec()
