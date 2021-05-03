#python2 script.py >& logWorld &
cd calcoloRt && (./getIssData.sh >& logRt) &
sleep 3
python2 scriptItalyISS.py >& logISS &
python2 scriptItaly.py >& logItaly &
python2 scriptVaccini.py >& logVaccini &
cd calcoloRt && (Rscript calcoloRt_EpiEstim.R >& logRt2) &
