#!/usr/bin/python3
import sys

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
            dd, mm, yyyy = data2.split("/")
            nl = "%s-%s-%s %s 0\n"%(yyyy, mm, dd, value)
            newfile.write(nl)

file_.close()
newfile.close()
