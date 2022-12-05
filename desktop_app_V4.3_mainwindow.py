from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
import mysql.connector
import socket
import os
import csv
from time import sleep
import threading
import xlsxwriter
from emergency_history import Ui_emergency_history
import vlc
import tkinter
from tkinter import * 
from tkinter import messagebox as mb

class Ui_Desktop_MainWindow(QtWidgets.QMainWindow):

    def connectDatabase(self):

        try:
            self.mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Admin123",
                database="companion_app"
                )

            self.mycursor = self.mydb.cursor()

        except mysql.connector.Error as err:
            self.errorDisplay(err.errno, err.sqlstate, err.msg)

    def errorDisplay(self, errorCode, sqlState, text):
        error1 = "Error Code: " + str(errorCode)
        error2 = "SQL State: " + sqlState
        error3 = "Description: "+ text
        QMessageBox.critical(self,"Error", error1 + error2 + error3)

    def display_dates(self):
        try:
            self.mycursor.execute("SELECT DISTINCT date_time_a FROM access_history")
            self.distinct_names = self.mycursor.fetchall()
            self.column1 = [item[0] for item in self.distinct_names]
            self.searchcomboBox.addItems(self.column1)

        except mysql.connector.Error as err:
            self.errorDisplay(err.errno, err.sqlstate, err.msg)
    
    def export(self):
        exporter = QMessageBox.question(self, 'Notice', 'This will erase the previous file, continue anyway?', 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if exporter == QMessageBox.Yes:
            self.username = os.getlogin()
            self.path = str("C:/Users/" + self.username)
            self.directory = str(self.path + '/Desktop/Access History.xlsx')
            
            self.outWorkBook = xlsxwriter.Workbook(self.directory)
            self.outsheet = self.outWorkBook.add_worksheet()

            self.outsheet.write("A1", "Date & Time")
            self.outsheet.write("B1", "Responder ID")
            self.outsheet.write("C1", "Responder Name")
            self.outsheet.write("D1", "Responder Course")
            self.outsheet.write("E1", "Injury")
            self.outsheet.write("F1", "Body Part")
            
            self.mycursor.execute("SELECT * FROM access_history")
            self.result = self.mycursor.fetchall()
            
            self.column1 = [item[0] for item in self.result]
            self.column2 = [item[1] for item in self.result]
            self.column3 = [item[2] for item in self.result]
            self.column4 = [item[3] for item in self.result]
            self.column5 = [item[4] for item in self.result]
            self.column6 = [item[5] for item in self.result]

            for item in range(len(self.column1)):
                    self.outsheet.write(item + 1, 0, self.column1[item])
                    self.outsheet.write(item + 1, 1, self.column2[item])
                    self.outsheet.write(item + 1, 2, self.column3[item])
                    self.outsheet.write(item + 1, 3, self.column4[item])
                    self.outsheet.write(item + 1, 4, self.column5[item])
                    self.outsheet.write(item + 1, 5, self.column6[item])

            self.outWorkBook.close()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowIcon(QtGui.QIcon('green_cross.png'))
            msg.setText("Data Has Been Exported as Excel File")
            msg.setWindowTitle("Success")
            msg.exec_()
        else:
            pass


    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Exit', 'Are you sure you want to exit?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def display_data(self):
        print("refresh")
        
        try:
            try:
                self.mycursor.execute("SELECT * FROM access_history")
                self.result = self.mycursor.fetchall()

            except mysql.connector.Error as err:
                self.errorDisplay(err.errno, err.sqlstate, err.msg)

            self.numcols = len(self.result[0])
            self.numrows = len(self.result)

            self.tableWidget.setColumnCount(self.numcols)
            self.tableWidget.setRowCount(self.numrows)

            for row in range(self.numrows):
                for column in range(self.numcols):
                    self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.result[row][column])))
            
            self.display_dates()
        except:
            print("error")
            pass

    def receive_data(self):

        SERVER_HOST = "0.0.0.0"
        SERVER_PORT = 4899
        BUFFER_SIZE = 4096
        SEPARATOR = "<SEPARATOR>"

        s = socket.socket()

        s.bind((SERVER_HOST, SERVER_PORT))

        s.listen(5)

        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

        client_socket, address = s.accept() 

        # if below code is executed, that means the sender is connected
        print(f"[+] {address} is connected.")

        received = client_socket.recv(BUFFER_SIZE).decode()
        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)

        with open(filename, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    break
                f.write(bytes_read)

        ################## READ CSV FILE ######################
        with open(filename, 'r') as file:
           csvreader = csv.reader(file)
           for row in csvreader:
                print(row)

        print("attempt to extract data from rows")
        date_time = row[0]
        r_id = row[1]
        rname = row[2]
        rcourse = row[3]
        injury = row[4]
        bodypart = row[5]

        print("reading done")        

        ################## WRITE DATA FROM CSV FILE TO DATABASE ######################

        try:
            print("attempt to write to db")
            sql = "INSERT INTO access_history (date_time_a, responder_id, responder_name, responder_course, injury, body_part) VALUES (%s,%s,%s,%s,%s,%s)"
            value = (date_time, r_id, rname, rcourse, injury, bodypart)
            self.mycursor.execute(sql, value)
            self.mydb.commit()
            
        except mysql.connector.Error as err:
            self.errorDisplay(err.errno, err.sqlstate, err.msg)

        client_socket.close()
        s.close()
        print("client closed")

        ##################### ALERT MESSAGE BOX ####################################

        self.data = str("On " + date_time + ", Responder " + r_id + " " + rname + " of " + rcourse + ", responded to " + injury + " on " + bodypart)

        def play():
            print("test2")      
            try:                
                while True:
                    p = vlc.MediaPlayer("alarm.mp3")
                    p.play() 
                    sleep(1)
                    p.stop()                    
                    if self.stop_thread:
                        break
            except:
                pass

        self.stop_thread = False
        t1 = threading.Thread(target = play)
        t1.start()

        self.data = str("On " + date_time + ", Responder " + r_id + " " + rname + " of " + rcourse + ", responded to " + injury + " on " + bodypart)

        root = tkinter.Tk()
        root.withdraw()

        alert = mb.showwarning('Emergency Received', self.data)

        root.destroy()

        if alert == 'ok' :
            try:
                self.stop_thread = True
                t1.join()
            except:
                pass
 
        else :            
            print("else")
        
        self.display_data()
        self.receive_data()
        
    def complete_data(self):
        ################## RECEIVE DATA ######################
        SERVER_HOST = "0.0.0.0"
        SERVER_PORT = 4799
        BUFFER_SIZE = 4096
        SEPARATOR = "<SEPARATOR>"

        s = socket.socket()

        s.bind((SERVER_HOST, SERVER_PORT))

        s.listen(5)
        print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")

        client_socket, address = s.accept() 
        # if below code is executed, that means the sender is connected
        print(f"[+] {address} is connected.")

        received = client_socket.recv(BUFFER_SIZE).decode()
        filename = received.split(SEPARATOR)
        filename = os.path.basename(filename)

        with open(filename, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    break
                f.write(bytes_read)
        
        ################## READ CSV FILE ######################
        with open(filename, 'r') as file:
           csvreader = csv.reader(file)
           for row in csvreader:
                print(row)

        date_time = row[0]
        r_id = row[1]
        rname = row[2]
        rcourse = row[3]
        p_id = row[4]
        pname = row[5]
        pcourse = row[6]
        injury = row[7]
        bodypart = row[8]
        pgender = row[9]
        p_age = row[10]

        ################## WRITE DATA FROM CSV FILE TO DATABASE ######################
        
        try:
            sql = "INSERT INTO emergency_history (date_time_e, responder_id, responder_name, responder_course, patient_id, patient_name, patient_course, injury, body_part, patient_gender, patient_age) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            value = (date_time, r_id, rname, rcourse, p_id, pname, pcourse, injury, bodypart, pgender, p_age)
            self.mycursor.execute(sql, value)
            self.mydb.commit()

        except mysql.connector.Error as err:
                    self.errorDisplay(err.errno, err.sqlstate, err.msg)

        client_socket.close()
        s.close()
        
        self.display_data()
        self.complete_data()


    def start_threading(self):
        global x
        x = threading.Thread(target=self.receive_data)
        x.setDaemon(True)
        x.start()
        
        global y
        y = threading.Thread(target=self.complete_data)
        y.setDaemon(True)
        y.start()

        print(threading.active_count())

    def search(self):
        print("search")
        self.searched_term = self.searchcomboBox.currentText()
        while (self.tableWidget.rowCount()>0):
            self.tableWidget.removeRow(0)
       
        try:
            try:
                sql = "SELECT * FROM access_history WHERE date_time_a LIKE %s OR responder_id LIKE %s OR responder_name LIKE %s OR responder_course LIKE %s OR injury LIKE %s OR body_part LIKE %s"
                print(sql)
                value = ("%" + self.searched_term + "%","%" + self.searched_term + "%","%" + self.searched_term + "%","%" + self.searched_term + "%","%" + self.searched_term + "%","%" + self.searched_term + "%")
                self.mycursor.execute(sql, value)
                self.result = self.mycursor.fetchall()

                self.numcols = len(self.result[0])
                self.numrows = len(self.result)

                self.tableWidget.setColumnCount(self.numcols)
                self.tableWidget.setRowCount(self.numrows)

                for row in range(self.numrows):
                        for column in range(self.numcols):
                            if isinstance(self.result[row][column], int):
                                self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.result[row][column])))
                            elif isinstance(self.result[row][column], float):
                                self.tableWidget.setItem(row, column, QTableWidgetItem(str(self.result[row][column])))
                            else:
                                self.tableWidget.setItem(row, column, QTableWidgetItem((self.result[row][column])))
            except mysql.connector.Error as err:
                self.errorDisplay(err.errno, err.sqlstate, err.msg)
        except:
            pass


    
    
    def setupUi(self, MainWindow):
        ################## call functions ###################
        self.connectDatabase()
        self.start_threading()
        
        #################### UI STUFF ######################
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.WindowModal)
        MainWindow.resize(1378, 1037)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("green_cross.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(278, 168, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.TUPLOGO = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TUPLOGO.sizePolicy().hasHeightForWidth())
        self.TUPLOGO.setSizePolicy(sizePolicy)
        self.TUPLOGO.setMaximumSize(QtCore.QSize(115, 115))
        self.TUPLOGO.setAutoFillBackground(False)
        self.TUPLOGO.setStyleSheet("")
        self.TUPLOGO.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.TUPLOGO.setFrameShadow(QtWidgets.QFrame.Plain)
        self.TUPLOGO.setText("")
        self.TUPLOGO.setPixmap(QtGui.QPixmap("306923334_441149988133144_8535244359366534707_n.png"))
        self.TUPLOGO.setScaledContents(True)
        self.TUPLOGO.setObjectName("TUPLOGO")
        self.horizontalLayout_3.addWidget(self.TUPLOGO)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QtCore.QSize(517, 80))
        self.frame.setMaximumSize(QtCore.QSize(16777215, 100))
        self.frame.setStyleSheet("background-color: rgb(209, 209, 209);")
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.TheCompanionApp = QtWidgets.QLabel(self.frame)
        self.TheCompanionApp.setMaximumSize(QtCore.QSize(1920, 80))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        self.TheCompanionApp.setFont(font)
        self.TheCompanionApp.setStyleSheet("background-color: rgb(209, 209, 209);\n"
"")
        self.TheCompanionApp.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.TheCompanionApp.setObjectName("TheCompanionApp")
        self.verticalLayout_2.addWidget(self.TheCompanionApp)
        self.AccessHistory = QtWidgets.QLabel(self.frame)
        self.AccessHistory.setMaximumSize(QtCore.QSize(680, 50))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.AccessHistory.setFont(font)
        self.AccessHistory.setStyleSheet("background-color: rgb(209, 209, 209);")
        self.AccessHistory.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.AccessHistory.setObjectName("AccessHistory")
        self.verticalLayout_2.addWidget(self.AccessHistory)
        spacerItem1 = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_3.addWidget(self.frame)
        self.GreenCross = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.GreenCross.sizePolicy().hasHeightForWidth())
        self.GreenCross.setSizePolicy(sizePolicy)
        self.GreenCross.setMaximumSize(QtCore.QSize(115, 115))
        self.GreenCross.setStyleSheet("")
        self.GreenCross.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.GreenCross.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.GreenCross.setText("")
        self.GreenCross.setPixmap(QtGui.QPixmap("green_cross.png"))
        self.GreenCross.setScaledContents(True)
        self.GreenCross.setObjectName("GreenCross")
        self.horizontalLayout_3.addWidget(self.GreenCross)
        spacerItem2 = QtWidgets.QSpacerItem(288, 168, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.gridLayout_3.addLayout(self.horizontalLayout_3, 1, 0, 1, 1)
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_20.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_20.addItem(spacerItem3)

        ######################## SEARCH BUTTON ###############################
        self.searchButton = QtWidgets.QPushButton(self.centralwidget)
        self.searchButton.setMaximumSize(QtCore.QSize(100, 16777215))
        self.searchButton.setObjectName("searchButton")
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        self.searchButton.setFont(font)
        self.searchButton.setStyleSheet("background-color: rgb(209, 209, 209);\n")
        self.horizontalLayout_20.addWidget(self.searchButton)
        self.searchButton.clicked.connect(self.search)

        ######################## SEARCH COMBO BOX ###############################
        self.searchcomboBox = QtWidgets.QComboBox(self.centralwidget)
        self.searchcomboBox.setMinimumSize(QtCore.QSize(400, 0))
        self.searchcomboBox.setMaximumSize(QtCore.QSize(400, 16777215))
        self.searchcomboBox.setEditable(True)
        self.searchcomboBox.setObjectName("searchcomboBox")
        self.horizontalLayout_20.addWidget(self.searchcomboBox)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_20.addItem(spacerItem4)
        self.gridLayout_3.addLayout(self.horizontalLayout_20, 2, 0, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem5 = QtWidgets.QSpacerItem(208, 458, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_4.addItem(spacerItem5)


        ############################## TABLE WIDGET ################################ 
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setMinimumSize(QtCore.QSize(0, 100))
        self.tableWidget.setMaximumSize(QtCore.QSize(903, 16777215))
        self.tableWidget.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(6)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(5, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(150)
        self.horizontalLayout_4.addWidget(self.tableWidget)
        spacerItem6 = QtWidgets.QSpacerItem(238, 458, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout_4.addItem(spacerItem6)
        self.gridLayout_3.addLayout(self.horizontalLayout_4, 3, 0, 1, 1)
        self.topbanner = QtWidgets.QLabel(self.centralwidget)
        self.topbanner.setMinimumSize(QtCore.QSize(680, 100))
        self.topbanner.setMaximumSize(QtCore.QSize(1920, 1080))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(48)
        font.setBold(True)
        font.setWeight(75)
        self.topbanner.setFont(font)
        self.topbanner.setStyleSheet("\n"
"background-color: rgb(0, 85, 0);\n"
"color: rgb(255, 255, 255);\n"
"")
        self.topbanner.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.topbanner.setFrameShadow(QtWidgets.QFrame.Plain)
        self.topbanner.setAlignment(QtCore.Qt.AlignCenter)
        self.topbanner.setObjectName("topbanner")
        self.gridLayout_3.addWidget(self.topbanner, 0, 0, 1, 1)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem7 = QtWidgets.QSpacerItem(428, 78, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem7)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        ######################## EXPORT BUTTON ###############################
        self.exportButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(8)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exportButton.sizePolicy().hasHeightForWidth())
        self.exportButton.setSizePolicy(sizePolicy)
        self.exportButton.setMinimumSize(QtCore.QSize(145, 45))
        self.exportButton.setMaximumSize(QtCore.QSize(16777215, 60))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.exportButton.setFont(font)
        self.exportButton.setStyleSheet("background-color: rgb(209, 209, 209);\n")
        self.exportButton.setText("")
        self.exportButton.setObjectName("exportButton")
        self.horizontalLayout.addWidget(self.exportButton)
        self.exportButton.clicked.connect(self.export)

        ######################## REFRESH BUTTON ###############################
        self.refreshButton = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.refreshButton.sizePolicy().hasHeightForWidth())
        self.refreshButton.setSizePolicy(sizePolicy)
        self.refreshButton.setMinimumSize(QtCore.QSize(145, 45))
        self.refreshButton.setMaximumSize(QtCore.QSize(16777215, 60))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(28)
        font.setBold(True)
        font.setWeight(75)
        self.refreshButton.setFont(font)
        self.refreshButton.setStyleSheet("background-color: rgb(209, 209, 209);")
        self.refreshButton.setText("")
        self.refreshButton.setObjectName("refreshButton")
        self.horizontalLayout.addWidget(self.refreshButton)
        self.refreshButton.clicked.connect(self.display_data)

        ######################## VIEW HISTORY BUTTON ###############################
        self.view_history_button = QtWidgets.QPushButton(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(8)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.view_history_button.sizePolicy().hasHeightForWidth())
        self.view_history_button.setSizePolicy(sizePolicy)
        self.view_history_button.setMinimumSize(QtCore.QSize(145, 45))
        self.view_history_button.setMaximumSize(QtCore.QSize(16777215, 60))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.view_history_button.setFont(font)
        self.view_history_button.setStyleSheet("\n"
"background-color: rgb(209, 209, 209);")
        self.view_history_button.setObjectName("view_history_button")
        self.horizontalLayout.addWidget(self.view_history_button)
        self.view_history_button.clicked.connect(self.open_emergency_history)


        self.horizontalLayout_5.addLayout(self.horizontalLayout)
        spacerItem8 = QtWidgets.QSpacerItem(408, 68, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem8)
        self.gridLayout_3.addLayout(self.horizontalLayout_5, 5, 0, 1, 1)
        self.gridLayout_4.addLayout(self.gridLayout_3, 0, 0, 1, 1)
        spacerItem9 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.gridLayout_4.addItem(spacerItem9, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "First Aid Cabinet"))
        self.TheCompanionApp.setText(_translate("MainWindow", "First Aid Cabinet"))
        self.AccessHistory.setText(_translate("MainWindow", "Access History"))
        self.searchButton.setText(_translate("MainWindow", "Search"))
        self.refreshButton.setText(_translate("MainWindow", "⟳"))
        self.exportButton.setText(_translate("MainWindow", "Export"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Date & Time"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Responder ID"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Responder Name"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Responder Course"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Injury"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Body Part"))
        self.topbanner.setText(_translate("MainWindow", "The Companion App"))
        self.exportButton.setToolTip(_translate("MainWindow", "<html><head/><body><p>Exports CSV file of stored data</p></body></html>"))
        self.refreshButton.setToolTip(_translate("MainWindow", "<html><head/><body><p>Refreshes the displayed information</p></body></html>"))
        self.view_history_button.setToolTip(_translate("MainWindow", "<html><head/><body><p>Exports CSV file of stored data</p></body></html>"))
        self.view_history_button.setText(_translate("MainWindow", "Emergency History"))
        self.display_data()

    def open_emergency_history(self):
        print("test")
        self.window = QtWidgets.QMainWindow()
        self.ui = Ui_emergency_history()
        self.ui.setupUi(self.window)
        self.window.show()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Desktop_MainWindow = QtWidgets.QMainWindow()
    Desktop_MainWindow = Ui_Desktop_MainWindow()
    ui = Ui_Desktop_MainWindow()
    ui.setupUi(Desktop_MainWindow)
    Desktop_MainWindow.show()
    sys.exit(app.exec_())
