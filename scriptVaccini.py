import ROOT,csv
from datetime import date

anagraficaFileName ="dataVaccini/dati/anagrafica-vaccini-summary-latest.csv"
consegneFileName ="dataVaccini/dati/consegne-vaccini-latest.csv"
somministrazioniFileName = "dataVaccini/dati/somministrazioni-vaccini-latest.csv"

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

anagrafica = getAnagrafica("dataVaccini/dati/anagrafica-vaccini-summary-latest.csv")
consegneROOTFileName = consegneFileName.replace(".csv",".root")
somministrazioniROOTFileName = somministrazioniFileName.replace(".csv",".root")
updateROOTfile(somministrazioniFileName, somministrazioniROOTFileName)
updateROOTfile(consegneFileName, consegneROOTFileName)

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

selection = "(fornitore==-1) * (fascia_anagrafica==90)"
#selection = "(fornitore==-1) * (codice_regione_ISTAT==7)"
c1 = ROOT.TCanvas("c1")
somministrazioniTree.Draw("data_somministrazione >> histo","1. * %s * (prima_dose+seconda_dose)"%selection,"HIST")
histo = ROOT.histo.GetCumulative()
#consegneTree.Draw("data_consegna >> histo2","1. * %s * (numero_dosi)"%selection,"HIST")
#histo2 = ROOT.histo2.GetCumulative()
#histo2.Draw("HIST")
histo.Draw("HIST,SAME")

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
