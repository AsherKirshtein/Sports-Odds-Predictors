import csv
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error
import numpy as np


def combine_record(record):
    # Split the record by space to separate the prefix from the numbers
    parts = record.split()
    score = parts[1]
    num1_str, num2_str = score.split('-')
    return (int(num1_str) + int(num2_str))

def get_Team_Usuals(amount, Team_1, Team_2):
    if amount < 7.5:
        file = '/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/AllTime/By_Team_Total_Last_5.csv'
    elif amount < 15:
        file = '/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/AllTime/By_Team_Total_Last_10.csv'
    elif amount < 35:
        file = '/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/AllTime/By_Team_Total_Last_25.csv'
    else:
        file = '/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/AllTime/By_Team_Total_All_Time.csv'
    
    with open(file, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                parts = [] 
                for row in reader:    
                    if row[0] == Team_1:
                        parts.append(f"{Team_1} Over Record vs All Teams: {row[9]}")
                    if row[0] == Team_2:
                        parts.append(f"{Team_2} Over Record vs All Teams: {row[9]}")
                        
    summary = "\n".join(parts)
    return summary


def getLastMatchups(amount, team_1, team_2):
    found = 0
    current_year = 2023
    current_week = 18
    matchups = check_Current_Season(team_1,team_2)
    amount -= len(matchups)
    while found < amount:
        try:
            directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{current_year}'
            csv_filename = os.path.join(directory_path, f'{current_year}_Week_{current_week}.csv')
            with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    favorite = row[4]
                    underdog = row[8]
                    if (favorite == team_1 or favorite == team_2) and (underdog == team_1 or underdog == team_2):
                        matchups.append(row)
                        found+=1
                        
            current_week-=1
            if current_week == 0:
                current_year -=1
                if current_year > 2021:
                    current_week = 18
                elif current_year == 1987:
                    current_week = 16
                elif current_year == 1982:
                    current_week = 10
                elif current_year > 1977:
                    current_week = 17
                else:
                    current_week = 15
        except:
            print("No more matchups availible")
            return matchups
    return matchups

def check_Current_Season(team_1, team_2):
    current_year = 2024
    current_week = 2
    matchups = []
    while current_week > 0:
        directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{current_year}'
        csv_filename = os.path.join(directory_path, f'{current_year}_Week_{current_week}.csv')
        with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                favorite = row[4]
                underdog = row[8]
                if (favorite == team_1 or favorite == team_2) and (underdog == team_1 or underdog == team_2):
                    matchups.append(row)
        current_week-=1
    return matchups

def get_Team_Points_by_matchup(team_1, team_2, matches):
    team1_scores = []
    team2_scores = []
    for game in matches:
        fav_team = game[4]
        points = game[5].split()[1]
        fav_team_pts = points.split('-')[0]
        underDog_pts = points.split('-')[1]
        if team_1 == fav_team:
            team1_scores.append(fav_team_pts)
            team2_scores.append(underDog_pts)
        else:
            team2_scores.append(fav_team_pts)
            team1_scores.append(underDog_pts)
    return team1_scores, team2_scores
            
        
def predict_Score(team_1_scores, team_2_scores):
    team_1_scores = list(map(int, team_1_scores))
    team_2_scores = list(map(int, team_2_scores))
    X = np.arange(1, len(team_1_scores) + 1).reshape(-1, 1)  # Just using game number for simplicity

    # Separate models for predicting each team's scores
    team_1_model = LinearRegression()
    team_2_model = LinearRegression()

    # Fit the models with the game numbers (X) and the respective team scores
    team_1_model.fit(X, team_1_scores)
    team_2_model.fit(X, team_2_scores)

    # Predict the next game number (next game is len(X) + 1)
    next_game = np.array([[len(X) + 1]])

    team_1_predicted_score = team_1_model.predict(next_game)
    team_2_predicted_score = team_2_model.predict(next_game)

    return team_1_predicted_score, team_2_predicted_score

def get_Team_Score_by_last_games(amount_getting, team):
    current_year = 2024
    current_week = 2
    found = 0
    games = []
    while found < amount_getting:
        try:
            directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{current_year}'
            csv_filename = os.path.join(directory_path, f'{current_year}_Week_{current_week}.csv')
            with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    favorite = row[4]
                    underdog = row[8]
                    if favorite == team or underdog == team:
                        games.append(row)
                        found += 1
                        
            current_week-=1
            if current_week == 0:
                current_year -=1
                if current_year > 2021:
                    current_week = 18
                elif current_year == 1987:
                    current_week = 16
                elif current_year == 1982:
                    current_week = 10
                elif current_year > 1977:
                    current_week = 17
                else:
                    current_week = 15
        except:
            print("No more games")
    return games

def get_individual_team_points(last_games, team):
    team_scores = []
    for game in last_games:
        fav_team = game[4]
        points = game[5].split()[1]
        fav_team_pts = points.split('-')[0]
        underDog_pts = points.split('-')[1]
        if team == fav_team:
            team_scores.append(fav_team_pts)
        else:
            team_scores.append(underDog_pts)
    return team_scores


def get_Last_Home_games(team, amount_getting):
    current_year = 2024
    current_week = 2
    found = 0
    games = []
    while found < amount_getting:
        try:
            directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{current_year}'
            csv_filename = os.path.join(directory_path, f'{current_year}_Week_{current_week}.csv')
            with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    favorite = row[4]
                    favorite_home_attribute = row[3]
                    underdog = row[8]
                    underdog_home_attribute = row[7]
                    if (favorite == team and favorite_home_attribute == '@') or (underdog == team and underdog_home_attribute == '@'):
                        games.append(row)
                        found += 1
                        
            current_week-=1
            if current_week == 0:
                current_year -=1
                if current_year > 2021:
                    current_week = 18
                elif current_year == 1987:
                    current_week = 16
                elif current_year == 1982:
                    current_week = 10
                elif current_year > 1977:
                    current_week = 17
                else:
                    current_week = 15
        except:
            print("No more games")
    return games
            
def get_Last_Away_games(team, amount_getting):
    current_year = 2024
    current_week = 2
    found = 0
    games = []
    while found < amount_getting:
        try:
            directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{current_year}'
            csv_filename = os.path.join(directory_path, f'{current_year}_Week_{current_week}.csv')
            with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    favorite = row[4]
                    favorite_home_attribute = row[3]
                    underdog = row[8]
                    underdog_home_attribute = row[7]
                    if (favorite == team and favorite_home_attribute == '') or (underdog == team and underdog_home_attribute == ''):
                        games.append(row)
                        found += 1
                        
            current_week-=1
            if current_week == 0:
                current_year -=1
                if current_year > 2021:
                    current_week = 18
                elif current_year == 1987:
                    current_week = 16
                elif current_year == 1982:
                    current_week = 10
                elif current_year > 1977:
                    current_week = 17
                else:
                    current_week = 15
        except:
            print("No more games")
    return games

def get_Avg_of_factors(factors):
    T1p = 0
    T2p = 0
    for factor in factors:
        T1p += factor[0]
        T2p += factor[1]
    T1_pred = T1p/len(factors)
    T2_pred = T2p/len(factors)
    
    return round(T1_pred[0]), round(T2_pred[0])

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
    "Las Vegas Raiders", #16
    "Los Angeles Chargers", #17
    "Los Angeles Rams", #18
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

factors = []

Team_1 = nfl_teams[0] # assume team_1 is home team
Team_2 =  nfl_teams[10]     
matches = getLastMatchups(10, Team_1, Team_2)
last_5 = getLastMatchups(5, Team_1, Team_2)
columns = ['Day','Date','Time(ET)','Location','Favorite','Score','Spread','Opponent','Underdog','Over/Under','Additional Notes']

last_5pts_by_team = get_Team_Points_by_matchup(Team_1, Team_2, last_5)
points_by_team = get_Team_Points_by_matchup(Team_1, Team_2, matches)

predicted_score_by_matchup = predict_Score(points_by_team[0], points_by_team[1])
predicted_score_by_matchup_last_5 = predict_Score(last_5pts_by_team[0], last_5pts_by_team[1])
factors.append(predicted_score_by_matchup_last_5)
#Predicted score by matchup in last 5 games on each teams last matchups against each other factor 1
factors.append(predicted_score_by_matchup)
#Predicted score by matchup in lased 10 games based on each teams last matchups against each other factor 2

Team_1_last_10 = get_Team_Score_by_last_games(10, Team_1)
Team_2_last_10 = get_Team_Score_by_last_games(10, Team_2)
Team_1pts_last_10 = get_individual_team_points(Team_1_last_10, Team_1)
Team_2pts_last_10 = get_individual_team_points(Team_2_last_10, Team_2)

predicted_score_by_last_10_games = predict_Score(Team_1pts_last_10, Team_2pts_last_10) 
#predicted score by last 10 games factor 3

Team_1_last_5 = get_Team_Score_by_last_games(5, Team_1)
Team_2_last_5 = get_Team_Score_by_last_games(5, Team_2)
Team_1pts_last_5 = get_individual_team_points(Team_1_last_5, Team_1)
Team_2pts_last_5 = get_individual_team_points(Team_2_last_5, Team_2)

predicted_score_by_last_5_games = predict_Score(Team_1pts_last_5, Team_2pts_last_5) 
#predicted score by last 5 games factor 4

factors.append(predicted_score_by_last_10_games)
factors.append(predicted_score_by_last_5_games)

Team_1_last_home_5 = get_Last_Home_games(Team_1, 5)
Team_1_last_home_10 = get_Last_Home_games(Team_1,10)
Team_2_last_away_5 = get_Last_Away_games(Team_2,5)
Team_2_last_away_10 = get_Last_Away_games(Team_2,10)

T1_home_last_5_pts = get_individual_team_points(Team_1_last_home_5, Team_1)
T1_home_last_10_pts = get_individual_team_points(Team_1_last_home_10, Team_1)
T2_away_last_5_pts = get_individual_team_points(Team_2_last_away_5, Team_2)
T2_away_last_10_pts = get_individual_team_points(Team_2_last_away_10, Team_2)

predicted_score_by_last_5_home_games = predict_Score(T1_home_last_5_pts, T2_away_last_5_pts)
predicted_score_by_last_10_home_games = predict_Score(T1_home_last_10_pts, T2_away_last_10_pts)

factors.append(predicted_score_by_last_10_home_games) #last 10 home/away games factor 5
factors.append(predicted_score_by_last_5_home_games) #last 5 home/away games factor 6

fin_score = get_Avg_of_factors(factors)

print(Team_1, fin_score[0])
print(Team_2, fin_score[1])
