from __future__ import print_function
import pandas as pd
import datetime
import time
import re
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.client import SignedJwtAssertionCredentials
import json

global compareday
compareday= datetime.datetime.today()
global data

SCOPE = ["https://spreadsheets.google.com/feeds"]
SECRETS_FILE = "covidtrackerkey.json"
SPREADSHEET = "Health Screen - Microspec (Responses)"
json_key = json.load(open(SECRETS_FILE))
# Authenticate using the signed key
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
credentials = Credentials.from_service_account_file(
    'covidtrackerkey.json',
    scopes=scopes
)
gc = gspread.authorize(credentials)
workbook = gc.open(SPREADSHEET)
sheet = workbook.sheet1
data = pd.DataFrame(sheet.get_all_records())
data = data.set_index("Timestamp")
data.index = pd.to_datetime(data.index)

record=pd.read_csv('record.csv',index_col=0)
yes=None
no=None
atten=None

def checkday(data,date):
    
    yesframe=pd.DataFrame(columns=['First Name','Last Name'])
    noframe=pd.DataFrame(columns=['First Name','Last Name'])
    attendanceframe=pd.DataFrame(columns=['First Name','Last Name'])

    for x in data.index:
        day = datetime.datetime(x.year,x.month,x.day)
        mdate= datetime.datetime(date.year, date.month, date.day)
        if (day== mdate):
            temp = {'First Name': data['First Name'][x], "Last Name":data['Last Name'][x]}
            attendanceframe= attendanceframe.append(temp,ignore_index=True)
            try:
                if(data['I am participating in Microspec’s required COVID-19 Daily Safety Screening program. If any, or all, of my symptoms are consistent with cold, flu, respiratory or gastrointestinal illness (the markers of COVID-19), I agree to contact my physician for follow up and report the results to Human Resource. The responsibility for follow up is mine alone and not those associated with this screening. I hereby release Microspec Corporation ("Microspec" or the “Company") and each of its employees and agents from any liability arising from, or in any way connected with, this screening and disclosure form to the fullest extent permitted by applicable law.'][x]!="I Accept" or
                data['Answer this question only on the first day of your work week. If this is a Monday, was your temperature taken over the weekend on Saturday and Sunday 100° or higher?'][x]=='Yes' or
                data['Do you have a persistent cough?'][x]=='Yes'or
                data['Do you have shortness of breath?'][x]=='Yes'or
                data['In the last 24 hours, have you experienced any of the following symptoms: • Chills/shaking with chills • Loss of taste or smell • Muscle pain • Headache • Sore throat • Intestinal distress with vomiting or diarrhea • Nausea • Fever • Cough • Difficulty breathing • Stuffy nose • Congestion?'][x]=='Yes'or
                data['In the last 24 hours: • Have you taken a fever reducer (such as Tylenol or Advil) to relieve a fever of 100° or higher? • Have you taken a cough suppressant to relieve a dry cough?'][x]=='Yes'or
                data["In the last 7 days, have you, or someone in your household: • Visited inside your home or someone else's home with anyone outside of your household? • Attended an inside or outside public gathering?"][x]=='Yes'or
                data["In the last 7 days, have you, or someone in your household traveled outside of New England or traveled anywhere by air?"][x]=='Yes'or
                data["In the last 14 days, have you had contact with someone who has tested positive for COVID-19?"][x]=='Yes'):
                    yesframe= yesframe.append(temp, ignore_index=True)
                else:
                    noframe= noframe.append(temp, ignore_index=True)
            except ValueError:
                temp = {'First Name': data['First Name'][x], "Last Name":data['Last Name'][x]}
                print("At "+str(x))
                print(temp['First Name']+" "+temp['Last Name']+" has somehow filledout the form incorrectly")
    return(attendanceframe,yesframe,noframe)

def DNC(attendanceframe,MasterList):
    for x in attendanceframe.index:
        name=str(attendanceframe["First Name"][x])+" "+str(attendanceframe["Last Name"][x])
        name= re.sub(r"\s+", "", name)
        name= name.upper()
        for y in MasterList.index:
            mname=str(MasterList["First Name"][y])+" "+str(MasterList["Last Name"][y])
            mname= re.sub(r"\s+", "", mname)
            mname= mname.upper()
            if(mname=="BRUCECRAIG"):
                MasterList=MasterList.drop(y)
            if(mname==name):            
                MasterList=MasterList.drop(y)
                break
    return(MasterList)

