# -*- coding: utf-8 -*-
#import csv
#import copy
from tools import colors, fillDataISTATpickle, selectComuniDatesAgeGender, newCases, getRatio, makeHistos, fitDecessi, fitErf, fitGauss, fitLinear, fitExp, extendDates, saveCSV, savePlotNew, getPrediction, getPredictionErf, getColumn, makeCompatible
from operator import itemgetter, attrgetter


import ROOT
#ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
#ROOT.gROOT.SetBatch(0)

resX, resY = 1920, 1080

#dataISTAT, dates = fillDataISTATpickle('DatiISTAT/dati-giornalieri-comune/comune_giorno.csv', zerosuppression=100, pickleFileName = "temp_italia.pkl", writePickle = True)
dataISTAT, dates = fillDataISTATpickle('dataISTAT/comuni_giornaliero_30giugno.csv', zerosuppression=100, pickleFileName = "temp_italia_31maggio.pkl", writePickle = True)
dataISTAT = makeCompatible(dataISTAT, firstDateDay=1, firstDateMonth=1)
for i in range(len(dates)):
    dates[i] = dates[i].replace("/0","/")
    if dates[i][0]=="0": dates[i]=dates[i][1:]

dates = extendDates(dates, 200)

decessi     = selectComuniDatesAgeGender(dataISTAT, dates[:], places=None, ages=range(0,30), genders=[0,1])
decessi_old = selectComuniDatesAgeGender(dataISTAT, dates[:], places=None, ages=range(0,30), genders=[2,3])

places = decessi.keys()
#places = ["Italia"]



firstDate = 0
#lastDate = len(dates)-1
lastDate = dates.index("5/1/20")
#lastDate = dates.index("3/11/20")
predictionsDate = dates.index("6/30/20")
#predictionsDate = dates.index("3/8/20")
startDate = lastDate
#lastDate2015 = dates.index("4/30/20")
#lastDate2015 = dates.index("2/28/20")
#lastDate2015 = dates.index("3/1/20")
#lastDate2015 = dates.index("4/29/20")

decessi_h = makeHistos("histo_decessi", decessi,        dates[:], places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='sqrtN', lineWidth=2)
decessi_old_h = makeHistos("histo_storico", decessi_old,dates[:], places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='sqrtN', lineWidth=2)

decessi_excess_only_h = {}
for place in places:
    if decessi_old_h[place].Integral(0, dates.index("2/15/20"))>0: decessi_old_h[place].Scale(decessi_h[place].Integral(0, dates.index("2/15/20"))/decessi_old_h[place].Integral(0, dates.index("2/15/20")))
    feb29_bin = dates.index("3/1/20")
    decessi_old_h[place].SetBinContent(feb29_bin, decessi_old_h[place].GetBinContent(feb29_bin-1))
    decessi_old_h[place].SetBinError(  feb29_bin, decessi_old_h[place].GetBinContent(feb29_bin-1))

fitLinears, fitLinears_res, fitLinears_error              = fitLinear(decessi_old_h,      places, firstDate+1, lastDate-1, predictionsDate, maxConstExp=10000, tail=True, fitOption="SEQ0L")

for place in places:
    decessi_excess_only_h[place] = decessi_h[place].Clone("ISTAT"+place)
    decessi_excess_only_h[place].Add(fitLinears[place],-1)

fits, fits_res, fits_error              = fitExp(decessi_excess_only_h,      places, firstDate, lastDate, predictionsDate, maxConstExp=10000)
fitGausss, fitGausss_res, fitGausss_error              = fitGauss(decessi_excess_only_h,      places, firstDate, dates.index("5/15/20"), predictionsDate, maxPar3=1E-9)
fitTails, fitTails_res, fitTails_error              = fitExp(decessi_excess_only_h,      places, dates.index("3/27/20"), len(dates)-1, predictionsDate, maxConstExp=10000, tail=True)


d3 = ROOT.TCanvas("d1","",resX,resY)
leg = ROOT.TLegend(0.9,0.1,1.0,0.9)
leg.Draw()
d3.SetGridx()
d3.SetGridy()

fits_sigOnly={}
funct_const = ROOT.TF1("funct_const","[0]",firstDate,predictionsDate)
firstDeaths = {}

for place in places:
    fits[place].fitResult = fits_res[place]
    if fits[place].fitResult.Get():
        fit_val = fits[place].fitResult.GetParams()[1]
        fit_err = fits[place].fitResult.GetErrors()[1]
        if fit_val>0 and fit_val<lastDate and fit_err<3.5:
            firstDeaths[place] = (fit_val,  fit_err)


goodFits = []
firstDeath_f = open("firstDeath.csv","w")
firstDeathsInv = {v: k for k, v in firstDeaths.iteritems()}
firstDeath_f.write("%s,%s,%s\n"%("place","days since 1/1/2020", "date"))
for x in sorted(firstDeathsInv.keys()):
    print "%.2f +/- %.2f (%s)\t%s"%(x[0], x[1], dates[int(x[0]+0.5)], str(firstDeathsInv[x]))
    goodFits.append(str(firstDeathsInv[x]))
    firstDeath_f.write("%s,%.2f +/- %.2f,%s\n"%(str(firstDeathsInv[x]),x[0], x[1], dates[int(x[0]+0.5)] ))

firstDeath_f.close()

for place in places:
#for place in goodFits:
    decessi_h[place].SetLineColor(ROOT.kBlack)
    decessi_old_h[place].SetLineColor(ROOT.kMagenta+1)
    decessi_h[place].GetYaxis().SetTitle("Number of deaths / day")
    decessi_h[place].SetMinimum(0.1)
    decessi_h[place].SetMaximum(2*decessi_h[place].GetMaximum())
    fits[place].error = fits_error[place]
    fits[place].fitResult = fits_res[place]
    fits_sigOnly[place] = fits[place].Clone(fits[place].GetName()+"_sig")
    funct_const.SetParameter(0 , fits_sigOnly[place].GetParameter(2))
    fits_sigOnly[place].SetParameter(2, 0 )
    fits_sigOnly[place].error = fits_error[place].Clone(fits_error[place].GetName()+"_sig")
    fits_sigOnly[place].error.Add(funct_const, -1)
    fits[place].SetLineColor(ROOT.kBlue)
    fits_sigOnly[place].SetLineColor(ROOT.kRed)
    fits[place].label="Fit totale"
    fits_sigOnly[place].label="Fit solo eccesso"
    fitGausss[place].SetLineColor(ROOT.kBlack)
    fitGausss[place].error = fitGausss_error[place]
    fitGausss[place].fitResult = fitGausss_res[place]
    fitGausss[place].label="Fit Gaus"
    fitLinears[place].SetLineColor(ROOT.kMagenta)
    fitLinears[place].error = fitLinears_error[place]
    fitLinears[place].fitResult = fitLinears_res[place]
    fitLinears[place].label="Fit 2015/19"
#    funct_const.label="Fit costante"
#    funct_const.SetLineColor(ROOT.kGreen+2)
#    funct_const.SetLineStyle(2)
#    funct_const.error = None
    fitTails[place].label="Fit costante"
    fitTails[place].SetLineColor(ROOT.kGreen+2)
    fitTails[place].SetLineStyle(2)
    fitTails[place].error = fitTails_error[place]
    fitTails[place].fitResult = fitTails_res[place]
    savePlotNew([decessi_h[place], decessi_old_h[place], decessi_excess_only_h[place]], [fits[place], fits_sigOnly[place], fitTails[place], fitGausss[place], fitLinears[place]], "plotsISTAT/%s.png"%place, startDate, d3, True)



