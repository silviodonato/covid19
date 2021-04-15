#!/usr/bin/python3
import sys
from datetime import datetime

fileName = sys.argv[1]
print(fileName)

file_ = open(fileName,'r')

todos = [
    "nuovi_positivi",
    "deceduti",
    "ingressi_terapia_intensiva",
]
index = {}
files = {}

todoIndex = []
firstLine = True
for l in file_.readlines():
    if firstLine:
        labels = l.split(",")
        print(labels)
        for todo in todos:
            index[todo] = labels.index(todo)
            files[todo] = ''
        index["data"] = labels.index("data")
        firstLine = False
    else:
        els = l.split(",")
        data = els[index["data"]]
        yyyy, mm, dd = data.split("T")[0].split("-")
        if int(yyyy)<=2020 and int(mm)<=2: continue
        for todo in todos:
            value = els[index[todo]]
            if value == "": value = "0"
            nl = "%s-%s-%s %s 0\n"%(yyyy, mm, dd, value)
            files[todo] += nl

file_.close()

#print(files)

for todo in todos:
    newfile = open("dpc_%s.Rdata"%todo,'w')
    newfile.write(files[todo])
    newfile.close()

