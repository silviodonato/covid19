#!/usr/bin/python3
import sys
from datetime import datetime, timedelta
from convertCSVtoR import beginDate, endDate

applySF = True

nuovi_positivi_sfs ={}
nuovi_positivi_sfs[0] = 1.019799
nuovi_positivi_sfs[1] = 1.438239
nuovi_positivi_sfs[2] = 1.108412
nuovi_positivi_sfs[3] = 0.936199
nuovi_positivi_sfs[4] = 0.855101
nuovi_positivi_sfs[5] = 0.788904
nuovi_positivi_sfs[6] = 0.853346

deceduti_sfs = {}
deceduti_sfs[0] = 1.374735
deceduti_sfs[1] = 1.047937
deceduti_sfs[2] = 0.804842
deceduti_sfs[3] = 0.903648
deceduti_sfs[4] = 0.895749
deceduti_sfs[5] = 0.933157
deceduti_sfs[6] = 1.039933

fileName = sys.argv[1]
print(fileName)

beginDate = datetime(2020, 8, 1)
endDate = datetime(2021, 5, 15)

beginDateSF = datetime(2020, 2, 1) ## to apply the SFs in the proper order

file_ = open(fileName,'r')

todos = [
    "nuovi_positivi",
    "deceduti",
    "ingressi_terapia_intensiva",
]
index = {}
files = {}
prevValue = {}

todoIndex = []
firstLine = True
for l in file_.readlines():
    if firstLine:
        labels = l.split(",")
        print(labels)
        for todo in todos:
            index[todo] = labels.index(todo)
            files[todo] = ''
            prevValue[todo] = "0"
        index["data"] = labels.index("data")
        firstLine = False
    else:
        els = l.split(",")
        data = els[index["data"]]
        yyyy, mm, dd = data.split("T")[0].split("-")
        date = datetime(int(yyyy), int(mm), int(dd))
        if date>beginDate:
            for todo in todos:
                valuet = els[index[todo]][:]
                if valuet == "": valuet = "0"
                if todo == "deceduti": 
                    value = str(int(valuet) - int(prevValue[todo]))
                else:
                    value = valuet
                if int(value)<0: value="0"
                if applySF:
                    sf_day = ((date-beginDateSF).days-1)%7
                    if todo == "deceduti":
                        sfs = deceduti_sfs
                    else:
                        sfs = nuovi_positivi_sfs
                    value = str(int(float(value)*sfs[sf_day] + 0.5))
                if todo == "nuovi_positivi":
                    print (date, sfs[sf_day], value)
                nl = "%s-%s-%s %s 0\n"%(yyyy, mm, dd, value)
                files[todo] += nl
                prevValue[todo] = valuet[:]
print(date)

while date<endDate:
    date += timedelta(days=1)
    for todo in todos:
        nl = "%s %s 0\n"%(date.strftime("%Y-%m-%d"), 0) #prevValue[todo]
        files[todo] += nl

file_.close()

#print(files)

for todo in todos:
    newfile = open("dpc_%s.Rdata"%todo,'w')
    newfile.write(files[todo])
    newfile.close()