def Fillsheet (yesframe,noframe,MasterList,record,date):
    colname=str(date.month)+"/"+str(date.day)+"/"+str(date.year)
    nonearr=[]
    for x in record.index:
        nonearr.append(None)
    record[colname]=nonearr
    for x in yesframe.index:
        i=re.sub(r"\s+", "", yesframe["First Name"][x])+" "+re.sub(r"\s+", "", yesframe["Last Name"][x])
        i=i.lower()
        i=i.title()
        record[colname][i]="FOLLOW UP"
    for x in noframe.index:
        i=re.sub(r"\s+", "", noframe["First Name"][x])+" "+re.sub(r"\s+", "", noframe["Last Name"][x])
        i=i.lower()
        i=i.title()
        record[colname][i]="all set"
    for x in MasterList.index:
        i=re.sub(r"\s+", "", MasterList["First Name"][x])+" "+re.sub(r"\s+", "", MasterList["Last Name"][x])
        i=i.lower()
        i=i.title()
        record[colname][i]="DID NOT COMPLETE"
    arrr=[]
    for x in record.index:
        arrr.append(record[colname][x])
    record[colname]=arrr
    record.to_csv(r'record.csv', index = True, header=True)

def weekcycle(date,data):
    MasterList=pd.read_csv('MasterList.csv')
    if(date.day==datetime.datetime.today().day):
        print("Writting to record date: ", date )
        atten,yes,no=checkday(data,date)
        MasterList=DNC(atten, MasterList)
        Fillsheet(yes, no, MasterList, record,date)
    else:
        print("Writting to record date: ", date )
        atten,yes,no=checkday(data,date)
        MasterList=DNC(atten, MasterList)
        Fillsheet(yes, no, MasterList, record,date)
        date+=datetime.timedelta(days=1)
        weekcycle(date,data)

def dayprint(date,data):
        MasterList=pd.read_csv('MasterList.csv')
        atten,yes,no=checkday(data,date)
        MasterList=DNC(atten, MasterList)
        Fillsheet(yes, no, MasterList, record,date)
        print("-"*7)
        print("data recorded in record.csv")
        print("-"*7)
        print("people that need to be followed up it with:")
        for x in yes.index:
            print("   * "+yes["First Name"][x]+" "+yes["Last Name"][x])
        print("people who have not completed the form:")
        for x in MasterList.index:
            print("   * "+MasterList["First Name"][x]+" "+MasterList["Last Name"][x])


print("Welcome to the auto Covid Tracker Fillanator")
print("What would you like to do?")
print("1. Check todays date")
print("2. Check yesterday")
print("3. Check certain date")
print("4. Run tracker for past week")
print("5 Do today and yesterday")
num = input("Choice[5] ")
if(num==''):
    
    today=compareday
    compareday-= datetime.timedelta(days=1)
    compareday= datetime.datetime(compareday.year, compareday.month, compareday.day)
    print("-*-"*7)
    print("YESTERDAY   "+str(compareday.month)+"-"+str(compareday.day))
    print("-*-"*7)
    dayprint(compareday,data)

    compareday= datetime.datetime(today.year, today.month, today.day)
    print("-*-"*7)
    print("TODAY   "+str(compareday.month)+"-"+str(compareday.day))
    print("-*-"*7)  
    dayprint(compareday,data)
    
    pp=input("Press any key to exit")
    exit()
else:
    num=int(num)

if(num==1):
    compareday= datetime.datetime(compareday.year, compareday.month, compareday.day)
    atten,yes,no=checkday(data,compareday)
if(num==2):
    compareday-= datetime.timedelta(days=1)
    compareday= datetime.datetime(compareday.year, compareday.month, compareday.day)
    atten,yes,no=checkday(data,compareday)
if(num==3):
    newdate=input("Enter date MM/DD/YYYY: ")
    compareday= datetime.datetime.strptime(newdate, '%m/%d/%Y')
    atten,yes,no=checkday(data,compareday)
if(num==4):
    compareday-= datetime.timedelta(days=7)
    compareday= datetime.datetime(compareday.year, compareday.month, compareday.day)
    weekcycle(compareday, data)
    print("Past week has been recorded")
    time.sleep(3)
    exit()
if(num==5):

    today=compareday
    compareday-= datetime.timedelta(days=1)
    compareday= datetime.datetime(compareday.year, compareday.month, compareday.day)
    print("-*-"*7)
    print("YESTERDAY   "+str(compareday.month)+"-"+str(compareday.day))
    print("-*-"*7)
    dayprint(compareday,data)

    compareday= datetime.datetime(today.year, today.month, today.day)
    print("-*-"*7)
    print("TODAY   "+str(compareday.month)+"-"+str(compareday.day))
    print("-*-"*7)  
    dayprint(compareday,data)
    
    pp=input("Press any key to exit")
    exit()
    
else:
    print ("number entered is not a vaild number")
MasterList=pd.read_csv('MasterList.csv')
MasterList=DNC(atten, MasterList)
Fillsheet(yes, no, MasterList, record,compareday)
print("-"*7)
print("data recorded in record.csv")
print("-"*7)
print("people that need to be followed up it with:")
for x in yes.index:
    print("   * "+yes["First Name"][x]+" "+yes["Last Name"][x])
print("people who have not completed the form:")
for x in MasterList.index:
    print("   * "+MasterList["First Name"][x]+" "+MasterList["Last Name"][x])
pp=input("Press any key to exit")









