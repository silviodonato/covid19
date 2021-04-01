import ROOT,csv
from datetime import date

#cumulative = False
cumulative = True

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
colors += colors

#anagraficaFileName ="dataVaccini/dati/anagrafica-vaccini-summary-latest.csv"
consegneFileName ="dataVaccini/dati/consegne-vaccini-latest.csv"
somministrazioniFileName = "dataVaccini/dati/somministrazioni-vaccini-latest.csv"

def getPlot(somministrazioniTree, selection, dosi= "prima_dose+seconda_dose", cumulative=True, hname = None):
    sel = "1. * %s * (%s)"%(selection,dosi)
    somministrazioniTree.Draw("data_somministrazione >> histo", sel, "HIST")
    histo = ROOT.histo
    if cumulative:
        histo = histo.GetCumulative()
    if hname==None:
        hname = "histo_"+selection+dosi
        if cumulative: hname = hname + "cumul"
    histo = histo.Clone(hname)
    print(hname)
    print(sel)
    return histo


def convertData(label, data):
    
    if 'data' in label:
        yyyy, mm, dd = data.split("-")
        delta = date(int(yyyy), int(mm), int(dd)) - date(2021,1,1)
        return str(delta.days)
    elif label=='fornitore':
        if 'Pfizer'in data:
            return "1"
        elif 'Moderna' in data:
            return "2"
        elif 'Astrazeneca':
            return "-1"
    elif label=='fascia_anagrafica':
        if "90+" in data: return "90"
        return data.split("-")[0]
    else:
        return data

def getAnagrafica(fileName):
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        labels = None
        data = {}
        for row in csv_reader:
    #            print "XXX",row
            if line_count ==0:
                labels = row[:]
            else:
                for label in labels:
                    if not label in data: data[label]={}
                    data[label][convertData('fascia_anagrafica',row[0])]=convertData(label, row[labels.index(label)])
            line_count+=1
    return data

def updateROOTfile(fileName, rootFileName):
    newcsvFileName = fileName.replace(".csv","_tmp.csv")
    print("I'm building %s from %s"%(rootFileName,newcsvFileName))
    sel_labels = [
        "data_somministrazione",
        "numero_dosi",
    #    "area",
        "fornitore",
        "fascia_anagrafica",
        "sesso_maschile",
        "sesso_femminile",
        "categoria_operatori_sanitari_sociosanitari",
        "categoria_personale_non_sanitario",
        "categoria_ospiti_rsa",
        "categoria_over80",
        "categoria_forze_armate",
        "categoria_personale_scolastico",
        "categoria_altro",
        "prima_dose",
        "seconda_dose",
        "numero_dosi",
        "data_consegna",
    #    "codice_NUTS1",
    #    "codice_NUTS2",
        "codice_regione_ISTAT",
    #    "nome_area"
    ]
    
    fixed_csv = file(newcsvFileName,'w')
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        labels = None
        data = {}
        for row in csv_reader:
    #            print "XXX",row
            if line_count ==0:
                labels = row[:]
                for label in sel_labels:
                    if not label in labels: continue
                    fixed_csv.write(label)
                    if label==sel_labels[-1]:
                        fixed_csv.write("\n")
                    else:
                        fixed_csv.write(",")
            else:
                for label in sel_labels:
                    if not label in labels: continue
                    fixed_csv.write(convertData(label, row[labels.index(label)]))
                    if label==sel_labels[-1]:
                        fixed_csv.write("\n")
                    else:
                        fixed_csv.write(",")
            line_count+=1
    fixed_csv.close()
    
    fil_ = ROOT.TFile(rootFileName,"RECREATE")
    tree = ROOT.TTree()
    tree.SetName("tree")
    tree.ReadFile(newcsvFileName)
    
    tree.Write()
    fil_.Close()
    print("DONE")

#anagrafica = getAnagrafica("dataVaccini/dati/anagrafica-vaccini-summary-latest.csv")
consegneROOTFileName = consegneFileName.replace(".csv",".root")
somministrazioniROOTFileName = somministrazioniFileName.replace(".csv",".root")
#updateROOTfile(somministrazioniFileName, somministrazioniROOTFileName)
#updateROOTfile(consegneFileName, consegneROOTFileName)

somministrazioniFile = ROOT.TFile.Open(somministrazioniROOTFileName)
consegneFile = ROOT.TFile.Open(consegneROOTFileName)
somministrazioniTree = somministrazioniFile.Get("tree")
consegneTree = consegneFile.Get("tree")

ROOT.gStyle.SetOptStat("0")
print('''
selection = "(fornitore==-1) * (codice_regione_ISTAT==7)"
c1 = ROOT.TCanvas("c1")
somministrazioniTree.Draw("data_somministrazione >> histo","1. * %s * (prima_dose+seconda_dose)"%selection,"HIST")
histo = ROOT.histo.GetCumulative()
consegneTree.Draw("data_consegna >> histo2","1. * %s * (numero_dosi)"%selection,"HIST")
histo2 = ROOT.histo2.GetCumulative()
histo2.Draw("HIST")
histo.Draw("HIST,SAME")
''')

