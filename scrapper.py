import pandas as pd
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

# Constants
URL = "https://tradestat.commerce.gov.in/meidb/brc.asp?ie=i"
DATABASE_FILE = "data.csv"

# set the year range for data
START_YEAR = 2020
END_YEAR = 2022

# set the month range for data
START_MONTH = 1
END_MONTH = 12

# set principal commodity code
PRINCIPAL_COMMODITY_CODE = 1

# clean the data
def cleanData(data: str) -> list:
    """Cleans the data by removing unnecessary characters and splitting the data into a list
    
    Arguments:
        data {string} -- data to be cleaned

    Returns:
        list -- cleaned data
    """
    data = data.replace(" ","")
    data = data.replace("\n","")
    data = data.replace("\r","")
    data = data.replace("\xa0","0")
    return data.split('<fontsize="2">')[1:]

def fetchTable(year: int, month: int) -> str:
    """Fetches the table from the URL using requests and BeautifulSoup

    Arguments:
        year {int} -- year of the data
        month {int} -- month of the data

    Returns:
        string -- table data
    """
    form_data = {"radioFY": 1,"Mm1":month,"yy1":year,"brcCode":PRINCIPAL_COMMODITY_CODE,"sort":0,"radioD100":1,"radioval":1}
    server = requests.post(URL,data=form_data,verify=False)
    output = server.text
    soup = BeautifulSoup(output,'html.parser')

    table = soup.find('table')
    return str(table).split("<tr>")

def getTableData(year: int, month: int) -> pd.DataFrame:
    """Gets the table data as a dataframe

    Arguments:
        year {int} -- year of the data
        month {int} -- month of the data

    Returns:
        dataframe -- table data
    """
    table = fetchTable(year,month)

    monthlyData = []
    for i in range(2,len(table)-1):
        data = cleanData(table[i])

        rowData = []
        for i in data:
            rowData.append(i.split("</font>")[0])

        monthlyData.append(rowData)
    return pd.DataFrame(monthlyData, columns=['id', 'HSCode', 'Commodity', 'Val1', 'Val2', 'Val3', 'Val4', 'Val5', 'Val6'])

def formatData(year: int, month: int, data_df: pd.DataFrame, formatted_df: pd.DataFrame) -> pd.DataFrame:
    """Formats the data into a dataframe

    Arguments:
        year {int} -- year of the data
        month {int} -- month of the data
        data_df {dataframe} -- dataframe of the data
        formatted_df {dataframe} -- formatted dataframe

    Returns:
        dataframe -- formatted dataframe
    """
    if data_df.empty:
        return formatted_df
    if formatted_df.empty :
        formatted_df = data_df[['HSCode', 'Commodity', 'Val6']].copy()
        # convert the Val6 column from string to float format
        formatted_df['Val6'] = formatted_df['Val6'].str.replace(',', '')
        formatted_df['Val6'] = formatted_df['Val6'].astype(float)
        formatted_df.rename(columns={'Val6': str(year) + '-' + str(month)}, inplace=True)
    else:
        # conver the Val6 column to float format
        data_df['Val6'] = data_df['Val6'].str.replace(',', '')
        data_df['Val6'] = data_df['Val6'].astype(float)
        formatted_df[str(year) + '-' + str(month)] = data_df['Val6'].copy()
    return formatted_df


def main():
    # get data for each month in the year range
    year_tqdm = tqdm(range(START_YEAR,END_YEAR+1))
    formatted_df = pd.DataFrame()
    for year in year_tqdm:
        for month in range(START_MONTH,END_MONTH+1):
            year_tqdm.set_description("Processing year: " + str(year) + " month: " + str(month))
            data_df = getTableData(year,month)
            formatted_df = formatData(year, month, data_df, formatted_df)

    # save the data to a csv file
    formatted_df.to_csv(DATABASE_FILE)

if __name__ == "__main__":
    main()
