#!/usr/bin/python3
import sys
from datetime import datetime

fileName = sys.argv[1]
print(fileName)

file_ = open(fileName,'r')
newfile = open(fileName.replace(".csv",".R"),'w')

for l in file_.readlines():
    els = l.split(",")
    if len(els)==3:
        data1, data2, value = els
        value = value.replace("\n","")
        value = value.replace("<","")
        if ("/2021" in data1 or "/2020" in data1) and ("/2021" in data2 or "/2020" in data2):
            dd1, mm1, yyyy1 = data1.split("/")
            dd, mm, yyyy = data2.split("/")
            if int(yyyy)<=2020 and int(mm)<=2: continue
            if ((datetime(int(yyyy),int(mm),int(dd)) - datetime(int(yyyy1),int(mm1),int(dd1))).days)>=-2: continue
            nl = "%s-%s-%s %s 0\n"%(yyyy, mm, dd, value)
            newfile.write(nl)

file_.close()
newfile.close()
