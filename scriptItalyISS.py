# -*- coding: utf-8 -*-
#import csv
#import copy
from tools import colors, fillDataRegioni, fillDataISTATpickle, newCases, getRatio, makeHistos, fitErf, fitGauss, fitGaussAsymmetric, fitExp, extendDates, saveCSV, savePlotNew, getPrediction, getPredictionErf, getColumn, selectComuniDatesAgeGender, makeCompatible, fitLinear, fitTwoExp, fitGaussExp, applyScaleFactors, useLog, positiveHisto, fitTwoGaussDiff, fitGaussExp, getScaled, fillDataISS

useDatiISTAT = False
useScaleFactor = True
daysSmearing = 1
places = ["Italia"]

import ROOT
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
#ROOT.gROOT.SetBatch(0)

resX, resY = 1920, 1080

dataCasi, dates = fillDataISS('calcoloRt/casi_inizio_sintomi.csv')
casi = getColumn(dataCasi, "CASI")

dataCasiSintomatici, dateCasiSintomatici = fillDataISS('calcoloRt/casi_inizio_sintomi_sint.csv')
casiSintomatici = getColumn(dataCasiSintomatici, "CASI_SINT")

dataPrelievi, datesPrelievi = fillDataISS('calcoloRt/casi_prelievo_diagnosi.csv')
prelievi = getColumn(dataPrelievi, "CASI")

dataDecessi, datesDecessi = fillDataISS('calcoloRt/decessi.csv')
decessi = getColumn(dataDecessi, "DECESSI")

lastDateData = len(dates)-1
dates = extendDates(dates, 650)
print(dates)
print(dataCasi["Italia"])
print(dataCasiSintomatici["Italia"])
print(dataPrelievi["Italia"])
print(dataDecessi["Italia"])

################


#firstDate = 0
#firstDate = dates.index("6/1/20")
#firstDate = dates.index("5/15/20")
#firstDate = dates.index("5/15/20")
#firstDate = dates.index("9/1/20")
#firstDate = dates.index("12/1/20")
#firstDate = dates.index("12/30/20")
#firstDate = dates.index("10/1/20")
#firstDate = dates.index("1/1/21")
firstDate = dates.index("4/11/21")
#firstDate = dates.index("10/1/20")
#firstDate = dates.index("1/1/21")
#firstDate = dates.index("12/20/20")
#firstDate = dates.index("4/1/20")
#firstDate = 16
lastDate = lastDateData - 2
#lastDate = dates.index("2/29/20")
#lastDate = dates.index("3/1/20")
#lastDate = 30
#predictionsDate = dates.index("12/31/20")
predictionsDate = dates.index("7/11/21")
#predictionsDate = 95

#firstDate = dates.index("3/1/20")
#lastDate  = dates.index("5/1/20")
#predictionsDate = dates.index("6/30/20")

#firstDate = 10
#lastDate = 35
#predictionsDate = 35

#firstDate = dates.index("10/1/20")
#lastDate = dates.index("10/15/20")
#predictionsDate = lastDate+1

################

#casi = decessi


newcasi = casi
newdecessi = decessi
newprelievi = prelievi
newcasiSintomatici = casiSintomatici


#newcasi = newCases(casi, dates)
#newdecessi = newCases(decessi, dates)
#newprelievi = newCases(prelievi, dates)
#newcasiSintomatici = newCases(casiSintomatici, dates)
#newIntensivas = newCases(intensivas, dates) # newIntensivas taken from ingressi_terapia_intensiva

intensivas = []
ricoveratis = []
positives = []
newRicoveratis = []
newPositives = []
newIntensivas = []

###########################

## scale used ##
casi_scale=1
decessi_scale=40
decessiIstatExcess_scale=20
intensivas_scale=90 
ricoveratis_scale=20
casiSintomatici_scale=0.10

