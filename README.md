Get repository

```
git clone git@github.com:silviodonato/covid19.git
cd covid19
```

Get dataWorld

```
git clone git@github.com:CSSEGISandData/COVID-19.git dataWorld
```

Get dataItaly

```
git clone git@github.com:pcm-dpc/COVID-19.git dataItaly
```

Get dataISTAT

```
wget "https://www.istat.it/it/files//2020/03/Dataset-decessi-comunali-giornalieri-e-tracciato-record_al30giugno.zip"
unzip -d dataISTAT Dataset-decessi-comunali-giornalieri-e-tracciato-record_al30giugno.zip 
rm Dataset-decessi-comunali-giornalieri-e-tracciato-record_al30giugno.zip
```

Get dataVaccini

```
git clone git@github.com:italia/covid19-opendata-vaccini.git dataVaccini

```

Run scripts

```
python script.py
python scriptDatiIstat.py
python scriptItaly.py
```

Check the results

```
ls plots
ls plotsItalia
ls *csv
```

#############################################

Update data

```
cd dataItaly
git pull origin master
cd .. 
```

```
cd dataWorld
git pull origin master
cd ..                           
```

```
cd dataVaccini
git pull origin master
cd ..
```


