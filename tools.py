import ROOT
import csv
import copy
import array
import datetime
import pickle

rnd = ROOT.TRandom3()

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
ROOT.kGreen+1,

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

colorMap = {
    "positives":  ROOT.kYellow+2,
    "histo_confirmes":  ROOT.kBlue,
    "recoveres":  ROOT.kRed,
    "deaths":     ROOT.kBlack,
    "newConfirmes":   ROOT.kBlue,
    "newRecoveres":   ROOT.kRed,
    "newDeaths":      ROOT.kBlack,
    "prediction":      ROOT.kMagenta+2,
    "functionExp":      ROOT.kMagenta,
    "intensiva":      ROOT.kGreen+2,
    "ricoverati":      ROOT.kOrange+1,
    "test":      ROOT.kGray+2,
    "newIntensiva":      ROOT.kGreen+2,
    "newRicoverati":      ROOT.kOrange+1,
    "newTest":      ROOT.kGray+2,
    "Decessi":      ROOT.kBlack,
    "decessi":      ROOT.kBlack,
    "ISTAT":        ROOT.kMagenta+1,
    "storico":      ROOT.kBlack,
}

labelMap = {
    "positives":  "positives",
    "confirmes":  "confirmed",
    "recoveres":  "recovered",
    "deaths":     "deaths",
    "newConfirmes":   "new confirmed",
    "newRecoveres":   "new recovered",
    "newDeaths":      "new deaths",
    "prediction":      "prediction",
    "intensiva":      "Terapia Intensiva",
    "ricoverati":      "Ricoverati",
    "test":      "Tamponi",
    "newIntensiva":      "Terapia Intensiva",
    "newRicoverati":      "Ricoverati",
    "newTest":      "Tamponi",
    "Decessi":      "Decessi",
    "decessi":      "Decessi",
    "ISTAT":        "#splitline{Decessi totali}{(eccesso ISTAT)}",
    "storico":      "#splitline{Media 2015-19}{(riscalata)}",
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
    for k in dictionary:
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
    return out

def getLabel(name):
    out = getGeneric (name, labelMap)
    assert(type(out)==str)
    return out


def getData(row, i):
    try:
        value = int(row[i+4])
    except:
        print "WARNING: problems with '%s' '%s' at %i. The numeber is '%s'. I wil use 0."%(row[0],row[1],i+4,row[i+4])
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
        dataISTAT, dates = fillDataISTAT(fileName, zerosuppression=100)
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
            print "XXX",row
            if line_count ==0:
                labels = row[:]
            else:
                date = row[labels.index("data")].split(" ")[0].split("T")[0].replace("2020-0","").replace("-","/").replace("/0","/")+"/20"
                if not date in dates: dates.append(date)
                regione = row[labels.index(column_regione)]
                if regione == "In fase di definizione/aggiornamento": continue
                if regione == "Friuli V. G. ": regione = "Friuli Venezia Giulia"
                regione = regione.replace(" ","")
                regione = regione.replace("-","")
                regione = regione.replace("P.A.","")
                if not regione in data: data[regione] = {}
                if date in data[regione]: print "WARNING: OVERWRITING DATA: %s %s"%(regione, date)
                data[regione][date] = {}
                for i,label in enumerate(labels):
                    data[regione][date][label] = row[i]
                    print regione, date, label, row[i]
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

def getColumn(dataRegioni_, label):
    data = {}
    for regione in dataRegioni_:
        for place in regions("", regione, ["Italia"]):
            if not place in data: data[place] = {}
            for date in dataRegioni_[regione]:
                if not date in data[place]: data[place][date] = 0
                data[place][date] += int(dataRegioni_[regione][date][label])
    return data

def newCases(cases, dates):
    newCases = {}
    for place in cases:
        newCases[place] = {}
        newCases[place][dates[0]] = 0
        for i in range(1, len(cases[place])):
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

def makeHistos(prefix, dataUnsmeared, dates, places, firstDate, lastDate, predictionDate, threshold=-1, cutTails=False, errorType=None, lineWidth=3, daysSmearing=1):
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
        for i in reversed(range(firstDate, predictionDate)):
            binx = histos[place].FindBin(i)
            date = dates[i]
#            print(binx,date)
            if type(date)==str and i%2==0: histos[place].GetXaxis().SetBinLabel(  binx, date[:-3] )
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
                    if errorType=='cumulative':
                        error = 1.+(data[place][dates[lastDate]] - data[place][date])**0.5    if (data[place][dates[lastDate]] - data[place][date]) >=0 else 0
                    elif errorType=='sqrtN':
                        error = (data[place][date])**0.5
                    else:
                        error = 10.+(data[place][date])**0.5+0*0.25*(data[place][date]) if data[place][date]>=0 else abs(data[place][date])*2                    ## error 10 + sqrt(N) + 0*25% N
                        if i>=1: error = max(error, abs(data[place][date]-data[place][dates[i-1]]))
                        if i<=lastDate: error = max(error, abs(data[place][date]-data[place][dates[i+1]]))
                if value>threshold:
                    if not stop:
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
        functs_res[place] = h[place].Fit(functs[place],"0S","",0,lastDate+0.5)
        functs[place].ReleaseParameter(3)
        functs[place].SetParLimits(3,0,maxPar3)
        functs_res[place] = h[place].Fit(functs[place],"0S","",0,lastDate+0.5)
        if minPar2 != maxPar2:
            functs[place].ReleaseParameter(2)
            functs[place].SetParLimits(2,minPar2,maxPar2)
        functs_res[place] = h[place].Fit(functs[place],"0S","",0,lastDate+0.5)
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

def fitGauss(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ", maxPar3=maxPar3):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("function"+place,"gaus + [3]",firstDate,predictionDate))
        functs[place].SetParameters(h[place].Integral(), h[place].GetMean(), fixSigma)
        functs[place].FixParameter(2, fixSigma)
        functs[place].FixParameter(3, 1)
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs[place].ReleaseParameter(3)
        functs[place].SetParLimits(3,0,maxPar3)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        if minPar2 != maxPar2:
            functs[place].ReleaseParameter(2)
            functs[place].SetParLimits(2,minPar2,maxPar2)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
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


def fitGaussAsymmetric(h, places, firstDate, lastDate, predictionDate, fitOption="0SEQ", maxPar3=maxPar3):
    functs = {}
    functs_res = {}
    functs_err = {}
    for place in places:
        print "### Fit %s ###"%place
        functs[place] = copy.copy(ROOT.TF1("function"+place,"[0]*exp(-0.5*( (x<=[1])*(x-[1])/[2] + (x>[1])*(x-[1])/[4] )**2) + [3]",firstDate,predictionDate))
        functs[place].SetParameters(h[place].Integral(), h[place].GetMean(), fixSigma, 0, fixSigma)
        functs[place].FixParameter(2, fixSigma)
        functs[place].FixParameter(4, fixSigma*2)
        functs[place].FixParameter(3, 1)
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs[place].ReleaseParameter(3)
        functs[place].SetParLimits(3,0,maxPar3)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        if minPar2 != maxPar2:
            functs[place].ReleaseParameter(2)
            functs[place].SetParLimits(2,minPar2,maxPar2)
            functs[place].ReleaseParameter(4)
            functs[place].SetParLimits(4,minPar2,maxPar2)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
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
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs[place].ReleaseParameter(2)
        functs[place].SetParLimits(2,0,maxConstExp)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
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
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs[place].ReleaseParameter(2)
        functs[place].SetParLimits(2,0,maxConstExp)
        functs[place].SetParLimits(0,0,100)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
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
        functs[place] = copy.copy(ROOT.TF1("functionLinear"+str(place),"[0]+[1]*x+[2]*x*x",firstDate,predictionDate))
        functs[place].SetParameters(h[place].GetBinContent(2), 0, 0)
        functs[place].FixParameter(1, 0)
        functs[place].FixParameter(2, 0)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs[place].ReleaseParameter(1)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs[place].ReleaseParameter(2)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
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
        functs[place] = copy.copy(ROOT.TF1("functionExp"+str(place),"exp((x-[1])/[0]) + [2]",firstDate,predictionDate))
        functs[place].SetParameters(5, 10, 0 )
        if tail: functs[place].SetParameters(-10, 200, 0 )
#        functs[place].FixParameter(2, 0)
#        print h[place]
#        print functs[place]
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs[place].ReleaseParameter(2)
        functs[place].SetParLimits(2,0,maxConstExp)
        functs[place].SetParLimits(0,0,100)
        if tail: functs[place].SetParLimits(0,-100,0)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
        functs_res[place] = h[place].Fit(functs[place], fitOption,"",firstDate,lastDate)
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
#        histoRicoverati.SetLineColor(ROOT.kOrange+1)
##        histoRicoverati.SetFillColor(ROOT.kOrange+1)
#        histoRicoverati.SetLineStyle(1)
#        histoRicoverati.Draw("HIST,PL,same")
#    if histoTamponi: 
#        histoTamponi.SetLineColor(ROOT.kGray+2)
##        histoTamponi.SetFillColor(ROOT.kGray+2)
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


def savePlotNew(histos, functions, fName, xpred, canvas, ISTAT=False):
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
    for histo in histos:
        maxim = max(maxim, histo.GetMaximum())
        leg.AddEntry(histo, getLabel(histo.GetName()), "lep")
        if not ISTAT: histo.SetLineColor(getColor(histo.GetName()))
#        histo.SetFillColor(getColor(histo.GetName()))
        histo.SetLineStyle(1)
    
    for function in functions:
        function.SetMinimum(1)
        if not ISTAT: function.SetLineColor(getColor(function.GetName()))
#        function.SetFillStyle(0)
        function.SetFillColor(function.GetLineColor())
        if not ISTAT:
            if "Gaus" in function.GetName():
                if function.fitResult.Get(): 
                    leg.AddEntry(function, "#splitline{Gaussian fit}{#splitline{#mu=%.1f #pm %.1f}{ #sigma=%.1f #pm %.1f}} "%(function.fitResult.GetParams()[1],function.fitResult.GetErrors()[1],function.fitResult.GetParams()[2],function.fitResult.GetErrors()[2]), "lep")
                else:
                    leg.AddEntry(function, "Gaussian fit", "lep")
            if "Exp" in function.GetName():
                leg.AddEntry(function, "#splitline{Exponential fit}{#tau_{2} = %.1f days}"%(function.GetParameter(0)*ROOT.TMath.Log(2)), "lep")
        else:
            leg.AddEntry(function, function.label, "lep")
            
    if maxim>0 and useLog: maxim = 10**int(ROOT.TMath.Log10(maxim)+1)
    
    line = ROOT.TLine(xpred+0.5,0,xpred+0.5,maxim)
    line.SetLineStyle(2)
    line.SetLineWidth(3)
    
    histos[0].SetMaximum(maxim)
    histos[0].Draw("")
    for i, histo in enumerate(reversed(histos+[histos[0]])):
        if i == 0: same = ""
        else: same = "same"
        if "predictions" in histo.GetName(): 
            histoErr = histo.Clone(histo.GetName()+"err")
            histoErr.SetFillColor(histo.GetLineColor())
            histoErr.SetFillStyle(3144)
            histoErr.Draw("e3"+same)
        histo.SetMarkerStyle(20)
        histo.SetMarkerColor(histo.GetLineColor())
        if not ISTAT:
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
            if interr>1: 
                interr = (interr**2 + integr)**0.5 # Err = (Syst^2 + Stat(ie sqrtN)^2)^0.5
            else:
                interr = (interr**2 + integr)**0.5 # Err = (Syst^2 + Stat(ie sqrtN)^2)^0.5
                print "WARNING interr=%f"%interr
            print "Expected fit new cases (%s): %.1f +/- %.1f"%(dates[predictionDate],  val + integr, interr)
            predictions[place][dates[predictionDate]] = (val + integr, interr) if float(interr)/(1.+val+integr)<0.5 else (0,0)
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
