import ROOT
import csv
import copy
import array
import datetime
import pickle

rnd = ROOT.TRandom3()

scuola7=[
"Bolzano",
]

scuola14=[
"EmiliaRomagna",
"Lazio",
"Liguria",
"Lombardia",
"Marche",
"Piemonte",
"Toscana",
"Umbria",
"Valled'Aosta",
"Veneto",
"Sicilia",
"Molise",
]

scuola24=[
"Abruzzo",
"Calabria",
"Campania",
"Puglia",
"Sardegna",
]

#useLog = False
useLog = True
fixSigma = 8
#maxPar3 = 1E4
maxPar3 = 1
#minPar2,maxPar2 = 7.9, 8.1
#minPar2,maxPar2 = 7, 9
#minPar2,maxPar2 = 8, 8
#minPar2,maxPar2 = 7.5, 8.5
#minPar2,maxPar2 = 7, 9
#minPar2,maxPar2 = 8, 8
minPar2,maxPar2 = 5.5, 100
#minPar2,maxPar2 = 5.5, 7.5
#minPar2,maxPar2 = 5, 11
#minPar2,maxPar2 = 6.5-3, 6.5+3
maxConstExp = 1

colors = [
ROOT.kBlack,

ROOT.kYellow+1,
ROOT.kRed,
ROOT.kMagenta,
ROOT.kBlue,
ROOT.kCyan+1,
ROOT.kGray+1,

ROOT.kOrange,
ROOT.kPink,
ROOT.kViolet,
ROOT.kAzure,
ROOT.kTeal,
ROOT.kSpring,

ROOT.kGray,
] 

colors = colors *1000

maps = {
"America" : ["US","Canada","Ecuador"],
"Africa" : ["Algeria"],
"Europe" : ["Austria", "Belarus", "Belgium", "Croatia", "Czech Republic", "Denmark", "Finland", "France", "Germany", "Greece", "Iceland", "Ireland", "Italy", "Netherlands", "Norway", "Spain", "Sweden", "Switzerland", "UK", "Romania", "San Marino", "Portugal"],
"MiddleEast" : ["Azerbaijan", "Bahrain", "Iran", "Iraq", "Israel", "Kuwait", "Lebanon", "Qatar", "Oman", "United Arab Emirates",],
"FarEast" : ["Hong Kong", "Japan", "Malaysia", "Macau", "Singapore", "South Korea", "Taiwan", "India", "Thailand", "Vietnam",],
"Nord" : ["Valle d'Aosta",'FriuliVeneziaGiulia' , 'Bolzano', 'Veneto', 'Liguria', 'Piemonte', 'Lombardia', 'Emilia Romagna', 'Trento'],
"Centro" : ['Umbria', 'Marche', 'Toscana', 'Lazio', 'Abruzzo'],
"Sud" : ['Calabria', 'Molise',  'Campania', 'Sardegna', 'Sicilia',  'Basilicata', 'Puglia'],
}

#maps["Centro e Sud"] = maps["Centro"] + maps["Sud"]

positivi    = ROOT.kMagenta+1
contagiati  = ROOT.kBlue
ricoverati  = ROOT.kGreen+1
guariti     = ROOT.kRed
intensiva   = ROOT.kBlue+2
test        = ROOT.kGray+2
decessi     = ROOT.kBlack
storico     = ROOT.kMagenta
prediction  = ROOT.kMagenta+2
istat       = ROOT.kMagenta+1
funcExp     = ROOT.kMagenta
colorMap = {
    "positives": positivi ,
    "histo_confirmes": contagiati ,
    "recoveres":  guariti,
    "deaths":     decessi,
    "positiveToTestRatio":     funcExp,
    "deathToRecoverRatio":     contagiati,
    "deathDailyToRecoverRatio":     decessi,
    "newConfirmes":   contagiati,
    "newRecoveres":   guariti,
    "newDeaths":      decessi,
    "storico":        storico,
    "prediction":      prediction,
    "functionExp":      funcExp,
    "functionExp_newConfirmes":      funcExp,
    "functionExp_confirmes":      funcExp,
    "intensiva":      intensiva,
    "ricoverati":      ricoverati,
    "test":      test,
    "newIntensiva":      intensiva,
    "newRicoverati":      ricoverati,
    "newTest":      test,
    "Decessi":      decessi,
    "decessi":      decessi,
    "ISTAT":        istat,
    "predictionConfirmes":   contagiati,
    "predictionRecoveres":   guariti,
    "predictionDeaths":      decessi,
    "predictionIntensiva":      intensiva,
    "predictionRicoverati":      ricoverati,
    "predictionTest":      test,
}

labelMap = {
    "positives":  "Positivi",
    "confirmes":  "Casi totali",
    "recoveres":  "Guariti",
    "deaths":     "Decessi",
    "positiveToTestRatio":     "Tasso positivita'",
    "deathToRecoverRatio":     "Decessi/Guariti (cumulato)",
    "deathDailyToRecoverRatio":     "Decessi/Guariti (giornaliero)",
    "prediction":      "Prediction",
    "intensiva":      "Terapia Intensiva",
    "ricoverati":      "Ricoverati",
    "test":      "Tamponi",
    "newConfirmes":   "Casi totali",
    "newRecoveres":   "Guariti",
    "newDeaths":      "Decessi",
    "newIntensiva":      "Terapia Intensiva",
    "newRicoverati":      "Ricoverati",
    "newTest":      "Tamponi",
    "Decessi":      "Decessi",
    "decessi":      "Decessi",
    "ISTAT":        "#splitline{Decessi totali}{(eccesso ISTAT)}",
    "storico":      "#splitline{Media 2015-19}{(riscalata)}",
    "predictionConfirmes":   "Casi totali (prev.)",
    "predictionRecoveres":   "Guariti (prev.)",
    "predictionDeaths":      "Decessi (prev.)",
    "predictionIntensiva":      "Terapia Intensiva (prev.)",
    "predictionRicoverati":      "Ricoverati (prev.)",
    "predictionTest":      "Tamponi (prev.)",
}

def makeCompatible(dataISTAT, firstDateDay=24, firstDateMonth=2):
    for place in dataISTAT.keys()[:]:
        ## remove 0 as first digit (eg. 04/02/20 -> 4/2/20)
        for date in dataISTAT[place].keys()[:]:
            mm, dd, yy = date.split("/")
            mm, dd, yy = int(mm), int(dd), int(yy)
            if mm<firstDateMonth: 
                dd=firstDateDay
                mm=firstDateMonth
            if mm==firstDateMonth and dd<firstDateDay: dd=firstDateDay
            newDate = "%s/%s/%s"%(mm,dd,yy)
            if newDate!= date:
                if not newDate in dataISTAT[place]: dataISTAT[place][newDate] = {}
                for age in dataISTAT[place][date]:
                    if not age in dataISTAT[place][newDate]: dataISTAT[place][newDate][age] = [0] * len(dataISTAT[place][date][age])
                    for i in range(len(dataISTAT[place][date][age])):
#                        print dataISTAT[place][newDate]
#                        print dataISTAT[place][date]
                        dataISTAT[place][newDate][age][i] += dataISTAT[place][date][age][i]
                del dataISTAT[place][date] ## delete old date
        ## cancella i dati dei singoli comuni
        if len(place.split("_"))==3: del dataISTAT[place]
#        elif place=='Italia': del dataISTAT[place] ## avoid double counting
        elif len(place.split("_"))==2: dataISTAT[place.split("_")[1]] = dataISTAT.pop(place)
        elif place=='TrentinoAltoAdige/S\xfcdtirol': dataISTAT["TrentinoAltoAdige"] = dataISTAT.pop(place)
    return dataISTAT

