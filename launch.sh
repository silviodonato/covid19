#python2 script.py >& logWorld &
python2 scriptItaly.py >& logItaly &
python2 scriptVaccini.py >& logVaccini &
cd calcoloRt && (./getIssData.sh >& logRt) && (Rscript calcoloRt_EpiEstim.R >& logRt2) &