prelievi_scale=casi_scale
positives_scale=casi_scale
predictioncasi_scale=casi_scale
predictionprelievi_scale=casi_scale
predictionPositives_scale=casi_scale
predictionIntensivas_scale=intensivas_scale
predictionRicoveratis_scale=ricoveratis_scale
predictiondecessi_scale=decessi_scale

newcasi_scale=casi_scale
newprelievi_scale=casi_scale
newdecessi_scale=decessi_scale
newdecessiIstatExcess_scale=decessi_scale
newIntensivas_scale=intensivas_scale 
newRicoveratis_scale=ricoveratis_scale
newcasiSintomatici_scale=casi_scale
newPositives_scale=casi_scale

################

fits   = {}
fits2   = {}
fitdiffs   = {}

d1 = ROOT.TCanvas("d1","",resX,resY)


print(places)
casi_h = makeHistos("histo_casi", casi,        dates, places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='cumulative', lineWidth=2, daysSmearing=1)
prelievi_h = makeHistos("histo_prelievi", prelievi,        dates, places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='cumulative', lineWidth=2, daysSmearing=1)
decessi_h    = makeHistos("histo_decessi", decessi,           dates, places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='cumulative', lineWidth=2, daysSmearing=1)
casiSintomatici_h    = makeHistos("histo_casiSintomatici", casiSintomatici,           dates, places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='cumulative', lineWidth=2, daysSmearing=1)


#casiSintomatici_h["Italia"].Draw()
#casiSintomatici_h["Italia"].Integral()
#print(casiSintomatici["Italia"]["4/11/21"])
#1/0
#print("CHECK",positives_h[place].GetBinContent(1))

#histos = makeHistos(casi, places, firstDate, lastDate, predictionsDate, cumulativeError=True)
#eType = "default"
eType = "3sqrtN"
newcasi_h  = makeHistos("histo_newcasi", newcasi, dates, places, firstDate, lastDate, predictionsDate, 1, cutTails=True, lineWidth=2, daysSmearing=daysSmearing, errorType=eType)
newprelievi_h  = makeHistos("histo_newprelievi", newprelievi, dates, places, firstDate, lastDate, predictionsDate, 1, cutTails=False, lineWidth=2, daysSmearing=daysSmearing, errorType=eType)
newdecessi_h     = makeHistos("histo_newdecessi", newdecessi,    dates, places, firstDate, lastDate, predictionsDate, 1, cutTails=False, lineWidth=2, daysSmearing=daysSmearing, errorType=eType)
newcasiSintomatici_h     = makeHistos("histo_newcasiSintomatici", newcasiSintomatici,    dates, places, firstDate, lastDate, predictionsDate, 1, cutTails=False, lineWidth=2, daysSmearing=daysSmearing, errorType=eType)

place = places[0]

for place in places:
#    positiveHisto(casiSintomatici_h[place])
#    positiveHisto(newcasiSintomatici_h[place])
#    positiveHisto(casi_h[place])
#    positiveHisto(newcasi_h[place])
#    positiveHisto(decessi_h[place])
#    positiveHisto(newdecessi_h[place])
    if useScaleFactor:
        for histos in [newcasi_h,newprelievi_h,newdecessi_h,newcasiSintomatici_h]: #newRicoveratis_h,
            applyScaleFactors(histos[place], errorType=eType, maximum=histos[place].FindBin(lastDateData - 10))
            pass
    if useLog:
        for histo in [newcasi_h,newprelievi_h,newdecessi_h,newcasiSintomatici_h,casi_h,prelievi_h,decessi_h,casiSintomatici_h]:
#            positiveHisto(histo[place])
            pass


print(newcasiSintomatici_h[place])