def getGeneric(name, dictionary):
    for k in sorted(dictionary.keys(), key=len, reverse=True):
        if k in name:
            return dictionary[k]
    import pprint
    pprint.pprint(dictionary)
    print name
    raise Exception("Error getGeneric, not found %s"%name)
    return None

def getColor(name):
    out = getGeneric (name, colorMap)
    assert(type(out)==type(ROOT.kBlue))
#    print("getColor(%s) = %s"%(name, out))
    return out

def getLabel(name):
    out = getGeneric (name, labelMap)
    assert(type(out)==str)
    return out


def getData(row, i):
    try:
        value = int(row[i+4])
    except:
        print("WARNING: problems with '%s' '%s' at %i. The numeber is '%s'. I wil use 0."%(row[0],row[1],i+4,row[i+4]))
        value = 0
    state = row[0]
    country = row[1]
    if "Hubei" == state:
        if i < 22:
            value = value*1.2
#        if i < 30:
#            value = value*1.1
    elif "Shandong" == state:
        if i < 30:
            value = value*1.35
    return value

def regions(state, country, default = ["World"]):
    state = state.replace(",","")
    country = country.replace(",","")
    regions = set(default)
#    if state: regions.add(state)
    if country: regions.add(country)
    for zone in maps: 
        if country in maps[zone]: 
            regions.add(zone)
            if zone=="Europe" and country!="Italy": regions.add("Rest of Europe")
    if country=="Mainland China" and state!="Hubei": regions.add("Rest of China")
    if country!="Mainland China" and default[0]=="World": regions.add("Rest of World")
    if country!="Lombardia" and default[0]=="Italia": regions.add("FuoriLombardia")
    if country in scuola7:  regions.add("scuola7")
    if country in scuola14: regions.add("scuola14")
    if country in scuola24: regions.add("scuola24")
    if country!="Lombardia" and country!="Emilia Romagna" and country!="Veneto" and default[0]=="Italia": regions.add("FuoriLombardiaEmiliaVeneto")
#    print (state, country, regions)
    return regions
    
def fillData(fileName):
    data = {}
    dates = []
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                dates = row[4:]
            else:
                for place in regions(row[0], row[1]):
                    if not place in data: data[place]={}
                    for i, date in enumerate(dates):
                        if not date in data[place]: data[place][date] = 0
                        data[place][date] += getData(row, i)
            line_count += 1
    return data, dates

def fillDataISTATpickle(fileName, zerosuppression=0, pickleFileName="temp.pkl", writePickle=True):
    if writePickle:
        print "Writing pickle file"
        dataISTAT, dates = fillDataISTAT(fileName, zerosuppression)
        output = open(pickleFileName,'wb')
        pickle.dump(dataISTAT, output)
        pickle.dump(dates, output)
        output.close()
    else:
        print "Loading pickle file"
        inp = open(pickleFileName,'rb')
        dataISTAT = pickle.load(inp)
        dates = pickle.load(inp)
        inp.close()
    return dataISTAT, dates

maschiLab = "M_" # "MASCHI_"
femmLab   = "F_" # "FEMMINE_"

def fillDataISTAT(fileName, zerosuppression=0, pickleFileName="temp.pkl", writePickle=True):
    data = {}
    dates = []
    total = {}
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count ==0:
                labels = row[:]
            else:
                date = row[labels.index("GE")]
#                date = (datetime.date(year, int(date[0:2]),  int(date[2:4])) - datetime.date(year, 3,  1)).days
                date = "%s/%s/%s"%(date[0:2], date[2:4], "20")
                age = int(row[labels.index("CL_ETA")])
#                if not row[labels.index("NOME_REGIONE")]=="Lombardia": continue
#                if not row[labels.index("NOME_PROVINCIA")]=="Bergamo": continue
                if not date in dates: dates.append(date)
#                place = int(row[labels.index("COD_PROVCOM")])
#                if not place in placeMap: 
#                    placeMap[place] = (row[labels.index("NOME_COMUNE")], row[labels.index("NOME_PROVINCIA")], row[labels.index("NOME_REGIONE")])
                (regione, provincia, comune) = (row[labels.index("NOME_REGIONE")], row[labels.index("NOME_PROVINCIA")], row[labels.index("NOME_COMUNE")])
                regione = regione.replace("-","").replace(" ","")
                provincia = provincia.replace("-","").replace(" ","")
                comune = comune.replace("-","").replace(" ","")
                for place in ["%s_%s_%s"%(regione,provincia,comune),"%s_%s"%(regione,provincia),"%s"%(regione),"Italia"]:
                    if not place in data: data[place] = {}
                    if not place in total: total[place] = 0
                    if not date in data[place]: data[place][date] = {}
#                    if date in data[place] and age in data[place][date] and len(place.split("_"))>=3: print "WARNING: OVERWRITING DATA: %d %s %d"%(place, date, age)
                    if not (age in data[place][date]): data[place][date][age] = [0,0,0,0]
                    vals = (9999,9999)
                    if row[labels.index("%s20"%maschiLab)] != "n.d.":
                        vals = (int(row[labels.index("%s20"%maschiLab)]), int(row[labels.index("%s20"%femmLab)])) # M, F
                    if vals!=(9999,9999):
                        data[place][date][age][0] += vals[0] #M 2020
                        data[place][date][age][1] += vals[1] #F 2020
                        total[place] += vals[0]
                        total[place] += vals[1]
                        for year in ["19","18","17","16","15"]:
                            data[place][date][age][2] += int(row[labels.index(maschiLab+year) ]) #sum M 15-19
                            data[place][date][age][3] += int(row[labels.index(femmLab  +year)]) #sum F 15-19
            line_count+=1
    dates=sorted(dates)

    for place in total:
        if total[place]<=zerosuppression:
            del data[place]
            print "Deleting "+place

    return data, dates

    (regione, provincia, comune) = place.split("_")
    provincia = regione+"_"+provincia
    if not provincia in provinceMap: provinceMap[provincia] = set()
    if not regione in regioniMap: regioniMap[regione] = set()
    provinceMap[provincia].add(place)
    regioniMap[regione].add(place)

def fillDataRegioni(fileName, column_regione = "denominazione_regione"):
    data = {}
    dates = []
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
#            print "XXX",row
            if line_count ==0:
                labels = row[:]
            else:
                date = row[labels.index("data")].split(" ")[0].split("T")[0].replace("-0","-").replace("2020-","").replace("2021-","").replace("-","/").replace("/0","/")
                if "2020" in row[labels.index("data")]: date = date+"/20"
                if "2021" in row[labels.index("data")]: date = date+"/21"
                if not date in dates: dates.append(date)
                regione = row[labels.index(column_regione)]
                if regione == "Fuori Regione / Provincia Autonoma": continue
                if regione == "In fase di definizione/aggiornamento": continue
                if regione == "Friuli V. G. ": regione = "Friuli Venezia Giulia"
                regione = regione.replace(" ","")
                regione = regione.replace("-","")
                regione = regione.replace("P.A.","")
                if not regione in data: data[regione] = {}
  #              if date in data[regione]: print "WARNING: OVERWRITING DATA: %s %s"%(regione, date)
                data[regione][date] = {}
                for i,label in enumerate(labels):
                    data[regione][date][label] = row[i]
 #                   print regione, date, label, row[i]
            line_count+=1
    return data, dates

