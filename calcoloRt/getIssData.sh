rm -rf curva_epidemica_Italia_ufficiale
curl -LO  --ciphers 'DEFAULT:!DH'   https://www.epicentro.iss.it/coronavirus/open-data/calcolo_rt_italia.zip
unzip calcolo_rt_italia.zip
cp calcolo_Rt_Italia/curva_epidemica_Italia_20* curva_epidemica_Italia_ufficiale.Rdata
rm -rf calcolo_rt_italia.zip calcolo_Rt_Italia

rm covid_19-iss.xlsx
curl -LO  --ciphers 'DEFAULT:!DH'  https://www.epicentro.iss.it/coronavirus/open-data/covid_19-iss.xlsx

for SHEET in "casi_inizio_sintomi_sint" "casi_inizio_sintomi" "casi_prelievo_diagnosi" "decessi"
do
    rm -f aa.csv.0 $SHEET.csv $SHEET.R
    ssconvert -S -O "sheet=$SHEET"   covid_19-iss.xlsx   aa.csv
    mv aa.csv.0 $SHEET.csv
    ./convertCSVtoR.py $SHEET.csv
done