#fits, fits_res, fits_error              = fitErf(casi_h,      places, firstDate, lastDate, predictionsDate)
##fitdiffs, fitdiffs_res, fitdiffs_error  = fitGaussAsymmetric(newcasi_h, places, firstDate, lastDate, predictionsDate)
#fitdiffs, fitdiffs_res, fitdiffs_error  = fitTwoExp(newcasi_h, places, firstDate, lastDate, predictionsDate)
#fitexps, fitexps_res, fitexps_error                = fitExp(newcasi_h, places, lastDate-14, lastDate, predictionsDate)
#fitexptotals, fitexptotals_res, fitexptotals_error = fitExp(casi_h,    places, lastDate-14-1, lastDate-1, predictionsDate)
##fitexptotals, fitexptotals_res, fitexptotals_error = fitExp(casi_h,    places, lastDate-8, lastDate, predictionsDate)
#fitdiffIntensivas, fitdiffIntensivas_res, fitdiffIntensivas_error = fitTwoGaussDiff(newIntensivas_h, places, firstDate, lastDate, predictionsDate)
#fitdiffPositives, fitdiffPositives_res, fitdiffPositives_error = fitTwoGaussDiff(newPositives_h, places, firstDate, lastDate, predictionsDate)
#fitdiffRicoveratis, fitdiffRicoveratis_res, fitdiffRicoveratis_error = fitTwoGaussDiff(newRicoveratis_h, places, firstDate, lastDate, predictionsDate)
#fitdiffdecessi, fitdiffdecessi_res, fitdiffdecessi_error = fitTwoExp(newdecessi_h, places, firstDate, lastDate, predictionsDate)
#fitdiffprelievi, fitdiffprelievi_res, fitdiffprelievi_error = fitTwoExp(newprelievi_h, places, firstDate, lastDate, predictionsDate)

newdecessiIstatExcess_h = {}
if useDatiISTAT: 
    newdecessiIstats_h        = makeHistos("histo_ISTAT",     newdecessiIstats,        dates, places, firstDate, lastDate, predictionsDate, 1, cutTails=False, lineWidth=2, errorType='sqrtN')
    newdecessiIstats_old_h    = makeHistos("histo_ISTAT_old", newdecessiIstats_old,    dates, places, firstDate, lastDate, predictionsDate, 1, cutTails=False, lineWidth=2, errorType='sqrtN')
    for place in newdecessiIstats_old_h:
        if newdecessiIstats_old_h[place].Integral(0, dates.index("2/28/20"))>0: newdecessiIstats_old_h[place].Scale(newdecessiIstats_h[place].Integral(0, dates.index("2/28/20"))/newdecessiIstats_old_h[place].Integral(0, dates.index("2/28/20")))
        feb29_bin = dates.index("3/1/20")
        newdecessiIstats_old_h[place].SetBinContent(feb29_bin, newdecessiIstats_old_h[place].GetBinContent(feb29_bin-1))
        newdecessiIstats_old_h[place].SetBinError(  feb29_bin, newdecessiIstats_old_h[place].GetBinContent(feb29_bin-1))
    fitLinears, fitLinears_res, fitLinears_error              = fitLinear(newdecessiIstats_old_h,      newdecessiIstats_old_h.keys(), firstDate+1, dates.index("4/30/20"), predictionsDate, maxConstExp=10000, tail=True, fitOption="SEQ0L")
    for place in newdecessiIstats_old_h:
        newdecessiIstatExcess_h[place] = newdecessiIstats_h[place].Clone(newdecessiIstats_h[place].GetName()+"Excess")
        newdecessiIstatExcess_h[place].Add(fitLinears[place],-1)

#1/0

    


