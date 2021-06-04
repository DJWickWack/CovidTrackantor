taskkill /fi "WINDOWTITLE eq record - Excel" /f
echo.

@echo off
set PATH=%PATH%;C:\Users\19105\Documents\COVID-19 Tracking\CovidTrackantor\
cd C:\Users\19105\Documents\COVID-19 Tracking\CovidTrackantor\
git stash
echo.
git pull

python CovidFiller.py
echo.

@echo off
cls
:start
echo.
echo 1. Record
echo 2. Restart
echo 3. Exit
echo.
echo.
echo.
set /p x=Pick:
IF '%x%' == '%x%' GOTO Item_%x%

:Item_1
start "C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE" "C:\Users\19105\Documents\COVID-19 Tracking\CovidTrackantor\record.csv"
exit

:Item_2
python CovidFiller.py
GOTO Start

:Item_3
exit