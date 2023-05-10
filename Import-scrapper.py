import pandas as pd
from bs4 import BeautifulSoup
import requests
import calendar

####### Global vars ###########

url = "https://tradestat.commerce.gov.in/meidb/brc.asp?ie=i"
databaseFile = "data.csv"
unprocessedData = []

###############################


# Set the year range for data
yearBegin = 2022
yearEnd = 2022

# Set the month range for data
coverAllMonths = True
monthBegin = 1
monthEnd = 10

#Set Principal Commodity code
principalCommodityCode = 1


for year in range(yearBegin,yearEnd+1):
    unprocessedData = []
    if coverAllMonths:
        monthBegin = 1
        monthEnd = 12

    collectedMonthlyData = []
    for month in range(monthBegin,monthEnd+1):
        print("Month: " + str(month) + "/" + str(year))
        form_data = {"radioFY": 1,"Mm1":month,"yy1":year,"brcCode":principalCommodityCode,"sort":0,"radioD100":1,"radioval":1}
        server = requests.post(url,data=form_data,verify=False)
        output = server.text
        soup = BeautifulSoup(output,'html.parser')

        table = soup.find('table')
        split_table = str(table).split("<tr>")

        monthlyData = []
        for i in range(2,len(split_table)-1):
            data = split_table[i]
            data = data.replace(" ","")
            data = data.replace("\n","")
            data = data.replace("\r","")
            data = data.replace("\xa0","0")
            
            split_data = data.split('<fontsize="2">')[1:]
            rowData = []
            for i in split_data:
                rowData.append(i.split("</font>")[0])

            # monthlyData.append(rowData)
            print(rowData)
        print()
        print()
        
