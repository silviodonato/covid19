#!/usr/bin/python3
import sys
from datetime import datetime, timedelta

beginDate = datetime(2020, 8, 1)
endDate = datetime(2021, 9, 1)

print(endDate)

if __name__ == '__main__':
    fileName = sys.argv[1]
    print(fileName)
    
    file_ = open(fileName,'r')
    newfile = open(fileName.replace(".csv",".Rdata"),'w')
    
    for l in file_.readlines():
        els = l.split(",")
        if len(els)==3:
            iss_date, data, value = els
            value = value.replace("\n","")
            value = value.replace("<","")
            if ("/2021" in data or "/2020" in data):
                dd, mm, yyyy = data.split("/")
                date = datetime(int(yyyy), int(mm), int(dd))
                if date>beginDate:
                    nl = "%s %s 0\n"%(date.strftime("%Y-%m-%d"), value)
                    newfile.write(nl)
                    lastvalue = value

    lastvalue = 0
    while date<endDate:
        date += timedelta(days=1)
        nl = "%s %s 0\n"%(date.strftime("%Y-%m-%d"), lastvalue)
        newfile.write(nl)


    file_.close()
    newfile.close()