#for place in places:
#    fits2[place] = copy.copy(ROOT.TF1("function"+place,"[0]*(1+TMath::Erf((x-[1])/[2])) + [3]",0,predictionsDate))
#    mea = fitdiffs[place].GetParameter(1)
#    sig = abs(fitdiffs[place].GetParameter(2))
#    print "mean, sigma 0 = ", mea, sig
#    fits2[place].SetParameters(casi[place][dates[lastDate]], mea, sig)
#    histos[place].Fit(fits2[place],"0","",mea - 2*sig,lastDate)
#    for i in range(10):
#        mea = fits2[place].GetParameter(1)
#        sig = abs(fits2[place].GetParameter(2))
#        print "mean, sigma %i = ", mea, sig
#        histos[place].Fit(fits2[place],"0","",mea - 2*sig ,lastDate)
#    histos[place].Fit(fits2[place],"0","",mea - 2*sig,lastDate)
#    color = colors[casi.keys().index(place)]
#    fits2[place].SetLineColor(color)

#histos["Italy"].Draw()

#for place in casi.keys():
leg = ROOT.TLegend(0.9,0.1,1.0,0.9)

for place in places:
    casi_h[place].GetYaxis().SetTitle("Number of cases")
    if useLog: casi_h[place].SetMinimum(1)
#    casi_h[place].SetBinError(casi_h[place].FindBin(lastDate-0.5),1E-9)
    leg.AddEntry(casi_h[place], place, "lep")
    casi_h[place].Draw("ERR,same")
    prelievi_h[place].SetLineStyle(2)
#    prelievi_h[place].Draw("ERR,same")
    decessi_h[place].SetLineStyle(3)
#    decessi_h[place].Draw("ERR,same")
#    fits[place].Draw("same")

leg.Draw()
d1.SetGridx()
d1.SetGridy()
d1.SetLogy(useLog)
d1.Update()

d1.SaveAs("d1.png")


leg = ROOT.TLegend(0.9,0.1,1.0,0.9)

    

d2 = ROOT.TCanvas("d2","",resX,resY)

#diffs["Italy"].Draw()


#for place in ['Japan','Italy','Spain','France','South Korea']:
for place in places:
    newcasi_h[place].GetYaxis().SetTitle("Number of cases / day")
    if useLog: newcasi_h[place].SetMinimum(1)
    newcasi_h[place].Draw("same")
#    fitdiffs[place].Draw("same")



leg.Draw()
d2.SetGridx()
d2.SetGridy()
d2.SetLogy(useLog)
d2.Update()
d2.SaveAs("d2.png")


##########################################

d3 = ROOT.TCanvas("d1","",resX,resY)
leg = ROOT.TLegend(0.9,0.1,1.0,0.9)

histo_sigma1 = ROOT.TH1F("histo_sigma1","",100,0,30)
histo_sigma2 = ROOT.TH1F("histo_sigma2","",100,0,30)

#for place in places:
#    histo_sigma1.Fill(abs(fitdiffs[place].GetParameter(2)))
#    histo_sigma2.Fill(abs(fits[place].GetParameter(2)))

histo_sigma1.Draw()
histo_sigma2.Draw("same")
histo_sigma1.Fit("gaus")
print("Mean=",histo_sigma1.GetMean())
print("RMS=",histo_sigma1.GetRMS())

leg.Draw()
d3.SetGridx()
d3.SetGridy()
d3.SetLogy(useLog)
d3.Update()
d3.SaveAs("d3.png")

#input()
########################################

##########################################

'''
d4 = ROOT.TCanvas("d1","",resX,resY)

#ratios = getRatio(newdecessi_h, newprelievi_h)
ratios = getRatio(decessi_h, prelievi_h)
#ratios = getRatio(decessi_h, casi_h)
#ratios = getRatio(prelievi_h, casi_h)

for place in ratios:
    ratios[place].SetMaximum(1)
    ratios[place].SetMinimum(0)
    ratios[place].Draw("HIST,C,same")

leg.Draw()
d4.SetGridx()
d4.SetGridy()
d4.SetLogy(0)
d4.Update()
'''

########################################

#print casi
#print casi["Italy"]["2/2/20"]

#file_.Write()
#file_.Close()

