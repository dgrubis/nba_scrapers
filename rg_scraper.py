import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

class RGScraper:

    ''' This class can be used for the real gm players page to grab demographics and YOS '''

    def __init__(self, YEAR_FROM, YEAR_TO):
        self.year_from = YEAR_FROM
        self.year_to = YEAR_TO

    def get_table_soup(self, url):
        #extract url
        page = requests.get(url)
        #extract html soup
        soup = BeautifulSoup(page.content, 'html.parser')
        #get the table we want from RG
        table = soup.find('table', attrs = {"class" : 'tablesaw'})
        return table

    def get_table_headers(self, table):
        #get table headers
        headers = []
        #loop over each header and add the text to an array
        for header in table.find('thead').find('tr').find_all('th'):
            headers.append(header.text.replace('\n', '').strip())
        #remove empty strings and rank field
        #headers = [x for x in headers if x and x != 'Rk']
        return headers

    def get_table_data(self, table):
        #get data
        rows = []
        #extract all row tags
        table_rows = table.find('tbody').find_all('tr')
        for tr in table_rows:
            row = []
            #each field resides in a td tag
            for td in tr.find_all('td'):
                row.append(td.text)
            #remove empty strings
            #row = [x for x in row if x]
            #collect all player rows
            rows.append(row)
        return rows
    
    def build_df(self):
        #specify the intended range to grab data
        years = range(self.year_from, self.year_to + 1)
        #need to attach the season in format '2020-21' to the actual data retuend
        seasons = ["{0}-{1}".format(int(years[i]) - 1, str(years[i])[-2:]) for i in range(len(years))]
        df = pd.DataFrame()
        for year, season in zip(years, seasons):
            #build url
            url_year_i = 'https://basketball.realgm.com/nba/players/' + str(year)
            #get the table soup for current year
            table_year_i = self.get_table_soup(url_year_i)
            #get the headers and the rows for current year
            headers_year_i = self.get_table_headers(table_year_i)
            rows_year_i = self.get_table_data(table_year_i)
            #build df for current year
            df_year_i = pd.DataFrame(rows_year_i, columns = headers_year_i)
            df_year_i['season'] = season
            #attach the season of data to the complete dataframe
            df = pd.concat([df, df_year_i], axis = 0)
            print(season)
        return df

if __name__ == '__main__':
    #use the method 'build_df' to get the corresponding data you requested back into a pandas dataframe
    df = RGScraper(1980, 2021).build_df()

    #move up one level to where I want data placed
    os.chdir('..')

    df.to_csv('./data/rg_yos.csv', index = False)