def selectComuniDatesAgeGender(dataISTAT, dates, places=None, ages=[], genders=[]):
    ## places == None -> do no merge places
    data = {}
    for place in dataISTAT:
        if places==None: 
            data[place] = {}
            for place_ in regions("", place, ["Italia"]):
                if place_ in dataISTAT: continue #skip if already existing (no double counting italia)
                data[place_] = {}
        if places!=None and len(places)>0 and not place in places: continue 
        for date in dates:
            if not date in dataISTAT[place]: 
                if places==None: data[place][date]=0
                continue
            for age in dataISTAT[place][date]:
                if len(ages)>0 and not age in ages: continue 
                for gender in [0,1,2,3]:
                    if len(genders)>0 and not gender in genders: continue 
                    if not places == None: 
                        data[date] = data[date] + dataISTAT[place][date][age][gender] if date in data else dataISTAT[place][date][age][gender]
                    else: 
                        data[place][date] = data[place][date] + dataISTAT[place][date][age][gender] if date in data[place] else dataISTAT[place][date][age][gender]
                        for place_ in regions("", place, ["Italia"]):
                            if place_ in dataISTAT: continue #skip if already existing (no double counting italia)
                            data[place_][date] = data[place_][date] + dataISTAT[place][date][age][gender] if date in data[place_] else dataISTAT[place][date][age][gender]
    return data

def getColumn(dataRegioni_, label, scaleFactor=1):
    data = {}
    for regione in dataRegioni_:
        for place in regions("", regione, ["Italia"]):
            if not place in data: data[place] = {}
            for date in dataRegioni_[regione]:
                if not date in data[place]: data[place][date] = 0
                if dataRegioni_[regione][date][label] == "": dataRegioni_[regione][date][label] = 0
                data[place][date] += int(dataRegioni_[regione][date][label])*scaleFactor
    return data

def newCases(cases, dates):
    newCases = {}
    for place in cases:
        newCases[place] = {}
        newCases[place][dates[0]] = 0
        for i in range(1, len(cases[place])):
#            print place, i, dates[i]
            newCases[place][dates[i]] = cases[place][dates[i]] - cases[place][dates[i-1]]
    return newCases

def shiftHisto(histo, shift):
    shiftedHisto = histo.Clone(histo.GetName()+"shifted")
    shiftedHisto.Reset()
    for i in range(len(shiftedHisto)):
        for j in range(len(histo)):
            if i+shift>0 and i+shift<len(shiftedHisto):
                shiftedHisto.SetBinContent(i, histo.GetBinContent(i-shift))
                shiftedHisto.SetBinError(i, histo.GetBinError(i-shift))
    return shiftedHisto

def getRatio(numerators, denominators):
    ratios = {}
    for place in numerators:
        ratios[place] = numerators[place].Clone("ratio"+place)
        ratios[place].Divide(numerators[place],denominators[place])
    return ratios


def smearData(dataUnsmeared, dates, daysSmearing):
    if daysSmearing>2:
        data = {}
        for place in dataUnsmeared:
            data[place] = {}
            for date in dates:
                if date in dataUnsmeared[place]:
                    data[place][date] = 0
                    count = 0
                    for j in range(daysSmearing):
                        idx = dates.index(date) - j
                        if idx>0:
                            data[place][date] += dataUnsmeared[place][dates[idx]]
                            count += 1
                    if count>0:
                        data[place][date] = data[place][date] / count
    else:
        data = copy.copy(dataUnsmeared)
    return data

def makeHistos(prefix, dataUnsmeared, dates, places, firstDate, lastDate, predictionDate, threshold=-1E30, cutTails=False, errorType=None, lineWidth=3, daysSmearing=1):
    data = smearData(dataUnsmeared, dates, daysSmearing)
    histos = {}
    for place in places:
        if not place in data: continue
        histos[place] = copy.copy(ROOT.TH1F(prefix+"_"+str(place)+str(rnd.Rndm()), str(place), predictionDate-firstDate+1, firstDate-0.5, predictionDate+0.5))
        if histos[place].GetXaxis().GetBinWidth(1)!=1.0:
            print str(place)
            print histos[place].GetXaxis().GetBinWidth(1)
            print firstDate, predictionDate
            print predictionDate-firstDate+1
            raise Exception("histos[place].GetXaxis().GetBinWidth(1)!=1.0")
        stop = False
        start = False
        histos[place].GetXaxis().SetNdivisions(7)
        for i in reversed(range(firstDate, predictionDate)):
            binx = histos[place].FindBin(i)
            date = dates[i]
#            print(binx,date)
            if type(date)==str and i%7==0: histos[place].GetXaxis().SetBinLabel(  binx, date[:-3] )
            error = 0.
            if date in data.values()[0]:
                if not date in data[place] or data[place][date]==0: 
#                    histos[place].SetBinContent(binx, 0)
#                    histos[place].SetBinError(binx, 0)
                    continue
                if errorType=='dictionary': ## if dictionary, data is (value, error)
                    value = data[place][date][0]
                    error = data[place][date][1]
                else:
#                    print place, date
                    value = data[place][date]
                    valueM1 = data[place][dates[i-1]] if i>=1 else value
                    valueP1 = data[place][dates[i+1]] if i<=lastDate else value
                    valueM1 = max(valueM1,0)
                    valueP1 = max(valueP1,0)
                    average = ((valueM1+valueP1)/2)
                    if errorType=='cumulative':
                        error = 1.+(data[place][dates[lastDate]] - value)**0.5    if (data[place][dates[lastDate]] - value) >=0 else 0
                    elif errorType=='3sqrtN':
                        error = 0.05*abs(value)+ 3*abs(value)**0.5
                        error = 3*(value)**0.5 if (value>=9 and (value-average)<=0.5*average) else abs(value-average)*2
                    elif errorType=='sqrtN':
                        error = (value)**0.5 if (value>=9 and (value-average)<=0.5*average) else abs(value-average)*2
                    else:
                        error = 9.+(value)**0.5+0*0.25*(value) if value>=9 else 12.+abs(value-9.)                    ## error 10 + sqrt(N) + 0*25% N
                        if i>=1: error = max(error, abs(value-valueM1))
                        if i<=lastDate: error = max(error, abs(value-valueP1))
                if True or value>threshold:
                    if True or not stop:
                            histos[place].SetBinContent(binx, value)
                            histos[place].SetBinError(binx, error)
                            start = True
        if cutTails: ### remove tail, if there are 2 days without new cases from the peak
                maxBin = histos[place].GetMaximumBin()
                for i in range(maxBin, predictionDate):
                        if histos[place].GetBinContent(i-1)==0 and histos[place].GetBinContent(i-2)==0: 
                                histos[place].SetBinContent(i, 0)
                                histos[place].SetBinError(i, 0)
                for i in reversed(range(firstDate, maxBin)):
                        if histos[place].GetBinContent(i+1)==0 and histos[place].GetBinContent(i+2)==0: 
                                histos[place].SetBinContent(i, 0)
                                histos[place].SetBinError(i, 0)

        color = colors[places.index(place)]
        histos[place].SetLineWidth(lineWidth)
        histos[place].SetLineColor(color)
    return histos

