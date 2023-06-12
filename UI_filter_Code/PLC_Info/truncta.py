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
            tableWidget.setRowCount(len(data_set))
            for row in range(0,len(data_set)):
                Status = str(data_set[row][1])
                Start_Time = str(data_set[row][2])
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