'''
print "############"
print "PREDICTION From %s to %s"%(dates[lastDate], dates[predictionsDate])
print "############"


for place in places:
    print "#### ",place," ####"
    print "sintomed (%s): %d"%(dates[lastDate], casi_h[place].GetBinContent(casi_h[place].FindBin(lastDate)))
    val = casi_h[place].GetBinContent(casi_h[place].FindBin(lastDate))
    print "Expected fit total (%s): %f"%(dates[predictionsDate], val + (fits[place].Eval(predictionsDate)-fits[place].Eval(lastDate)))
    integr = fitdiffs[place].Integral(lastDate + 0.5, predictionsDate + 0.5)
    interr = fitdiffs[place].IntegralError(lastDate + 0.5, predictionsDate + 0.5, fitdiffs_res[place].GetParams(), fitdiffs_res[place].GetCovarianceMatrix().GetMatrixArray())
    print "Expected fit new cases (%s): %f +/- %f"%(dates[predictionsDate],  val + integr, interr)
#    for d in range(lastDate,predictionsDate):
#        val = val + fitdiffs[place].Eval(d+1)
#    print "Expected fit new cases (%s): %f"%(dates[predictionsDate],  val)
    try:
        print "Real sintomed (%s): %d"%(dates[predictionsDate], casi[place][dates[predictionsDate]])
        print "Error (sigma) : %f"%( (casi[place][dates[predictionsDate]] - (val + integr)) / interr)
    except:
        pass
'''

endDate = predictionsDate
startDate = lastDate + 1
#predictioncasi = getPrediction(places, dates, startDate, endDate, casi_h, fitdiffs, fitdiffs_res, casi)
##predictions = getPredictionErf(places, dates, startDate, endDate, casi_h, fits, fits_res, casi)

##predictionHistos = makeHistos(predictions, dates, startDate, endDate, predictionsDate, 0, errorType='dictionary')
#predictioncasi_h = makeHistos("histo_predictioncasi", predictioncasi, dates, places, startDate, None, endDate, threshold=0, cutTails=False, errorType='dictionary', lineWidth=3)

#predictiondecessi = getPrediction(places, dates, startDate, endDate, decessi_h, fitdiffdecessi, fitdiffdecessi_res, decessi)
#predictiondecessi_h = makeHistos("histo_predictiondecessi",    predictiondecessi, dates, places, startDate, None, endDate, threshold=0, cutTails=False, errorType='dictionary', lineWidth=3)

#predictionprelievi = getPrediction(places, dates, startDate, endDate, prelievi_h, fitdiffprelievi, fitdiffprelievi_res, prelievi)
#predictionprelievi_h = makeHistos("histo_predictionprelievi",    predictionprelievi, dates, places, startDate, None, endDate, threshold=0, cutTails=False, errorType='dictionary', lineWidth=3)

#predictionRicoveratis = getPrediction(places, dates, startDate, endDate, ricoveratis_h, fitdiffRicoveratis, fitdiffRicoveratis_res, ricoveratis)
#predictionRicoveratis_h = makeHistos("histo_predictionRicoveratis",    predictionRicoveratis, dates, places, startDate, None, endDate, threshold=0, cutTails=False, errorType='dictionary', lineWidth=3)

#predictionIntensivas = getPrediction(places, dates, startDate, endDate, intensivas_h, fitdiffIntensivas, fitdiffIntensivas_res, intensivas)
#predictionIntensivas_h = makeHistos("histo_predictionIntensivas",    predictionIntensivas, dates, places, startDate, None, endDate, threshold=0, cutTails=False, errorType='dictionary', lineWidth=3)

#predictionPositives = getPrediction(places, dates, startDate, endDate, positives_h, fitdiffPositives, fitdiffPositives_res, positives)
#predictionPositives_h = makeHistos("histo_predictionPositives",    predictionPositives, dates, places, startDate, None, endDate, threshold=0, cutTails=False, errorType='dictionary', lineWidth=3)