def fitErf(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ"):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        functs[place] = copy.copy(ROOT.TF1("functionErf"+place,"[0]*(1+TMath::Erf((x-[1])/[2])) + [3]",0,predictionDate))
        functs[place].SetParLimits(3,0,100)
        functs[place].SetParLimits(2,2,20)
        functs[place].SetParLimits(1,0,100)
        functs[place].SetParameters(6.60369e+02, 25, fixSigma, 0)
        functs[place].FixParameter(2, fixSigma)
        functs[place].FixParameter(3, 0)
#        h[place].Fit(functs[place],"0W","",0,lastDate)
        functs_res[place] = h[place].Fit(functs[place],"0S","",0,lastDate+1.5)
        functs[place].ReleaseParameter(3)
        functs[place].SetParLimits(3,0,maxPar3)
        functs_res[place] = h[place].Fit(functs[place],"0S","",0,lastDate+1.5)
        if minPar2 != maxPar2:
            functs[place].ReleaseParameter(2)
            functs[place].SetParLimits(2,minPar2,maxPar2)
        functs_res[place] = h[place].Fit(functs[place],"0S","",0,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("errErf"+h[place].GetName())))
        functs_err[place].Reset()
        ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionErf_")
        functs[place].SetName(name+"_centralValue") 
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
        functs_err[place].SetName(name+"_errorBand")
    return functs, functs_res, functs_err

from math import log

def fitExpGauss(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ", maxPar3=maxPar3):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("function"+place,"gaus + exp(+x/[4]*0-[3])",firstDate,predictionDate))
        functs[place].SetParameters(h[place].GetMaximum(), lastDate, fixSigma*10, 10, 1000)

##### Fit Exp then Gaus
        functs[place].FixParameter(3, functs[place].GetParameter(3))
        functs[place].FixParameter(4, functs[place].GetParameter(4))
#        functs[place].SetParameter(3, h[place].GetXaxis().GetXmin())
#        functs[place].SetParameter(4, h[place].GetMaximum())
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5 + (lastDate - firstDate)/2, lastDate+1.5 )

#        functs[place].FixParameter(0, functs[place].GetParameter(0))
#        functs[place].FixParameter(1, functs[place].GetParameter(1))
#        functs[place].FixParameter(2, functs[place].GetParameter(2))

        functs[place].ReleaseParameter(3)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
#        functs[place].ReleaseParameter(4)
 #       functs[place].ReleaseParameter(0)
 #       functs[place].ReleaseParameter(1)
  #      functs[place].ReleaseParameter(2)
        
#        functs[place].SetParameter(0, 0.01*h[place].GetMaximum())
#        functs[place].SetParameter(1, h[place].GetXaxis().GetXmax())
#        functs[place].SetParameter(2, fixSigma*10)
#        functs[place].SetParameter(4, functs[place].GetParameter(4)*10)

#        functs[place].SetParLimits(3,0,maxPar3)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
#        functs[place].ReleaseParameter(4)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)

#        if minPar2 != maxPar2:
#            functs[place].ReleaseParameter(2)
#            functs[place].SetParLimits(2,minPar2,maxPar2)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionGaus_")
        functs[place].SetName(name+"_centralValue") 
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
        functs_err[place].SetName(name+"_errorBand")
    return functs, functs_res, functs_err

def fitTwoGaussDiff(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ", maxPar3=maxPar3):
    functs = {}
    functs_res = {}
    functs_err = {}
    fixSigma=20
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("function"+place,"gaus(0) + exp(+x/[4]*0-[3]) + gaus(5)",firstDate,predictionDate))
        functs[place].SetParLimits(0, 0, h[place].GetMaximum()*2)
        functs[place].SetParameters(h[place].GetMaximum(), h[place].GetMean(), fixSigma, 1, 1000, 0, 0, 0)

##### Fit Exp then Gaus
#        functs[place].FixParameter(0, functs[place].GetParameter(0))
#        functs[place].FixParameter(1, functs[place].GetParameter(1))
#        functs[place].FixParameter(2, functs[place].GetParameter(2))
#        functs[place].FixParameter(3, functs[place].GetParameter(3))
        functs[place].FixParameter(4, functs[place].GetParameter(4))
        functs[place].FixParameter(5, functs[place].GetParameter(5))
        functs[place].FixParameter(6, functs[place].GetParameter(6))
        functs[place].FixParameter(7, functs[place].GetParameter(7))
#        functs[place].SetParameter(3, h[place].GetXaxis().GetXmin())
#        functs[place].SetParameter(4, h[place].GetMaximum())
#        print h[place]
#        print functs[place]
#        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5 + (lastDate - firstDate)/2, lastDate+1.5 )

#        functs[place].FixParameter(0, functs[place].GetParameter(0))
#        functs[place].FixParameter(1, functs[place].GetParameter(1))
#        functs[place].FixParameter(2, functs[place].GetParameter(2))

        functs[place].ReleaseParameter(3)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
#        functs[place].ReleaseParameter(4)
 #       functs[place].ReleaseParameter(0)
 #       functs[place].ReleaseParameter(1)
  #      functs[place].ReleaseParameter(2)
        
#        functs[place].SetParameter(0, 0.01*h[place].GetMaximum())
#        functs[place].SetParameter(1, h[place].GetXaxis().GetXmax())
#        functs[place].SetParameter(2, fixSigma*10)
#        functs[place].SetParameter(4, functs[place].GetParameter(4)*10)

#        functs[place].SetParLimits(3,0,maxPar3)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(5)
        functs[place].ReleaseParameter(6)
        functs[place].ReleaseParameter(7)
        functs[place].SetParLimits(5, -functs[place].GetParameter(0)*2, 0)
        functs[place].SetParameter(5, -functs[place].GetParameter(0)*0.5)
        functs[place].SetParameter(6, functs[place].GetParameter(1)+20)
 #       functs[place].SetParLimits(7, functs[place].GetParameter(2)/3, functs[place].GetParameter(2)*3)
        functs[place].SetParameter(7, functs[place].GetParameter(2))
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)

##        if minPar2 != maxPar2:
##            functs[place].ReleaseParameter(2)
##            functs[place].SetParLimits(2,minPar2,maxPar2)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
#        functs[place].SetParLimits(7, functs[place].GetParameter(2)/3, functs[place].GetParameter(2)*3)
#        functs[place].SetParameter(7, functs[place].GetParameter(2))
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionGaus_")
        functs[place].SetName(name+"_centralValue") 
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
        functs_err[place].SetName(name+"_errorBand")
    return functs, functs_res, functs_err

def fitGauss(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ", maxPar3=maxPar3):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("function"+place,"gaus + [3]",firstDate,predictionDate))
        functs[place].SetParameters(h[place].GetBinContent(h[place].GetMaximumBin()), h[place].GetMean(), fixSigma)
        functs[place].FixParameter(2, fixSigma)
        functs[place].FixParameter(3, 1)
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(3)
        functs[place].SetParLimits(3,0,maxPar3)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        if minPar2 != maxPar2:
            functs[place].ReleaseParameter(2)
            functs[place].SetParLimits(2,minPar2,maxPar2)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionGaus_")
        functs[place].SetName(name+"_centralValue") 
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
        functs_err[place].SetName(name+"_errorBand")
    return functs, functs_res, functs_err


def fitGaussAsymmetric(h, places, firstDate, lastDate, predictionDate, fitOption="0SE", maxPar3=maxPar3):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit fitGaussAsymmetric %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("function"+place,"[0]*exp(-0.5*( (x<=[5])*(x-[1])/[2] + [4]/[2]*(x>[5])*(x-[1])/[4] )**2) + [3]",firstDate,predictionDate))
#        functs[place] = copy.copy(ROOT.TF1("function"+place,"[0]*exp(-0.5*( (x<=[1])*(x-[1])/[2] + (x>[1])*(x-[1])/[4] )**2) + [3]",firstDate,predictionDate))
        fixSigma = 20
        functs[place].SetParameters(h[place].GetBinContent(h[place].GetMaximumBin()), h[place].GetMean(), fixSigma, 0, fixSigma)
