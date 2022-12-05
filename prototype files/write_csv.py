import csv
import mysql.connector
import os
from datetime import datetime
import xlsxwriter


try:
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Admin123",
    database="companion_app"
    )

    mycursor = mydb.cursor()                

except mysql.connector.Error as err:
            print("oopsie poopsie")

print("start")
username = os.getlogin()
path = str("C:/Users/" + username)
#directory = str(path + '/Documents/Access Records.xlsx')
directory = str(path + '/Desktop/Access Records.xlsx')
print("test1")

# C:\Users\DURAN\Desktop

outWorkBook = xlsxwriter.Workbook(directory)
outsheet = outWorkBook.add_worksheet()
print("test2")

outsheet.write("A1", "Date & Time")
outsheet.write("B1", "Responder ID")
outsheet.write("C1", "Responder Name")
outsheet.write("D1", "Responder Course")
outsheet.write("E1", "Patient ID")
outsheet.write("F1", "Patient Name")
outsheet.write("G1", "Patient Course")
outsheet.write("H1", "Patient Gender")
outsheet.write("J1", "Injury")
print("test3")

mycursor.execute("SELECT * FROM access_records")
result = mycursor.fetchall()
print("test4")

column1 = [item[0] for item in result]
column2 = [item[1] for item in result]
column3 = [item[2] for item in result]
column4 = [item[3] for item in result]
column5 = [item[4] for item in result]
column6 = [item[5] for item in result]
column7 = [item[6] for item in result]
column8 = [item[7] for item in result]
column9 = [item[8] for item in result]
print("test5")

for item in range(len(column1)):
    outsheet.write(item + 1, 0, column1[item])
    outsheet.write(item + 1, 1, column2[item])
    outsheet.write(item + 1, 2, column3[item])
    outsheet.write(item + 1, 3, column4[item])
    outsheet.write(item + 1, 4, column5[item])
    outsheet.write(item + 1, 5, column6[item])
    outsheet.write(item + 1, 6, column7[item])
    outsheet.write(item + 1, 7, column8[item])
    outsheet.write(item + 1, 8, column9[item])
    print("test6")

outsheet.write("K1", "Total Profit")
outsheet.write("K2", "something")
print("test7")

outWorkBook.close()
print("finish")