from ast import parse
from datetime import datetime
import time, re

print("hello world")

#sample_data = "TUPC-18-0516 EDELLON JY BET-COET-C 5514"

sample_data = input("enter student ID:")
key="TUPC"
key_index = sample_data.find(key)
lkey=int(4)


if key_index < 0:
    print("not valid tupc student ID")
else:
    identifier= sample_data[key_index:key_index+lkey]
    print("key index is:" + str(key_index))
    print("identifier is: " + identifier)
    print("valid TUPC student ID")
    print(datetime.now())


    regexp=re.compile(r'[a-zA-z0-9_|^&+\-%*/=!>]+')
    #regexp2=re.compile(r'[0-9]')
    parsed_text = regexp.findall(sample_data)
    #regexp2.findall(sample_data)
    print(parsed_text)
    #print(regexp2.findall(sample_data))
    fullname = str(parsed_text[1]+" "+ parsed_text[2])

    print("student id is: " + parsed_text[0])
    print("full name is: " + fullname)
    