#        functs[place].SetParameters(h[place].GetBinContent(h[place].GetMaximumBin()), h[place].GetMean(), fixSigma, 0, fixSigma)
#        functs[place].FixParameter(5, 100000)
#        functs[place].FixParameter(3, 0)
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].SetParameter(5, functs[place].GetParameter(1))
#        functs[place].FixParameter(5, h[place].GetMean())
        functs[place].FixParameter(4, functs[place].GetParameter(2))
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
#        functs[place].FixParameter(5, h[place].GetMean())
        functs[place].ReleaseParameter(4)
        functs[place].SetParameter(4, functs[place].GetParameter(2))
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(5)
        functs[place].SetParameter(4, functs[place].GetParameter(2))
        functs[place].SetParameter(5, h[place].GetMean())
        functs[place].ReleaseParameter(4)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(3)
        functs[place].ReleaseParameter(4)
        functs[place].SetParameter(4, functs[place].GetParameter(2))
#        functs[place].FixParameter(5, functs[place].GetParameter(5))
        functs[place].FixParameter(4, functs[place].GetParameter(4))
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionGaus_")
        functs[place].SetName(name+"_centralValue") 
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
        functs_err[place].SetName(name+"_errorBand")
    return functs, functs_res, functs_err

def fitGaussExp(h, places, firstDate, lastDate, predictionDate, fitOption="0SE", maxPar3=maxPar3):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit fitGaussExp %s ###"%place
#        functs[place] = copy.copy(ROOT.TF1("function"+place,"[0]*exp( (x<=[5])*(-0.5*(x-[1])**2/[2]) - (x>[5])*(0.5*([5]-[1])**2/[2])/(1+[4]*[5])*(1+[4]*x) ) + [3]",firstDate,predictionDate))

        functs[place] = copy.copy(ROOT.TF1("function"+place,"[0]*exp( (x<=[5])*(-0.5*(x-[1])**2/[2]) - (x>[5])*(0.5*([5]-[1])**2/[2])/(1+-2/([1] + [5])*[5])*(1+-2/([1] + [5])*x) ) + [3]",firstDate,predictionDate)) ###FUNZIONA! DERIVATA CONTINUA
#()-[2]*((0.5 *[4]* ([0] - [5])**2)/([4] *[5]* [2] + [2]) - [0]/[2]))

        fixSigma = 20
        functs[place].SetParameters(h[place].GetBinContent(h[place].GetMaximumBin()), h[place].GetMean(), fixSigma, 0, fixSigma)
        print("FitInitValue:",h[place].GetBinContent(h[place].GetMaximumBin()), h[place].GetMean(), fixSigma, 0, fixSigma)

        functs[place].FixParameter(5, 100000)
#        functs[place].FixParameter(3, 0)
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].SetParameter(5, functs[place].GetParameter(1))
#        functs[place].FixParameter(5, h[place].GetMean())
#        functs[place].FixParameter(4, 0)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
#        functs[place].FixParameter(5, h[place].GetMean())
#        functs[place].ReleaseParameter(4)
        functs[place].SetParameter(4, 0)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(5)
        functs[place].SetParameter(5, h[place].GetMean())
        functs[place].ReleaseParameter(4)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(3)
        functs[place].ReleaseParameter(4)
#        functs[place].FixParameter(5, functs[place].GetParameter(5))

#        functs[place].FixParameter(0, h[place].GetBinContent(h[place].GetMaximumBin()))
#        functs[place].FixParameter(1, h[place].GetMean())
#        functs[place].FixParameter(2, fixSigma)
#        functs[place].FixParameter(3, 0)
#        functs[place].FixParameter(4, fixSigma)
        
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionGaus_")
        functs[place].SetName(name+"_centralValue") 
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
        functs_err[place].SetName(name+"_errorBand")
    return functs, functs_res, functs_err

