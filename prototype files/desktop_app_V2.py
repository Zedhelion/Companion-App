from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView, QTableWidgetItem
import mysql.connector
import socket
import tqdm
import os
import csv
from time import sleep
import threading
from datetime import datetime
import xlsxwriter

class Ui_MainWindow(object):

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

    def display_data(self):
        print("refresh")
        try:
            try:
                self.mycursor.execute("SELECT * FROM access_records")
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
        except:
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
        filesize = int(filesize)

        progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
        with open(filename, "wb") as f:
            while True:
                bytes_read = client_socket.recv(BUFFER_SIZE)
                if not bytes_read:    
                    break
                f.write(bytes_read)
                progress.update(len(bytes_read))
        
        #self.writeData
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
        pgender = row[7]
        injury = row[8]

        try:
            sql = "INSERT INTO access_records (date_time, responder_id, responder_name, responder_course, patient_id, patient_name, patient_course, patient_gender, injury) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            value = (date_time, r_id, rname, rcourse, p_id, pname, pcourse, pgender, injury)
            self.mycursor.execute(sql, value)
            self.mydb.commit()

        except mysql.connector.Error as err:
                    self.errorDisplay(err.errno, err.sqlstate, err.msg)

        client_socket.close()
        s.close()
        self.display_data()
        self.receive_data()

    def start_threading(self):
        x = threading.Thread(target=self.receive_data)
        x.start()
        print(threading.activeCount())
    
    def export(self):
        print("export")
        self.username = os.getlogin()
        self.path = str("C:/Users/" + self.username)
        self.directory = str(self.path + '/Desktop/Access Records.xlsx')
        
        self.outWorkBook = xlsxwriter.Workbook(self.directory)
        self.outsheet = self.outWorkBook.add_worksheet()

        self.outsheet.write("A1", "Date & Time")
        self.outsheet.write("B1", "Responder ID")
        self.outsheet.write("C1", "Responder Name")
        self.outsheet.write("D1", "Responder Course")
        self.outsheet.write("E1", "Patient ID")
        self.outsheet.write("F1", "Patient Name")
        self.outsheet.write("G1", "Patient Course")
        self.outsheet.write("H1", "Patient Gender")
        self.outsheet.write("J1", "Injury")
        
        self.mycursor.execute("SELECT * FROM access_records")
        self.result = self.mycursor.fetchall()
        
        self.column1 = [item[0] for item in self.result]
        self.column2 = [item[1] for item in self.result]
        self.column3 = [item[2] for item in self.result]
        self.column4 = [item[3] for item in self.result]
        self.column5 = [item[4] for item in self.result]
        self.column6 = [item[5] for item in self.result]
        self.column7 = [item[6] for item in self.result]
        self.column8 = [item[7] for item in self.result]
        self.column9 = [item[8] for item in self.result]

        for item in range(len(self.column1)):
                self.outsheet.write(item + 1, 0, self.column1[item])
                self.outsheet.write(item + 1, 1, self.column2[item])
                self.outsheet.write(item + 1, 2, self.column3[item])
                self.outsheet.write(item + 1, 3, self.column4[item])
                self.outsheet.write(item + 1, 4, self.column5[item])
                self.outsheet.write(item + 1, 5, self.column6[item])
                self.outsheet.write(item + 1, 6, self.column7[item])
                self.outsheet.write(item + 1, 7, self.column8[item])
                self.outsheet.write(item + 1, 8, self.column9[item])

        self.outWorkBook.close()

    def setupUi(self, MainWindow):
        ################## call functions ###################
        self.connectDatabase()
        self.start_threading()
        ##################### UI STUFF ######################
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.WindowModal)
        MainWindow.resize(1920, 1080)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(1920, 1080))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(1920, 1080))
        self.centralwidget.setObjectName("centralwidget")
        self.Background = QtWidgets.QLabel(self.centralwidget)
        self.Background.setGeometry(QtCore.QRect(0, 0, 1981, 1083))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Background.sizePolicy().hasHeightForWidth())
        self.Background.setSizePolicy(sizePolicy)
        self.Background.setMinimumSize(QtCore.QSize(1920, 1080))
        self.Background.setMouseTracking(True)
        self.Background.setFocusPolicy(QtCore.Qt.NoFocus)
        self.Background.setStyleSheet("background-color: qlineargradient(spread:reflect, x1:0, y1:0, x2:0.46, y2:0.4375, stop:0 rgba(255, 171, 114, 255), stop:1 rgba(255, 122, 105, 255));")
        self.Background.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.Background.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.Background.setText("")
        self.Background.setPixmap(QtGui.QPixmap("abstract-white-graphic-design-presentation-background-web-template_156943-914.png"))
        self.Background.setScaledContents(True)
        self.Background.setObjectName("Background")
        self.topbanner = QtWidgets.QLabel(self.centralwidget)
        self.topbanner.setGeometry(QtCore.QRect(0, 0, 1920, 131))
        self.topbanner.setMinimumSize(QtCore.QSize(680, 0))
        self.topbanner.setMaximumSize(QtCore.QSize(1920, 1080))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(48)
        font.setBold(True)
        font.setWeight(75)
        self.topbanner.setFont(font)
        self.topbanner.setStyleSheet("background-color: rgb(195, 29, 57);\n"
"color: rgb(0, 0, 0);\n"
"")
        self.topbanner.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.topbanner.setFrameShadow(QtWidgets.QFrame.Plain)
        self.topbanner.setAlignment(QtCore.Qt.AlignCenter)
        self.topbanner.setObjectName("topbanner")
        self.AccessHistory = QtWidgets.QLabel(self.centralwidget)
        self.AccessHistory.setGeometry(QtCore.QRect(620, 214, 680, 61))
        self.AccessHistory.setMaximumSize(QtCore.QSize(680, 1080))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.AccessHistory.setFont(font)
        self.AccessHistory.setStyleSheet("background-color: rgb(209, 209, 209);")
        self.AccessHistory.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.AccessHistory.setObjectName("AccessHistory")
        self.TheCompanionApp = QtWidgets.QLabel(self.centralwidget)
        self.TheCompanionApp.setGeometry(QtCore.QRect(620, 160, 680, 61))
        self.TheCompanionApp.setMaximumSize(QtCore.QSize(1920, 1080))
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
        self.TUPLOGO = QtWidgets.QLabel(self.centralwidget)
        self.TUPLOGO.setGeometry(QtCore.QRect(630, 170, 91, 91))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.TUPLOGO.sizePolicy().hasHeightForWidth())
        self.TUPLOGO.setSizePolicy(sizePolicy)
        self.TUPLOGO.setMaximumSize(QtCore.QSize(115, 115))
        self.TUPLOGO.setStyleSheet("")
        self.TUPLOGO.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.TUPLOGO.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.TUPLOGO.setText("")
        self.TUPLOGO.setPixmap(QtGui.QPixmap("306923334_441149988133144_8535244359366534707_n.png"))
        self.TUPLOGO.setScaledContents(True)
        self.TUPLOGO.setObjectName("TUPLOGO")
        self.GreenCross = QtWidgets.QLabel(self.centralwidget)
        self.GreenCross.setGeometry(QtCore.QRect(1200, 170, 91, 91))
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


        ######################## REFRESH BUTTON ###############################
        self.refreshButton = QtWidgets.QPushButton(self.centralwidget)
        self.refreshButton.setGeometry(QtCore.QRect(960, 950, 341, 61))
        self.refreshButton.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.refreshButton.setFont(font)
        self.refreshButton.setStyleSheet("image: url(:/refresh/refresh.png);\n"
"background-image: url(:/refresh/refresh.png);\n"
"background-color: rgb(209, 209, 209);")
        self.refreshButton.setText("")
        self.refreshButton.setObjectName("refreshButton")
        self.refreshButton.clicked.connect(self.display_data)


        ######################## EXPORT BUTTON ###############################
        self.exportButton = QtWidgets.QPushButton(self.centralwidget)
        self.exportButton.setGeometry(QtCore.QRect(620, 950, 331, 61))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(8)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exportButton.sizePolicy().hasHeightForWidth())
        self.exportButton.setSizePolicy(sizePolicy)
        self.exportButton.setMinimumSize(QtCore.QSize(0, 45))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift SemiBold")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.exportButton.setFont(font)
        self.exportButton.setStyleSheet("image: url(:/export/export.png);\n"
"background-image: url(:/export/export.png);\n"
"background-color: rgb(209, 209, 209);")
        self.exportButton.setText("")
        self.exportButton.setObjectName("exportButton")
        self.exportButton.clicked.connect(self.export)


        ############################## TABLE WIDGET ################################ 
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(310, 300, 1341, 631))
        self.tableWidget.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(9)
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
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setPointSize(11)
        item.setFont(font)
        self.tableWidget.setHorizontalHeaderItem(8, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(150)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "First Aid Cabinet"))
        self.topbanner.setText(_translate("MainWindow", "The Companion App"))
        self.AccessHistory.setText(_translate("MainWindow", "Access History"))
        self.TheCompanionApp.setText(_translate("MainWindow", "First Aid Cabinet"))
        self.refreshButton.setToolTip(_translate("MainWindow", "<html><head/><body><p>Refreshes the displayed information</p></body></html>"))
        self.exportButton.setToolTip(_translate("MainWindow", "<html><head/><body><p>Exports CSV file of stored data</p></body></html>"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "Date & Time"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "Responder ID"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "Responder Name"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "Responder Course"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "Patient ID"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "Patient Name"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "Patient Course"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "Patient Gender"))
        item = self.tableWidget.horizontalHeaderItem(8)
        item.setText(_translate("MainWindow", "Injury"))
        self.display_data()
        
import test

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
