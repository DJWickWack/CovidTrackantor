@echo off
set PATH=%PATH%;C:\Users\19105\Documents\COVID-19 Tracking\CovidTrackantor\
cd C:\Users\19105\Documents\COVID-19 Tracking\CovidTrackantor\
git pull

python CovidFiller.py

start "C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE" "C:\Users\19105\Documents\COVID-19 Tracking\CovidTrackantor\record.csv"