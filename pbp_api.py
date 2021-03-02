import pandas as pd
import requests
import re
import os

class PBPStatsAPI:

    def __init__(self, URL, YEAR_FROM=None, YEAR_TO=None):
        self.url = URL
        self.year_from = YEAR_FROM
        self.year_to = YEAR_TO

    #extract json from the given url
    def extract_data(self):
        json = requests.get(self.url).json()
        rows = json['multi_row_table_data']
        headers = self.extract_headers(json)
        df = pd.DataFrame(rows, columns = headers)
        return df
    
    def extract_data_multiple_seasons(self):
        years = range(self.year_from, self.year_to + 1)
        seasons = ["{0}-{1}".format(int(years[i]) - 1, str(years[i])[-2:]) for i in range(len(years))]
        df = pd.DataFrame()
        for season in seasons:
            #tune url
            self.url = re.sub('(?<=Season=)(.*)(?=&SeasonType)', str(season), self.url)
            df_i = self.extract_data()
            df_i['season'] = season
            df = pd.concat([df, df_i], axis = 0)
            print(season)
        return df
    
    def extract_headers(self, json):
        headers = []
        for header in json['multi_row_table_headers']:
            for subheader in json['multi_row_table_headers'][header]:
                headers.append(subheader['field'])
        return headers.sort()

if __name__ == '__main__':
    
    df = PBPStatsAPI('https://api.pbpstats.com/get-totals/nba?Season=2020-21&SeasonType=Regular%2BSeason&Type=Player', 2014, 2021).extract_data_multiple_seasons()
    
    os.chdir('..')
    df.to_csv('./data/pbp_totals.csv', index = False)
    