#saveCSV(predictioncasi, places, dates, "predictionRegioni.csv", "predictionRegioni_error.csv")
#saveCSV(predictiondecessi, places, dates, "predictionRegioniMorti.csv", "predictionRegioniMorti_error.csv")
#saveCSV(predictionprelievi, places, dates, "predictionRegioniGuariti.csv", "predictionRegioniGuariti_error.csv")
#saveCSV(predictionIntensivas, places, dates, "predictionRegioniTerapiaIntensiva.csv", "predictionRegioniTerapiaIntensiva_error.csv")
#saveCSV(predictionPositives, places, dates, "predictionRegioniTerapiaPositive.csv", "predictionRegioniPositive_error.csv")
#saveCSV(predictionRicoveratis, places, dates, "predictionRegioniRicoverati.csv", "predictionRegioniRicoverati_error.csv")


d5 = ROOT.TCanvas("d5","",resX,resY)

#ratios = getRatio(newdecessi_h, newprelievi_h)
ratios = getRatio(decessi_h, prelievi_h)
#ratios = getRatio(decessi_h, casi_h)
#ratios = getRatio(prelievi_h, casi_h)

for place in ratios:
    ratios[place].SetMaximum(1)
    ratios[place].SetMinimum(0)
    ratios[place].Draw("HIST,C,same")

leg.Draw()
d5.SetGridx()
d5.SetGridy()
d5.SetLogy(useLog)
d5.Update()

for place in places:
#    savePlot(casi_h[place], prelievi_h[place], decessi_h[place], predictions_h[place], fits[place], fits_res[place], fits_error[place], fitexptotals[place], "plots/%s.png"%place, lastDate, d5)
#    fitexptotals[place].error = fitexptotals_error[place]
#    fitexptotals[place].fitResult = fitexptotals_res[place]
#    fitdiffs[place].error = fitdiffs_error[place]
#    fitdiffs[place].fitResult = fitdiffs_res[place]
#    fitdiffdecessi[place].error = fitdiffdecessi_error[place]
#    fitdiffdecessi[place].fitResult = fitdiffdecessi_res[place]
#    fitdiffprelievi[place].error = fitdiffprelievi_error[place]
#    fitdiffprelievi[place].fitResult = fitdiffprelievi_res[place]
#    fitdiffIntensivas[place].error = fitdiffIntensivas_error[place]
#    fitdiffIntensivas[place].fitResult = fitdiffIntensivas_res[place]
#    fitdiffPositives[place].error = fitdiffPositives_error[place]
#    fitdiffPositives[place].fitResult = fitdiffPositives_res[place]
#    fitdiffRicoveratis[place].error = fitdiffRicoveratis_error[place]
#    fitdiffRicoveratis[place].fitResult = fitdiffRicoveratis_res[place]
#    fitexps[place].error = fitexps_error[place]
#    fitexps[place].fitResult = fitexps_res[place]


    if useDatiISTAT: 
        if not place in fitLinears: fitLinears[place] = None
        else:
            fitLinears[place].error = fitLinears_error[place]
            fitLinears[place].res = fitLinears_res[place]
    if not place in newdecessiIstatExcess_h: newdecessiIstatExcess_h[place] = None
    savePlotNew([casi_h[place], prelievi_h[place], decessi_h[place], casiSintomatici_h[place] if useLog else 0], [], "plotsISS/%s.png"%place, startDate, dates, d3)
    savePlotNew([newcasi_h[place], newprelievi_h[place], newdecessi_h[place], newcasiSintomatici_h[place] if useLog else 0], [], "plotsISS/%s_newCases.png"%place, startDate, dates, d3)
    
    savePlotNew([getScaled(newcasi_h[place],newcasi_scale), getScaled(newprelievi_h[place],newprelievi_scale), getScaled(newdecessi_h[place],newdecessi_scale), getScaled(newcasiSintomatici_h[place],newcasiSintomatici_scale)], [], "plotsISS/%s_newCases_scaled.png"%place, startDate, dates, d3, log=False)
    
    fromZero=False
    savePlotNew([getScaled(casi_h[place], casi_scale, fromZero), getScaled(prelievi_h[place], prelievi_scale, fromZero), getScaled(decessi_h[place], decessi_scale, fromZero), getScaled(casiSintomatici_h[place], casiSintomatici_scale, fromZero)], [], "plotsISS/%s_scaled.png"%place, startDate, dates, d3, log=False)
    
    positiveTocasiSintomaticiRatio = newcasi_h[place].Clone("positiveTocasiSintomaticiRatio_"+place)
    positiveTocasiSintomaticiRatio.Reset()
    positiveTocasiSintomaticiRatio.Divide(newcasiSintomatici_h[place], newcasi_h[place])