def fitTwoExp(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ", maxPar3=maxPar3):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("function"+place,"exp((x-[0])/[1]) + exp(-(x-[2])/[3])",firstDate,predictionDate))
        functs[place].SetParameters(h[place].GetMean(), h[place].GetMean(), h[place].GetMean(), h[place].GetMean())
#        functs[place].FixParameter(2, 10000)
 #       functs[place].FixParameter(3, 1)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
  #      functs[place].FixParameter(2, functs[place].GetParameter(0))
   #     functs[place].FixParameter(3, functs[place].GetParameter(1))
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
    #    functs[place].ReleaseParameter(2)
     #   functs[place].ReleaseParameter(3)
#        if minPar2 != maxPar2:
#            functs[place].ReleaseParameter(2)
#            functs[place].SetParLimits(2,minPar2,maxPar2)
#            functs[place].ReleaseParameter(4)
#            functs[place].SetParLimits(4,minPar2,maxPar2)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionGaus_")
        functs[place].SetName(name+"_centralValue") 
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
        functs_err[place].SetName(name+"_errorBand")
    return functs, functs_res, functs_err

def fitDecessi(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ"):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("functionDecessi"+place,"exp((x-[1])/[0]) + [2]",firstDate,predictionDate))
        functs[place].SetParameters(5, 10, 0 )
        functs[place].FixParameter(2, 0)
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(2)
        functs[place].SetParLimits(2,0,maxConstExp)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionDecessi_")
        functs[place].SetName(name+"_centralValue") 
        functs_err[place].SetName(name+"_errorBand")
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
    return functs, functs_res, functs_err

def fitMultiExp(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ",maxConstExp=maxConstExp):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("functionExp"+str(place),"exp((x-[1])/[0]) + [2]",firstDate,predictionDate))
        functs[place].SetParameters(5, 10, 0 )
#        functs[place].FixParameter(2, 0)
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(2)
        functs[place].SetParLimits(2,0,maxConstExp)
        functs[place].SetParLimits(0,0,100)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        if ROOT.TVirtualFitter.GetFitter(): ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionExp_")
        functs[place].SetName(name+"_centralValue") 
        functs_err[place].SetName(name+"_errorBand")
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
    return functs, functs_res, functs_err

def fitLinear(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ", maxConstExp=maxConstExp, tail=False):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("functionLinear"+str(place),"[0]+[1]*x+[2]*x*x+[3]*x*x*x+[4]*x*x*x*x+[5]*x*x*x*x*x+[6]*x*x*x*x*x*x",firstDate,predictionDate))
        functs[place].SetParameters(h[place].GetBinContent(2), 0, 0)
        functs[place].FixParameter(1, 0)
        functs[place].FixParameter(2, 0)
        functs[place].FixParameter(3, 0)
        functs[place].FixParameter(4, 0)
        functs[place].FixParameter(5, 0)
        functs[place].FixParameter(6, 0)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(1)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(2)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(3)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(4)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(5)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(6)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        if ROOT.TVirtualFitter.GetFitter(): ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionLinear_")
        functs[place].SetName(name+"_centralValue") 
        functs_err[place].SetName(name+"_errorBand")
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
    return functs, functs_res, functs_err

def fitExp(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ", maxConstExp=maxConstExp, tail=False):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("functionExp"+str(place),"exp((x-[1])*[0]) + [2]",firstDate,predictionDate))
        functs[place].SetParameters(1./5, 10, 0 )
        if tail: functs[place].SetParameters(-1./10, 200, 0 )
#        functs[place].FixParameter(2, 0)
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs[place].ReleaseParameter(2)
        functs[place].SetParLimits(2,0,maxConstExp)
        functs[place].SetParLimits(0,-100,100)
        if tail: functs[place].SetParLimits(0,-100,100)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate-0.5,lastDate+1.5)
        color = colors[places.index(place)]
        functs[place].SetLineColor(color)
        functs_err[place] = copy.copy(h[place].Clone(("err"+h[place].GetName())))
        functs_err[place].Reset()
        if ROOT.TVirtualFitter.GetFitter(): ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(functs_err[place], 0.68)
        functs_err[place].SetStats(ROOT.kFALSE)
        functs_err[place].SetLineColor(color)
        functs_err[place].SetFillColor(color)
        name = h[place].GetName().replace("histo_","functionExp_")
        functs[place].SetName(name+"_centralValue") 
        functs_err[place].SetName(name+"_errorBand")
        if functs_res[place].Get(): functs_res[place].SetName(name+"_fitResult")
    return functs, functs_res, functs_err


def extendDates(dates, nextend):
    offset = 365
    ndates = len(dates)
    for i in range(1,nextend):
    #    dates.append(dates[ndates-1]+"+"+str(i))
        if i<=31:
            newDate = "3/%d/20"%i
        elif i>31 and i<=61:
            newDate = "4/%d/20"%(i-31)
        elif i>61 and i<=92:
            newDate = "5/%d/20"%(i-61)
        elif i>92 and i<=122:
            newDate = "6/%d/20"%(i-92)
        elif i>122 and i<=153:
            newDate = "7/%d/20"%(i-122)
        elif i>153 and i<=184:
            newDate = "8/%d/20"%(i-153)
        elif i>184 and i<=214:
            newDate = "9/%d/20"%(i-184)
        elif i>214 and i<=245:
            newDate = "10/%d/20"%(i-214)
        elif i>245 and i<=275:
            newDate = "11/%d/20"%(i-245)
        elif i>275 and i<=306:
            newDate = "12/%d/20"%(i-275)
        elif i>306 and i<=337:
            newDate = "1/%d/21"%(i-306)
        elif i>337 and i<=365:
            newDate = "2/%d/21"%(i-337)
        elif i>0+offset and i<=31+offset:
            newDate = "3/%d/21"%(i-offset)
        elif i>31+offset and i<=61+offset:
            newDate = "4/%d/21"%(i-31-offset)
        elif i>61+offset and i<=92+offset:
            newDate = "5/%d/21"%(i-61-offset)
        elif i>92+offset and i<=122+offset:
            newDate = "6/%d/21"%(i-92-offset)
        elif i>122+offset and i<=153+offset:
            newDate = "7/%d/21"%(i-122-offset)
        elif i>153+offset and i<=184+offset:
            newDate = "8/%d/21"%(i-153-offset)
        elif i>184+offset and i<=214+offset:
            newDate = "9/%d/21"%(i-184-offset)
        elif i>214+offset and i<=245+offset:
            newDate = "10/%d/21"%(i-214-offset)
        elif i>245+offset and i<=275+offset:
            newDate = "11/%d/21"%(i-245-offset)
        elif i>275+offset and i<=306+offset:
            newDate = "12/%d/21"%(i-275-offset)
        elif i>306+offset and i<=337+offset:
            newDate = "1/%d/22"%(i-306-offset)
        elif i>337+offset and i<=365+offset:
            newDate = "2/%d/22"%(i-337-offset)
        elif i>365+offset and i<=396+offset:
            newDate = "3/%d/22"%i
        if not newDate in dates: dates.append(newDate)
    return dates

def saveCSV(predictions, places, dates, fn_predictions, fn_predictions_error):
    f_predictions_error = open(fn_predictions_error,"w")
    f_predictions       = open(fn_predictions,"w")
    f_predictions.write( "place" )
    f_predictions_error.write( "place" )
    for date in dates:
        if date in predictions[predictions.keys()[0]]:
            f_predictions.write( ",%s"%date )
            f_predictions_error.write( ",%s"%date )
    f_predictions.write( "\n" )
    f_predictions_error.write( "\n" )
    for place in places:
        f_predictions.write( place )
        f_predictions_error.write( place )
        for date in dates:
            if date in predictions[place]:
                (pred, pred_err) = predictions[place][date]
                f_predictions.write( ",%.1f +/- %.1f"%(pred,pred_err) )
                f_predictions_error.write( ",%.1f"%pred_err )
        f_predictions.write( "\n" )
        f_predictions_error.write( "\n" )
    f_predictions_error.close()
    f_predictions.close()
                

#def savePlot(histoConfirmed, histoRecovered, histoDeaths, histoPrediction, histoTerapiaIntensiva, histoRicoverati, histoTamponi, function, function_res, function_error, functionExp, fName, xpred, canvas):
#    fres = None
#    if function: 
#        fres = function_res.Get()
#    canvas.SetLogy(useLog)
#    canvas.cd()
#    canvas.SetTitle("")
#    leg = ROOT.TLegend(0.9,0.1,1.0,0.9)
#    maxim = 0
#    for item in [histoConfirmed, histoRecovered, histoDeaths, histoPrediction, histoTerapiaIntensiva, histoRicoverati, histoTamponi, function]:
#        if item: 
#            maxim = max(maxim, item.GetMaximum())
#            if item == histoConfirmed: leg.AddEntry(item, "Confirmed", "lep")
#            if item == histoRecovered: leg.AddEntry(item, "Recovered", "lep")
#            if item == histoDeaths: leg.AddEntry(item, "Deaths", "lep")
#            if item == histoPrediction: leg.AddEntry(item, "Prediction", "lep")
#            if item == histoTerapiaIntensiva: leg.AddEntry(item, "Terapia Intensiva", "lep")
#            if item == histoRicoverati: leg.AddEntry(item, "Ricoverati", "lep")
#            if item == histoTamponi: leg.AddEntry(item, "Tamponi", "lep")
#            if item == function and fres: leg.AddEntry(item, "#splitline{Gaussian fit}{#splitline{#mu=%.1f #pm %.1f}{ #sigma=%.1f #pm %.1f}} "%(fres.GetParams()[1],fres.GetErrors()[1],fres.GetParams()[2],fres.GetErrors()[2]), "lep")
#    if function: maxim = min(maxim, histoConfirmed.GetMaximum()*100)
#    if maxim>0 and useLog:
#        maxim = 10**int(ROOT.TMath.Log10(maxim)+1)
#    histoRecovered.SetLineStyle(1)
#    histoDeaths.SetLineStyle(1)
#    histoConfirmed.SetLineColor(ROOT.kBlue)
##    histoConfirmed.SetFillColor(ROOT.kBlue)
#    histoRecovered.SetLineColor(ROOT.kRed)
##    histoRecovered.SetFillColor(ROOT.kRed)
#    histoDeaths.SetLineColor(ROOT.kBlack)
##    histoDeaths.SetFillColor(ROOT.kBlack)
#    histoConfirmed.SetMinimum(1)
#    histoConfirmed.SetMaximum(maxim)
#    histoConfirmed.Draw("HIST,PL,")
#    if histoPrediction: 
#        histoPrediction.SetLineColor(ROOT.kMagenta+2)
##        histoPrediction.SetFillColor(ROOT.kMagenta+2)
#        histoPrediction.SetLineStyle(1)
#        histoPrediction.Draw("HIST,PL,same")
#    if histoTerapiaIntensiva: 
#        histoTerapiaIntensiva.SetLineColor(ROOT.kGreen+2)
##        histoTerapiaIntensiva.SetFillColor(ROOT.kGreen+2)
#        histoTerapiaIntensiva.SetLineStyle(1)
#        histoTerapiaIntensiva.Draw("HIST,PL,same")
#    if histoRicoverati: 
#        histoRicoverati.SetLineColor(ROOT.kGreen+1)
##        histoRicoverati.SetFillColor(ROOT.kGreen+1)
#        histoRicoverati.SetLineStyle(1)
#        histoRicoverati.Draw("HIST,PL,same")
#    if histoTamponi: 
#        histoTamponi.SetLineColor(ROOT.kGreen+3)
##        histoTamponi.SetFillColor(ROOT.kGreen+3)
#        histoTamponi.SetLineStyle(1)
#        histoTamponi.Draw("HIST,PL,same")
#    line = ROOT.TLine(xpred+0.5,0,xpred+0.5,histoConfirmed.GetMaximum())
#    line.SetLineStyle(2)
#    line.SetLineWidth(3)
#    if function:
#        function.SetMinimum(1)
#        function.SetLineColor(ROOT.kBlue)
##        ci = copy.copy(histoConfirmed.Clone("ci"+histoConfirmed.GetName()))
##        function_res.Get().GetConfidenceIntervals(ci, 0.68)
##        ci.SetStats(kFALSE);
##        ci.SetFillColor(2);
##        ci.Draw("HIST,PL, same");
#        function.Draw("same")
#    if function_error:
#        function_error.SetFillColor(ROOT.kBlue)
#        function_error.SetFillStyle(3144)
#        function_error.SetLineColor(ROOT.kBlue)
#        function_error.Draw("e3same")
#    if functionExp and abs(functionExp.GetParameter(0)*ROOT.TMath.Log(2))<15: # and (not fres or fres.GetParams()[1] > 40)
#        functionExp.SetFillColor(ROOT.kMagenta)
#        functionExp.SetLineWidth(3)
#        functionExp.SetLineColor(ROOT.kMagenta)
#        leg.AddEntry(functionExp, "#splitline{Exponential fit}{#tau_{2} = %.1f days}"%(functionExp.GetParameter(0)*ROOT.TMath.Log(2)), "lep")
#        functionExp.SetRange(histoConfirmed.GetXaxis().GetXmin(),histoConfirmed.GetXaxis().GetXmax())
#        functionExp.Draw("same")
#    histoRecovered.Draw("HIST,PL,same")
#    histoDeaths.Draw("HIST,PL,same")
#    line.Draw()
#    leg.Draw("same")
#    canvas.SaveAs(fName)
#    print fName


def getScaled(histo, scale, fromZero=False):
    print(histo,scale)
    if type(histo)==ROOT.TH1F:
        histo = histo.Clone(histo.GetName()+"_scaled")
        histo.Scale(scale)
        if scale>1: histo.label_sf = "(x%d)"%scale
        elif scale<1: histo.label_sf = "(x%.2f)"%scale
        if fromZero:
            val = histo.GetBinContent(1)
            for i in range(histo.GetNbinsX()+2):
                print(i, histo.GetBinContent(i))
                if histo.GetBinContent(i)!=0:
                    histo.SetBinContent(i, histo.GetBinContent(i) - val)
                    print(histo.GetBinContent(i))

    return histo

def savePlotNew(histos, functions, fName, xpred, dates, canvas, ISTAT=False, log=useLog):
    useLog=log
#    print(type(dates))
#    print(dates)
    Nov1 = dates.index("11/1/20")
    histos = [h for h in histos if h]
    functions = [f for f in functions if f]
#    histoConfirmed, histoRecovered, histoDeaths, histoPrediction, histoTerapiaIntensiva, histoRicoverati, histoTamponi
#   function, function_res, function_error, functionExp
    canvas.SetLogy(useLog)
    canvas.cd()
    canvas.SetGridx(1)
    canvas.SetGridy(1)
    canvas.SetTitle("")
    leg = ROOT.TLegend(0.9,0.1,1.0,0.9)
    maxim = 0
    minim = 1E9
    for histo in histos:
        if not "prediction" in histo.GetName(): ## exclude prediction plot to define max/min
            maxim = max(maxim, histo.GetMaximum())*1.01
            minim = min(minim, histo.GetMinimum())-0.01*abs(min(minim, histo.GetMinimum()))
        maxim = min(maxim,1E7)
        if not "prediction" in histo.GetName():
            label = getLabel(histo.GetName())
            if hasattr(histo,"label_sf"): label="#splitline{%s}{%s}"%(label,histo.label_sf)
            leg.AddEntry(histo, label, "lep")
        if not "ISTAT" in histo.GetName(): histo.SetLineColor(getColor(histo.GetName()))
#        histo.SetFillColor(getColor(histo.GetName()))
        histo.SetLineStyle(1)
    
    if useLog: minim=max(1,minim)
    
    for function in functions:
        function.SetMinimum(minim)
        if not "ISTAT" in histo.GetName(): function.SetLineColor(getColor(function.GetName()))
#        function.SetFillStyle(0)
        function.SetFillColor(function.GetLineColor())
        if not "ISTAT" in histo.GetName():
            if "Gaus" in function.GetName():
                if function.fitResult.Get(): 
#                    leg.AddEntry(function, "Exp + Gauss fit", "lp")
                    leg.AddEntry(function, "#splitline{Gaussian fit}{#splitline{#mu=%.1f #pm %.1f Nov}{ #sigma=%.1f #pm %.1f}} "%(function.fitResult.GetParams()[1]-Nov1,function.fitResult.GetErrors()[1],function.fitResult.GetParams()[2],function.fitResult.GetErrors()[2]), "lep")
#                    leg.AddEntry(function, "#splitline{Gaussian fit}{#splitline{max %d}{ %.1f Nov}} "%( int(function.GetMaximum()), function.GetMaximumX() - Nov1), "lep")
                else:
                    leg.AddEntry(function, "Gaussian fit", "lp")
            if "Exp" in function.GetName():
                leg.AddEntry(function, "#splitline{Exponential fit}{#tau_{2} = %.1f days}"%((1./function.GetParameter(0))*ROOT.TMath.Log(2)), "lep")
        else:
            leg.AddEntry(function, function.label, "lp")
            
    if maxim>0 and useLog: maxim = 10**int(ROOT.TMath.Log10(maxim)+1)
    if maxim>0 and not useLog: maxim = (1.+int(maxim*100      /10**int(ROOT.TMath.Log10(maxim*100))     ))*10**int(ROOT.TMath.Log10(maxim*100))/100
    if minim<0 and not useLog: minim = -int(abs(minim)/10**int(ROOT.TMath.Log10(abs(minim)))+2)*10**int(ROOT.TMath.Log10(abs(minim)))
    
    line = ROOT.TLine(xpred+0.5,0,xpred+0.5,maxim)
    line.SetLineStyle(2)
    line.SetLineWidth(3)
    histo
    histos[0].SetMaximum(maxim)
    histos[0].SetMinimum(minim)
    histos[0].Draw("")
    for i, histo in enumerate(reversed(histos+[histos[0]])):
        if i == 0: same = ""
        else: same = "same"
        if "prediction" in histo.GetName(): 
            histoErr = histo.Clone(histo.GetName()+"err")
            histoErr.SetFillColor(histo.GetLineColor())
            histoErr.SetFillStyle(3144)
            histoErr.Draw("e3"+same)
            histo.SetMarkerStyle(0)
        else:
            histo.SetMarkerStyle(20)
        histo.SetMarkerColor(histo.GetLineColor())
        if not "ISTAT" in histo.GetName():
            histo.Draw("HIST,PL,"+same)
        else:
            histo.Draw("ERR,"+same)
        
    
    for function in functions:
        function.SetLineWidth(3)
        if "Exp" in function.GetName(): function.SetRange(histos[0].GetXaxis().GetXmin(),histos[0].GetXaxis().GetXmax())
        function.Draw("same")
        if function.error : 
            function.error.SetFillColor(function.GetLineColor())
            function.error.SetFillStyle(3144)
            function.error.Draw("e3same")
    line.Draw()
    leg.Draw("same")
    canvas.SetGridx(1)
    canvas.SetGridy(1)
    canvas.SaveAs(fName)
#    print fName
#    for h in histos:
#        print h.GetName()
#    for f in functions:
#        print f.GetName()

def getPrediction(places, dates, firstDate, finalDate, histo, functNewCases, functNewCases_res, realData=None):
    predictions = {}
    for place in places:
        print "### Prediction %s ###"%(place)
        predictions[place] = {}
        for predictionDate in range(firstDate, finalDate):
            val = histo[place].GetBinContent(histo[place].FindBin(firstDate))
            integr = functNewCases[place].Integral(firstDate + 0.5, predictionDate + 0.5)
            interr = functNewCases[place].IntegralError(firstDate + 0.5, predictionDate + 0.5, functNewCases_res[place].GetParams(), functNewCases_res[place].GetCovarianceMatrix().GetMatrixArray()) if functNewCases_res[place].Get() else 1E9
            if integr>0:
                if interr>1: 
                    interr = (interr**2 + integr)**0.5 # Err = (Syst^2 + Stat(ie sqrtN)^2)^0.5
                else:
                    interr = (interr**2 + integr)**0.5 # Err = (Syst^2 + Stat(ie sqrtN)^2)^0.5
                    print "WARNING interr=%f"%interr
            else:
                interr=1
            print "Expected fit new cases (%s): %.1f +/- %.1f"%(dates[predictionDate],  val + integr, interr)
            predictions[place][dates[predictionDate]] = (val + integr, interr) if float(interr)/(1.001+val+integr)<0.5 else (0,0)
#            predictions[place][dates[predictionDate]] = (val + integr, interr)
            try:
                print "Real Confirmed (%s): %d"%(dates[predictionDate], realData[place][dates[predictionDate]])
                print "Error (sigma) : %.1f"%( (realData[place][dates[predictionDate]] - (val + integr)) / interr)
            except:
                pass
    return predictions

def getPredictionErf(places, dates, firstDate, finalDate, histo, functErfs, functErfs_res, realData=None):
    predictions = {}
    for place in places:
        print "### Prediction (from Erf)%s ###"%(place)
        predictions[place] = {}
        valErf0 = functErfs[place].Eval( firstDate  )
        for predictionDate in range(firstDate, finalDate):
            valErf = functErfs[place].Eval( predictionDate  )
            err = array.array('d',[0])
            x   = array.array('d',[predictionDate ])
            functErfs_res[place].GetConfidenceIntervals(2, 1, 1, x, err, 0.683)
            err = (err[0]**2 + abs(valErf-valErf0))**0.5 ## add statistical error
            print "Expected fit erf (%s): %.1f +/- %.1f"%(dates[predictionDate], valErf, err)
            predictions[place][dates[predictionDate]] = (valErf, err)
            try:
                print "Real Confirmed (%s): %d"%(dates[predictionDate], realData[place][dates[predictionDate]])
                print "Error (sigma) : %.1f"%( (realData[place][dates[predictionDate]] - (val + integr)) / interr)
            except:
                pass
    return predictions

def getPredictionErf(places, dates, firstDate, finalDate, histo, functErfs, functErfs_res, realData=None):
    predictions = {}
    for place in places:
        print "### Prediction (from Erf)%s ###"%(place)
        predictions[place] = {}
        valErf0 = functErfs[place].Eval( firstDate  )
        for predictionDate in range(firstDate, finalDate):
            valErf = functErfs[place].Eval( predictionDate  )
            err = array.array('d',[0])
            x   = array.array('d',[predictionDate ])
            functErfs_res[place].GetConfidenceIntervals(2, 1, 1, x, err, 0.683)
            err = (err[0]**2 + abs(valErf-valErf0))**0.5 ## add statistical error
            print "Expected fit erf (%s): %.1f +/- %.1f"%(dates[predictionDate], valErf, err)
            predictions[place][dates[predictionDate]] = (valErf, err)
            try:
                print "Real Confirmed (%s): %d"%(dates[predictionDate], realData[place][dates[predictionDate]])
                print "Error (sigma) : %.1f"%( (realData[place][dates[predictionDate]] - (val + integr)) / interr)
            except:
                pass
    return predictions

def applyScaleFactors(histo, errorType='3sqrtN', threshold=0):
    print ("Getting scale factors: "+histo.GetName())
    sfs = [1.]*7
    count = [0]*7
    tot = 0.001
    countTot = 0.001
    offset=0
    for i in range(5-offset,len(histo)+1-offset):
        sum7binsBef = sum(histo.GetBinContent(i-j) for j in range(offset,7+offset))
#        sum7binsBefCorr = sum(histo.GetBinContent(i-j)>0 for j in range(offset,7+offset))/7
#        if sum7binsBefCorr>0:
#            sum7binsBef = sum7binsBef * 1./sum7binsBefCorr
        binVal = histo.GetBinContent(i)
        if binVal>threshold and sum7binsBef>threshold:
            print(i,sum7binsBef,binVal,sum7binsBef/binVal/7)
            val = sum7binsBef/binVal
            sfs[i%7] += val
            tot += val
            count[i%7] += 1
            countTot += 1
    
    sfAverage = 0
    for i in range(7):
        sfs[i] = sfs[i]/count[i] * countTot/tot if count[i]>0 else 1.
        sfAverage += sfs[i]
    sfAverage = sfAverage/7
    for i in range(7):
        sfs[i] = sfs[i] / sfAverage if sfAverage>0 else sfs[i]
        print ("sfs[%d] = %f"%(i,sfs[i]))
    print ("Applying scale factors: ")
    
    for i in range(1,len(histo)+1):
        if histo.GetBinContent(i)>0:
            print("XXX")
            print(histo.GetBinContent(i))
            print(histo.GetBinContent(i) * sfs[i%7])
            histo.SetBinContent(i, histo.GetBinContent(i)*sfs[i%7])
            print(histo.GetBinContent(i))

    ## Update Error
    oldValue = 0
    for i in range(1,len(histo)):
        value = histo.GetBinContent(i)
        error = histo.GetBinError(i)
        valueM1 = histo.GetBinContent(i-1) if i>=1 else value
        valueP1 = histo.GetBinContent(i+1) if i<=len(histo)-1 else value
        valueM1 = max(valueM1,0)
        valueP1 = max(valueP1,0)
        average = ((valueM1+valueP1)/2)
        if errorType=='3sqrtN':
            error = 0.05*abs(value)+ 2*abs(value)**0.5 + 9
#            error = abs(value)**0.5 + 9
        elif errorType=='sqrtN':
            error = (value)**0.5   if (value>=9 and value>=0.25*average) else max(3,abs(value-average)*2)
        elif errorType=='default':
            error = 9.+(value)**0.5+0*0.25*(value) if value>=9 else 12.+abs(value-9.)                    ## error 10 + sqrt(N) + 0*25% N
            if i>=1: error = max(error, abs(value-valueM1))
            if i<=lastDate: error = max(error, abs(value-valueP1))
#        histo.SetBinContent(i, value)
        error = max( error, abs(oldValue - value) )
        oldValue = value
        if histo.GetBinContent(i)!=0:
            histo.SetBinError(i, error)


def positiveHisto(histo):
    histo.SetMinimum(0.1)
#    return
    for i in range(0,len(histo)+2):
        val = histo.GetBinContent(i)
        if val<0.1 and val!=0:
#            err = histo.GetBinContent(i)
            histo.SetBinContent(i, 0.1)
#            histo.SetBinError(i, max(err,1))