#selection = "(fornitore==-1) * (codice_regione_ISTAT==7)"
#somministrazioniTree.Draw("data_somministrazione >> histo","1. * %s * (prima_dose+seconda_dose)"%selection,"HIST")
#histo = ROOT.histo.GetCumulative()
#consegneTree.Draw("data_consegna >> histo2","1. * %s * (numero_dosi)"%selection,"HIST")
#histo2 = ROOT.histo2.GetCumulative()
#histo2.Draw("HIST")
#histo.Draw("HIST,SAME")

#selection = "(fornitore==-1) * (fascia_anagrafica==90)"

norms = {
    "categoria_operatori_sanitari_sociosanitari":1.876108E6,
    "categoria_personale_non_sanitario":0.31E6,
    "categoria_ospiti_rsa":0.34E6,
    "categoria_over80":4.64E6,
    "categoria_forze_armate":0.55E6,
    "categoria_personale_scolastico":1.49E6,
    "categoria_altro":60E6,
    "prima_dose":60E6,
    "seconda_dose":60E6,
    16:2.169E6, 
    20:6.130E6, 
    30:6.817E6, 
    40:8.940E6, 
    50:9.407E6, 
    60:7.379E6, 
    70:5.944E6, 
    80:3.628E6,
    90:0.792E6, 
}

cats = [
    "categoria_operatori_sanitari_sociosanitari",
    "categoria_personale_non_sanitario",
    "categoria_ospiti_rsa",
    "categoria_forze_armate",
    "categoria_personale_scolastico",
    "categoria_altro",
    "categoria_over80",
    90, 
    80,
    70, 
    60, 
    50, 
    40, 
    30, 
    20, 
    16, 
    "prima_dose",
    "seconda_dose",
]

max_=0
histos = {}
ratio = {}
for i,cat in enumerate(cats):
    dosi = str(cat)
    selection = "1"
    if type(cat)==int: 
        dosi = "(prima_dose+seconda_dose) * (fascia_anagrafica==%d)"%cat
    histos[cat] = getPlot(somministrazioniTree, selection = selection, dosi = dosi, cumulative = cumulative, hname="histo_%s"%str(cat))
    histos[cat].SetLineWidth(3)
    histos[cat].SetFillStyle(0)
    histos[cat].Scale(1./norms[cat])
    ratio[cat] = histos[cat].GetMaximum()
    if not "sanitari" in str(cat): 
        max_ = max(max_, histos[cat].GetMaximum())

leg = ROOT.TLegend(0.1,0.35,0.35,0.9)

c1 = ROOT.TCanvas("c1","",1920, 1080)
for i,cat in enumerate(reversed([x for _,x in sorted(zip(ratio.values(),ratio.keys()))])):
#    histos[cat].SetMaximum(max_*1.1)
    histos[cat].SetLineColor(colors[i])
    histos[cat].SetMaximum(2.)
    if i==0:
        histos[cat].Draw("HIST")
    else:
        histos[cat].Draw("HIST,same")
    leg.AddEntry(histos[cat],str(cat).replace("categoria_",""),"l");
leg.Draw("same")

c1.SetGridx()
c1.SetGridy()
#c1.GetListOfPrimitives()[1].GetYaxis().SetRangeUser(0, 2.)
##c1.GetListOfPrimitives()[1].GetYaxis().SetRangeUser(0, max_*1.1)
c1.Modified()
c1.Update()

c1.SaveAs("vaccini.png")

c1.SetLogy()
c1.SaveAs("vaccini_log.png")

#integral = ROOT.histo.GetIntegral()
#for i in ROOT.histo:
#    ROOT.histo.SetBinContent(i, integral[i])

'''
data_somministrazione,
fornitore,
area,
fascia_anagrafica,
sesso_maschile,
sesso_femminile,
categoria_operatori_sanitari_sociosanitari,
categoria_personale_non_sanitario,
categoria_ospiti_rsa,
categoria_over80,
categoria_forze_armate,
categoria_personale_scolastico,
categoria_altro,
prima_dose,
seconda_dose,
codice_NUTS1,
codice_NUTS2,
codice_regione_ISTAT,
nome_area'''

#FASCIA ANAGRAFICA: [20, 16, 30, 50, 40, 60, 70, 90, 80]

'''
01 PIEMONTE
02 VALLE D'AOSTA
03 LOMBARDIA
04 TRENTINO A. A.
05 VENETO
06 FRIULI V. G
07 LIGURIA
08 EMILIA ROMAGNA
09 TOSCANA
10 UMBRIA
11 MARCHE
12 LAZIO
13 ABRUZZI
14 MOLISE
15 CAMPANIA
16 PUGLIE
17 BASILICATA
18 CALABRIA
19 SICILIA
20 SARDEGNA
'''
