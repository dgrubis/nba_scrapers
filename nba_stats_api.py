import pandas as pd
import requests
import re
import os

class NBAStatsAPI:

    def __init__(self, URL, YEAR_FROM=None, YEAR_TO=None):
        self.url = URL
        self.year_from = YEAR_FROM
        self.year_to = YEAR_TO
        #define header data for extracting json through an API endpoint
        self.header_data  = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'x-nba-stats-token': 'true',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
            'x-nba-stats-origin': 'stats',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Referer': 'https://stats.nba.com/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    #extract json from the given url
    def extract_data(self):
        r = requests.get(self.url, headers= self.header_data)
        resp = r.json()
        results = resp['resultSets'][0]
        headers = results['headers']
        rows = results['rowSet']
        frame = pd.DataFrame(rows, columns = headers)
        return frame
    
    def extract_data_multiple_seasons(self):
        years = range(self.year_from, self.year_to + 1)
        seasons = ["{0}-{1}".format(int(years[i]) - 1, str(years[i])[-2:]) for i in range(len(years))]
        df = pd.DataFrame()
        for season in seasons:
            #tune url
            self.url = re.sub('(?<=Season=)(.*)(?=&SeasonSegment)', str(season), self.url)
            df_i = self.extract_data()
            df_i['season'] = season
            df = pd.concat([df, df_i], axis = 0)
        return df

if __name__ == '__main__':

    df_passing = NBAStatsAPI('https://stats.nba.com/stats/leaguedashptstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PerMode=Totals&PlayerExperience=&PlayerOrTeam=Player&PlayerPosition=&PtMeasureType=Passing&Season=2020-21&SeasonSegment=&SeasonType=Regular+Season&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight=', 2014, 2021).extract_data_multiple_seasons()
    
    df_two_to_six = NBAStatsAPI('https://stats.nba.com/stats/leaguedashplayerptshot?CloseDefDistRange=&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2020-21&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=Touch+2-6+Seconds&VsConference=&VsDivision=&Weight=', 2014, 2021).extract_data_multiple_seasons()
    df_six_plus = NBAStatsAPI('https://stats.nba.com/stats/leaguedashplayerptshot?CloseDefDistRange=&College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&DribbleRange=&GameScope=&GameSegment=&GeneralRange=&Height=&LastNGames=0&LeagueID=00&Location=&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=Totals&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2020-21&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&ShotDistRange=&StarterBench=&TeamID=0&TouchTimeRange=Touch+6%2B+Seconds&VsConference=&VsDivision=&Weight=', 2014, 2021).extract_data_multiple_seasons()

    df_self_creation = pd.concat([df_two_to_six, df_six_plus], axis = 0).groupby(['PLAYER_NAME', 'season'])[['FGM', 'FGA', 'FG2M', 'FG2A', 'FG3M', 'FG3A']].sum().reset_index()
    #calculate shooting percentages
    df_self_creation['FG_PER'] = df_self_creation['FGM'] / df_self_creation['FGA']
    df_self_creation['FG2_PER'] = df_self_creation['FG2M'] / df_self_creation['FG2A']
    df_self_creation['FG3_PER'] = df_self_creation['FG3M'] / df_self_creation['FG3A']
    df_self_creation['eFG_PER'] = (df_self_creation['FGM'] + 0.5 * df_self_creation['FG3M']) / df_self_creation['FGA']
    
    os.chdir('..')
    df_passing.to_csv('./data/nba_stats_tracking_passing.csv', index = False)
    df_self_creation.to_csv('./data/nba_stats_shot_creation.csv', index = False)