#    positiveHisto(positiveTocasiSintomaticiRatio)
    
#    for i in range(positiveTocasiSintomaticiRatio.GetNbins()+2):
#        if positiveTocasiSintomaticiRatio.GetBinContent(i)<0: positiveTocasiSintomaticiRatio.SetBinContent(i,0)
    
    decessiToRecoverRatio = decessi_h[place].Clone("decessiToRecoverRatio_"+place)
    decessiToRecoverRatio.Reset()
    decessiToRecoverRatio.Divide(prelievi_h[place], decessi_h[place])
    
    decessiDailyToRecoverRatio = newdecessi_h[place].Clone("decessiDailyToRecoverRatio_"+place)
    decessiDailyToRecoverRatio.Reset()
    decessiDailyToRecoverRatio.Divide(newprelievi_h[place], newdecessi_h[place])

    savePlotNew([getScaled(positiveTocasiSintomaticiRatio,0.2), decessiToRecoverRatio,decessiDailyToRecoverRatio], [], "plotsISS/%s_rapporto.png"%place, startDate, dates, d3, log=False)




ROOT.gROOT.SetBatch(0)
canv=ROOT.TCanvas("canv")
p = "Italia"
#p = placescasiSintomatici[0]

#intensivas_h[p].Draw()
#newdecessi_h[p].Draw()
#fitdiffdecessi[p].Draw("same")
#print(fitdiffdecessi[p])
#fitdiffdecessi[p].Print()
#newdecessi_h[p].Fit(fitdiffdecessi[p])


#newcasi_h[p].Draw()
#fitdiffs[p].Draw("same")
#print(fitdiffs[p])

#fitdiffs[p].Print()
#newcasi_h[p].Fit(fitdiffs[p])


#newcasi_h[p].Draw()
#fitdiffs[p].Draw("same")

#newcasi_h['Liguria'].Draw()
#fitdiffs['Liguria'].Draw("same")


#newdecessi_h[p].Draw()
#fitdiffdecessi[p].Draw("same")

#intensivas_h[p].Draw()
#predictionIntensivas_h[p].Draw("same")

newcasi_h[p].Draw()
#fitdiffs[p].Draw("same")
#fitdiffs[p].error.Draw("same")

#newRicoveratis_h[p].Draw()
#fitdiffRicoveratis[p].Draw("same")

#newprelievi_h[p].Draw()
#fitdiffprelievi[p].Draw("same")

#hist = newcasi_h[p]

#fixSigma=10

#fitdiffs[place].SetParameters(hist.GetMaximum(), hist.GetXaxis().GetXmax(), fixSigma, hist.GetXaxis().GetXmax(), hist.GetXaxis().GetXmax()/log(hist.GetMaximum()))
#hist.Draw()
#fitdiffs[place].Draw("same")
        
'''



TFitResultPtr r = graph->Fit(myFunction,"S");

double x[1] = { x0 };
double err[1];  // error on the function at point x0

r->GetConfidenceIntervals(1, 1, 1, x, err, 0.683, false);
cout << " function value at " << x[0] << " = " << myFunction->Eval(x[0]) << " +/- " << err[0] << endl;
'''
