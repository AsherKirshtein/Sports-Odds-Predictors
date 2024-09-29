import requests
from lxml import etree
from bs4 import BeautifulSoup
import os
import csv

nfl_teams = [
    "Arizona Cardinals", #0
    "Atlanta Falcons", #1
    "Baltimore Ravens", #2
    "Buffalo Bills", #3
    "Carolina Panthers", #4
    "Chicago Bears", #5
    "Cincinnati Bengals", #6
    "Cleveland Browns", #7
    "Dallas Cowboys", #8
    "Denver Broncos", #9
    "Detroit Lions", #10
    "Green Bay Packers", #11
    "Houston Texans", #12
    "Indianapolis Colts", #13
    "Jacksonville Jaguars", #14
    "Kansas City Chiefs", #15
    "Los Angeles Chargers", #16
    "Los Angeles Rams", #17
    "Las Vegas Raiders", #18
    "Miami Dolphins", #19
    "Minnesota Vikings", #20
    "New England Patriots", #21
    "New Orleans Saints", #22
    "New York Giants", #23
    "New York Jets", #24
    "Philadelphia Eagles", #25
    "Pittsburgh Steelers", #26
    "San Francisco 49ers", #27
    "Seattle Seahawks", #28
    "Tampa Bay Buccaneers", #29
    "Tennessee Titans", #30
    "Washington Commanders" #31
]

nfl_abbreviations = [
    'ARI', #0
    'ATL', #1
    'BAL', #2
    'BUF', #3
    'CAR', #4
    'CHI', #5
    'CIN', #6
    'CLE', #7
    'DAL', #8
    'DEN', #9
    'DET', #10
    'GB', #11
    'HOU', #12
    'IND', #13
    'JAC', #14
    'KC', #15
    'LAC', #16
    'LAR', #17
    'LV', #18
    'MIA', #19
    'MIN', #20
    'NE', #21
    'NO', #22
    'NYG', #23
    'NYJ', #24
    'PHI', #25
    'PIT', #26
    'SF', #27
    'SEA', #28
    'TB', #29
    'TEN', #30
    'WSH' #31
]

def getSchedule():
    url = 'https://www.footballguys.com/schedule-grid'
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        dom = etree.HTML(str(soup))

        # Iterate over the rows (e.g., tr[2], tr[3], etc.)
        team_matchups = []
        for row in range(2, 34):  # Adjust range for the number of rows you want
            # Iterate over columns (e.g., td[2], td[3], etc.)
            team_1_matchups = []
            for col in range(2, 20):  # Adjust range for the number of columns you want
                xpath_query = f'/html/body/main/section/div/div/table/tbody/tr[{row}]/td[{col}]'
                element = dom.xpath(xpath_query)
                if element:
                    team_1_matchups.append(element[0].text)
            team_matchups.append(team_1_matchups)
        matches = convert_Matches(team_matchups)
        schedule = get_games_by_week(matches)
        make_CSV(schedule)

def make_CSV(schedule):
    directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{2024}'
    csv_filename = os.path.join(directory_path, f'{2024}_Schedule.csv')
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerow(['Week','Home_Team', 'Away_Team'])
                for week in range(0,18):
                    schedule[week]
                    for game in schedule[week]:
                        if game[1] != 'BYE':
                            csvwriter.writerow([(week+1),game[0].lstrip('@'),game[1]])
                    
    

def get_games_by_week(matches):
    schedule = []
    for week in range(0, 18):
        week_x = []
        for team in range(0, 32):
            # Check if the match is an away game
            if matches[team][week].startswith('@'):
                away_team = nfl_teams[team]  # Current team is away
                home_team = matches[team][week].lstrip('@')  # Remove '@' from the home team
            else:
                home_team = nfl_teams[team]  # Current team is home
                away_team = matches[team][week]  # The opponent is the away team
            
            # Avoid reversed duplicates by sorting teams
            
            matchup = [home_team, away_team]
            print(matchup)
            print(team)
            if sorted(matchup) not in [sorted(x) for x in week_x]:
                week_x.append(matchup)
        
        schedule.append(week_x)

    return schedule
    
        
def convert_Matches(matchups):
    whole_scedule = []
    for schedule in matchups:
        games = []
        for opponent in schedule:
            opponent = opponent.rstrip('*').rstrip('+').rstrip('^')
            if opponent.startswith('@'):
                opponent = opponent.lstrip('@')
                index = nfl_abbreviations.index(opponent)
                opponent = ('@' + nfl_teams[index])
                games.append(opponent)
            elif opponent == 'BYE':
                 games.append(opponent)
            else:
                index = nfl_abbreviations.index(opponent)
                opponent = nfl_teams[index]
                games.append(opponent)
        whole_scedule.append(games)
    return whole_scedule
        
getSchedule()