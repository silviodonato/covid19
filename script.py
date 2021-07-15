# -*- coding: utf-8 -*-
#import csv
#import copy
from tools import colors, fillData, newCases, getRatio, makeHistos, fitErf, fitGaussAsymmetric, fitExp, extendDates, saveCSV, savePlotNew, getPrediction, getPredictionErf, shiftHisto, applyScaleFactors, useLog, positiveHisto, getScaled, fitTwoExp

useScaleFactor = True
startFromZero = True

import ROOT
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)
#ROOT.gROOT.SetBatch(0)

resX, resY = 1920, 1080

#file_ = ROOT.TFile("data.root", "RECREATE")



confirmes, dates = fillData('dataWorld/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

deaths, dates = fillData('dataWorld/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv')

recoveres, dates = fillData('dataWorld/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv')

lastDateData = len(dates)-1
dates = extendDates(dates, 650)
################

firstDate = 0
#firstDate = dates.index("6/1/20")
#firstDate = dates.index("5/15/20")
#firstDate = dates.index("5/15/20")
#firstDate = dates.index("9/1/20")
#firstDate = dates.index("12/1/20")
#firstDate = dates.index("12/30/20")
#firstDate = dates.index("12/31/20")
#firstDate = dates.index("8/23/20")
firstDate = dates.index("6/1/21")
#firstDate = dates.index("1/1/21")
#firstDate = dates.index("12/20/20")
#firstDate = dates.index("4/1/20")
#firstDate = 16
#firstDate = dates.index("10/1/20")
lastDate = lastDateData - 1
#lastDate = dates.index("2/29/20")
#lastDate = dates.index("3/1/20")
#lastDate = 30
#predictionsDate = dates.index("12/31/20")
#predictionsDate = dates.index("8/1/21")
predictionsDate = dates.index("10/1/21")
#predictionsDate = 95

#firstDate = dates.index("4/30/20")
#lastDate  = dates.index("8/1/20")
#predictionsDate = dates.index("6/21/20")

#firstDate = 10
#lastDate = 35
#predictionsDate = 35

#firstDate = dates.index("10/1/20")
#lastDate = dates.index("10/15/20")
#predictionsDate = lastDate+1

################

#confirmes = deaths

positives = {}
for place in confirmes:
    positives[place] = {}
    for i in range(0, len(confirmes[place])):
        positives[place][dates[i]] = confirmes[place][dates[i]] - deaths[place][dates[i]] - recoveres[place][dates[i]]

newConfirmes = newCases(confirmes, dates)
newDeaths = newCases(deaths, dates)
newRecoveres = newCases(recoveres, dates)

################

## scale used ##
confirmes_scale=1
deaths_scale=40
deathIstatExcess_scale=20
intensivas_scale=100 
ricoveratis_scale=20
tests_scale=0.10

recoveres_scale=confirmes_scale
positives_scale=confirmes_scale
predictionConfirmes_scale=confirmes_scale
predictionRecoveres_scale=confirmes_scale
predictionPositives_scale=confirmes_scale
predictionIntensivas_scale=intensivas_scale
predictionRicoveratis_scale=ricoveratis_scale
predictionDeaths_scale=deaths_scale

newConfirmes_scale=confirmes_scale
newRecoveres_scale=confirmes_scale
newDeaths_scale=deaths_scale
newDeathIstatExcess_scale=deaths_scale
newIntensivas_scale=intensivas_scale 
newRicoveratis_scale=ricoveratis_scale
newTests_scale=tests_scale
newPositives_scale=confirmes_scale


###########################

places = []
for place in confirmes.keys():
    if place == "Others": continue
    if confirmes[place][dates[lastDate]]>1000000:
        places.append(place)

places = ["Switzerland", "United Kingdom", "India", "US", "Germany", "Singapore", "Spain", "Russia", "Italy", "Belgium", "Portugal", "France", "Denmark", "Indonesia", "Japan", "Australia", "Switzerland", "Ireland", "Canada", "Finland", "Mexico", "Israel", "Thailand", "Poland", "Norway", "Argentina", "Neatherlands"]
#places = ["Switzerland"]
#places = ["Italy"]
#places = ["United Kingdom"]
#places = ["Rest of Europe"]
#places = ["Italy","Japan","South Korea"]
#places = ["Guangdong","Henan","Zhejiang","Hunan","Anhui","Jiangxi","Italy"]
#places = ["Zhejiang"]
#places = ["Jiangxi"]
#places = ["France"]

#places.remove("World")


places = [p[1] for p in sorted([(confirmes[p][dates[lastDate]], p) for p in places], reverse=True)]

if "World" in place: places.remove("World")
if "Rest of World" in place: places.remove("Rest of World")

#places = ["Italy"]

print "places:",places

################

fits   = {}
fits2   = {}
fitdiffs   = {}

c1 = ROOT.TCanvas("c1","",resX,resY)

smear = 1
eType = "3sqrtN"
positives_h     = makeHistos("histo_positives", positives,    dates, places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='cumulative', lineWidth=2, daysSmearing=1)
confirmes_h     = makeHistos("histo_confirmes", confirmes,    dates, places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='cumulative', lineWidth=2, daysSmearing=1)
recoveres_h     = makeHistos("histo_recoveres", recoveres,    dates, places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='cumulative', lineWidth=2, daysSmearing=1)
deaths_h        = makeHistos("histo_deaths",    deaths,       dates, places, firstDate, lastDate, predictionsDate, 0, cutTails=False, errorType='cumulative', lineWidth=2, daysSmearing=1)
#histos          = makeHistos(confirmes, places, firstDate, lastDate, predictionsDate, cumulativeError=True)

if startFromZero:
    for place in places:
        for histo in [positives_h,confirmes_h,recoveres_h,deaths_h]:
            minVal_ = histo[place].GetBinContent(1)
            for ibin in range(1,lastDate-firstDate):
                val = histo[place].GetBinContent(ibin)
                if val < minVal_:
                    minVal_ = val
#            val = float(minVal_-1)
            val = histo[place].GetBinContent(1)
            for i in range(histo[place].GetNbinsX()+2):
                if histo[place].GetBinContent(i)!=0:
                    histo[place].SetBinContent(i, histo[place].GetBinContent(i) - val)
#            removeOffset(histo[place], firstDate)


newConfirmes_h  = makeHistos("histo_newConfirmes", newConfirmes, dates, places, firstDate, lastDate, predictionsDate, 1, cutTails=False,  lineWidth=2, daysSmearing=smear, errorType=eType)
newRecoveres_h  = makeHistos("histo_newRecoveres", newRecoveres, dates, places, firstDate, lastDate, predictionsDate, 1, cutTails=False, lineWidth=2, daysSmearing=smear, errorType=eType)
newDeaths_h     = makeHistos("histo_newDeaths",    newDeaths,    dates, places, firstDate, lastDate, predictionsDate, 1, cutTails=False, lineWidth=2, daysSmearing=smear, errorType=eType)
#newPositives_h  = makeHistos(newPositives, dates, places, firstDate, lastDate, predictionsDate)

for place in places:
    if useScaleFactor:
        for histo in [newConfirmes_h,newConfirmes_h,newRecoveres_h,newDeaths_h]:
            applyScaleFactors(histo[place], errorType=eType)
    if useLog:
        for histo in [newConfirmes_h,newConfirmes_h,newRecoveres_h,newDeaths_h]:
            positiveHisto(histo[place])


fits, fits_res, fits_error                         = fitErf(confirmes_h,      places, firstDate, lastDate, predictionsDate)
fitexps, fitexps_res, fitexps_error                = fitExp(newConfirmes_h,   places, lastDate-8, lastDate, predictionsDate)
fitexptotals, fitexptotals_res, fitexptotals_error = fitExp(confirmes_h,      places, lastDate-8, lastDate, predictionsDate)
fitdiffs, fitdiffs_res, fitdiffs_error             = fitTwoExp(newConfirmes_h, places, firstDate, lastDate, predictionsDate)
fitOnediffs, fitOnediffs_res, fitOnediffs_error             = fitTwoExp(newConfirmes_h, places, firstDate, lastDate, predictionsDate, oneExp=True)
fitdiffDeaths, fitdiffDeaths_res, fitdiffDeaths_error = fitTwoExp(newDeaths_h, places, firstDate, lastDate, predictionsDate)
fitdiffRecoveres, fitdiffRecoveres_res, fitdiffRecoveres_error = fitTwoExp(newRecoveres_h, places, firstDate, lastDate, predictionsDate)

for a in positives_h.values(): a.SetName('positives_'+a.GetName())

#for place in places:
#    fits2[place] = copy.copy(ROOT.TF1("function"+place,"[0]*(1+TMath::Erf((x-[1])/[2])) + [3]",0,predictionsDate))
#    mea = fitdiffs[place].GetParameter(1)
#    sig = abs(fitdiffs[place].GetParameter(2))
#    print "mean, sigma 0 = ", mea, sig
#    fits2[place].SetParameters(confirmes[place][dates[lastDate]], mea, sig)
#    histos[place].Fit(fits2[place],"0","",mea - 2*sig,lastDate)
#    for i in range(10):
#        mea = fits2[place].GetParameter(1)
#        sig = abs(fits2[place].GetParameter(2))
#        print "mean, sigma %i = ", mea, sig
#        histos[place].Fit(fits2[place],"0","",mea - 2*sig ,lastDate)
#    histos[place].Fit(fits2[place],"0","",mea - 2*sig,lastDate)
#    color = colors[confirmes.keys().index(place)]
#    fits2[place].SetLineColor(color)

#histos["Italy"].Draw()

#for place in confirmes.keys():
leg = ROOT.TLegend(0.9,0.1,1.0,0.9)

for place in places:
    confirmes_h[place].GetYaxis().SetTitle("Number of cases")
    confirmes_h[place].SetMinimum(1)
#    confirmes_h[place].SetBinError(confirmes_h[place].FindBin(lastDate-0.5),1E-9)
    leg.AddEntry(confirmes_h[place], place, "lep")
    confirmes_h[place].Draw("ERR,same")
    recoveres_h[place].SetLineStyle(2)
#    recoveres_h[place].Draw("ERR,same")
    deaths_h[place].SetLineStyle(3)
#    deaths_h[place].Draw("ERR,same")
#    fits[place].Draw("same")

leg.Draw()
c1.SetGridx()
c1.SetGridy()
c1.SetLogy()
c1.Update()
c1.SaveAs("c1.png")

c2 = ROOT.TCanvas("c1","",resX,resY)

#diffs["Italy"].Draw()

#for place in ['Japan','Italy','Spain','France','South Korea']:
for place in places:
    newConfirmes_h[place].GetYaxis().SetTitle("Number of cases / day")
    newConfirmes_h[place].SetMinimum(1)
    newConfirmes_h[place].Draw("same")
    fitdiffs[place].Draw("same")



leg.Draw()
c2.SetGridx()
c2.SetGridy()
c2.SetLogy()
c2.Update()
c2.SaveAs("c2.png")

##########################################

c3 = ROOT.TCanvas("c1","",resX,resY)

histo_sigma1 = ROOT.TH1F("histo_sigma1","",100,0,30)
histo_sigma2 = ROOT.TH1F("histo_sigma2","",100,0,30)

for place in places:
    histo_sigma1.Fill(abs(fitdiffs[place].GetParameter(2)))
#    histo_sigma2.Fill(abs(fits[place].GetParameter(2)))

histo_sigma1.Draw()
histo_sigma2.Draw("same")
histo_sigma1.Fit("gaus")
print "Mean=",histo_sigma1.GetMean()
print "RMS=",histo_sigma1.GetRMS()

leg.Draw()
c3.SetGridx()
c3.SetGridy()
c3.SetLogy()
c3.Update()
c3.SaveAs("c3.png")

#input()
########################################

##########################################

'''
c4 = ROOT.TCanvas("c1","",resX,resY)

#ratios = getRatio(newDeaths_h, newRecoveres_h)
ratios = getRatio(deaths_h, recoveres_h)
#ratios = getRatio(deaths_h, confirmes_h)
#ratios = getRatio(recoveres_h, confirmes_h)

for place in ratios:
    ratios[place].SetMaximum(1)
    ratios[place].SetMinimum(0)
    ratios[place].Draw("HIST,C,same")

leg.Draw()
c4.SetGridx()
c4.SetGridy()
c4.SetLogy(0)
c4.Update()
'''

########################################

#print confirmes
#print confirmes["Italy"]["2/2/20"]

#file_.Write()
#file_.Close()

'''
print "############"
print "PREDICTION From %s to %s"%(dates[lastDate], dates[predictionsDate])
print "############"


for place in places:
    print "#### ",place," ####"
    print "Confirmed (%s): %d"%(dates[lastDate], confirmes_h[place].GetBinContent(confirmes_h[place].FindBin(lastDate)))
    val = confirmes_h[place].GetBinContent(confirmes_h[place].FindBin(lastDate))
    print "Expected fit total (%s): %f"%(dates[predictionsDate], val + (fits[place].Eval(predictionsDate)-fits[place].Eval(lastDate)))
    integr = fitdiffs[place].Integral(lastDate + 0.5, predictionsDate + 0.5)
    interr = fitdiffs[place].IntegralError(lastDate + 0.5, predictionsDate + 0.5, fitdiffs_res[place].GetParams(), fitdiffs_res[place].GetCovarianceMatrix().GetMatrixArray())
    print "Expected fit new cases (%s): %f +/- %f"%(dates[predictionsDate],  val + integr, interr)
#    for d in range(lastDate,predictionsDate):
#        val = val + fitdiffs[place].Eval(d+1)
#    print "Expected fit new cases (%s): %f"%(dates[predictionsDate],  val)
    try:
        print "Real Confirmed (%s): %d"%(dates[predictionsDate], confirmes[place][dates[predictionsDate]])
        print "Error (sigma) : %f"%( (confirmes[place][dates[predictionsDate]] - (val + integr)) / interr)
    except:
        pass
'''

endDate = predictionsDate
startDate = lastDate+1
predictions = getPrediction(places, dates, startDate, endDate, confirmes_h, fitdiffs, fitdiffs_res, confirmes)
#predictions = getPredictionErf(places, dates, startDate, endDate, confirmes_h, fits, fits_res, confirmes)

#predictionHistos = makeHistos("histo_predictions",    predictions, dates, startDate, endDate, predictionsDate, 0, errorType='dictionary')
predictions_h = makeHistos("histo_predictions",    predictions, dates, places, startDate, None, endDate, threshold=0, cutTails=False, errorType='dictionary', lineWidth=3)

predictionDeaths = getPrediction(places, dates, startDate, endDate, deaths_h, fitdiffDeaths, fitdiffDeaths_res, deaths)
predictionDeaths_h = makeHistos("histo_predictionDeaths",    predictionDeaths, dates, places, startDate, None, endDate, threshold=0, cutTails=False, errorType='dictionary', lineWidth=3)

predictionRecoveres = getPrediction(places, dates, startDate, endDate, recoveres_h, fitdiffRecoveres, fitdiffRecoveres_res, recoveres)
predictionRecoveres_h = makeHistos("histo_predictionRecoveres",    predictionRecoveres, dates, places, startDate, None, endDate, threshold=0, cutTails=False, errorType='dictionary', lineWidth=3)

saveCSV(predictions, places, dates, "prediction.csv", "prediction_error.csv")
saveCSV(predictionDeaths, places, dates, "predictionDeath.csv", "predictionDeath_error.csv")
saveCSV(predictionRecoveres, places, dates, "predictionRecovered.csv", "predictionRecovered_error.csv")


c5 = ROOT.TCanvas("c5","",resX,resY)

#ratios = getRatio(newDeaths_h, newRecoveres_h)
ratios = getRatio(deaths_h, recoveres_h)
#ratios = getRatio(deaths_h, confirmes_h)
#ratios = getRatio(recoveres_h, confirmes_h)

for place in ratios:
    ratios[place].SetMaximum(1)
    ratios[place].SetMinimum(0)
    ratios[place].Draw("HIST,C,same")

leg.Draw()
c5.SetGridx()
c5.SetGridy()
c5.SetLogy(0)
c5.Update()

for place in places:
#    savePlot(confirmes_h[place], recoveres_h[place], deaths_h[place], predictions_h[place], fits[place], fits_res[place], fits_error[place], fitexptotals[place], "plots/%s.png"%place, lastDate, c5)
    shiftConf = None
    shiftNewConf = None
#    shiftConf = shiftHisto(confirmes_h[place], 14)
#    shiftNewConf = shiftHisto(newConfirmes_h[place], 14)
#    savePlot(confirmes_h[place], recoveres_h[place], deaths_h[place], predictions_h[place], shiftConf, None, None, None, None, None, fitexptotals[place], "plots/%s.png"%place, lastDate, c3)
#    savePlot(newConfirmes_h[place], newRecoveres_h[place], newDeaths_h[place],  shiftNewConf, None, None, None, fitdiffs[place], fitdiffs_res[place], fitdiffs_error[place], fitexps[place], "plots/%s_newCases.png"%place, lastDate, c5)
    fitexptotals[place].error = fitexptotals_error[place]
    fitexptotals[place].fitResult = fitexptotals_res[place]
    fitOnediffs[place].error = fitOnediffs_error[place]
    fitOnediffs[place].fitResult = fitOnediffs_res[place]
    fitdiffs[place].error = fitdiffs_error[place]
    fitdiffs[place].fitResult = fitdiffs_res[place]
    fitdiffDeaths[place].error = fitdiffDeaths_error[place]
    fitdiffDeaths[place].fitResult = fitdiffDeaths_res[place]
    fitdiffRecoveres[place].error = fitdiffRecoveres_error[place]
    fitdiffRecoveres[place].fitResult = fitdiffRecoveres_res[place]
    fitexps[place].error = fitexps_error[place]
    fitexps[place].fitResult = fitexps_res[place]
#    fitexps[place].error = None
#    fitexps[place].fitResult = None
    savePlotNew([confirmes_h[place], recoveres_h[place], deaths_h[place], predictions_h[place], predictionDeaths_h[place], predictionRecoveres_h[place], shiftConf], [fitexptotals[place]], "plots/%s.png"%place, startDate, dates, c3)
    savePlotNew([newConfirmes_h[place], newRecoveres_h[place], newDeaths_h[place], shiftNewConf], [fitdiffs[place], fitOnediffs[place], fitdiffRecoveres[place], fitdiffDeaths[place], fitexps[place]], "plots/%s_newCases.png"%place, startDate, dates, c5)

    savePlotNew([getScaled(newConfirmes_h[place],newConfirmes_scale), getScaled(newRecoveres_h[place],newRecoveres_scale), getScaled(newDeaths_h[place],newDeaths_scale)], [fitexps[place], fitdiffs[place], fitOnediffs[place], fitdiffRecoveres[place]], "plots/%s_newCases_scaled.png"%place, startDate, dates, c5, log=False)
    
    fromZero=False
    savePlotNew([getScaled(confirmes_h[place], confirmes_scale, fromZero), getScaled(recoveres_h[place], recoveres_scale, fromZero), getScaled(deaths_h[place], deaths_scale, fromZero), getScaled(predictionDeaths_h[place], predictionDeaths_scale, fromZero), getScaled(predictionRecoveres_h[place], predictionRecoveres_scale, fromZero), getScaled(positives_h[place], positives_scale, fromZero)], [fitexptotals[place]], "plots/%s_scaled.png"%place, startDate, dates, c5, log=False)
    
    
    positiveToTestRatio = newConfirmes_h[place].Clone("positiveToTestRatio_"+place)
    positiveToTestRatio.Reset()
#    positiveToTestRatio.Divide(newConfirmes_h[place], newTests_h[place])
#    positiveHisto(positiveToTestRatio)
    
#    for i in range(positiveToTestRatio.GetNbins()+2):
#        if positiveToTestRatio.GetBinContent(i)<0: positiveToTestRatio.SetBinContent(i,0)
    
    deathToRecoverRatio = deaths_h[place].Clone("deathToRecoverRatio_"+place)
    deathToRecoverRatio.Reset()
    deathToRecoverRatio.Divide(recoveres_h[place], deaths_h[place])
    
    deathDailyToRecoverRatio = newDeaths_h[place].Clone("deathDailyToRecoverRatio_"+place)
    deathDailyToRecoverRatio.Reset()
    deathDailyToRecoverRatio.Divide(newRecoveres_h[place], newDeaths_h[place])

    savePlotNew([getScaled(positiveToTestRatio,1000), deathToRecoverRatio,deathDailyToRecoverRatio], [], "plots/%s_rapporto.png"%place, startDate, dates, c5, log=False)



ROOT.gROOT.SetBatch(0)
canv=ROOT.TCanvas("canv")


p = places [0]

newConfirmes_h[p].Draw()
fitOnediffs[p].Draw("same")
fitOnediffs[p].error.Draw("same")



'''



TFitResultPtr r = graph->Fit(myFunction,"S");

double x[1] = { x0 };
double err[1];  // error on the function at point x0

r->GetConfidenceIntervals(1, 1, 1, x, err, 0.683, false);
cout << " function value at " << x[0] << " = " << myFunction->Eval(x[0]) << " +/- " << err[0] << endl;
'''
