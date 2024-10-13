import csv
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import accuracy_score, mean_squared_error
import numpy as np
from tqdm import tqdm
import urllib.parse

from pymongo import MongoClient
from dotenv import load_dotenv

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
            return matchups
    return matchups

def check_Current_Season(team_1, team_2):
    current_year = 2024
    current_week = 3
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
    current_week = 3
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

def get_individual_opponent_points(last_games, team):
    team_scores = []
    for game in last_games:
        fav_team = game[4]
        points = game[5].split()[1]
        fav_team_pts = points.split('-')[0]
        underDog_pts = points.split('-')[1]
        if int(underDog_pts) < 0:
                underDog_pts = 0
        if int(fav_team_pts) < 0:
                fav_team_pts = 0
        if team == fav_team:
            team_scores.append(underDog_pts)
        else:
            team_scores.append(fav_team_pts)
    return team_scores[::-1]


def get_Last_Home_games(team, amount_getting):
    current_year = 2024
    current_week = 5
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
    current_week = 5
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

def predict_super_bowl():
    Teams_and_victories = []
    for Team in nfl_teams:
        Teams_and_victories.append([Team, 0, 0])
    directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{2024}'
    csv_filename = os.path.join(directory_path, f'{2024}_Schedule.csv')
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row.__contains__('Home_Team'):
                continue
            team1 = row[1]
            team2 = row[2]
            t1_index = nfl_teams.index(team1)
            t2_index = nfl_teams.index(team2)
            prediction = predict_game(team1, team2)
            try:
                if prediction[2][0] > prediction[2][1]:
                    Teams_and_victories[t1_index][1] += 1
                    Teams_and_victories[t2_index][2] += 1
                else:
                    Teams_and_victories[t1_index][2] += 1
                    Teams_and_victories[t2_index][1] += 1
            except:
                print(team1, team2, 'Need to fix team name change issue')
            
    print(Teams_and_victories)
    
    
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

def get_actual_scores(week):
    directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{2024}'
    csv_filename = os.path.join(directory_path, f'{2024}_Week_{week}.csv')
    actual_scores = []
    with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == 'Day':
                continue
            home_attribute = row[4]
            if home_attribute == '@':
                home = row[4]
                away = row[8]
                score = row[5].lstrip('W').lstrip('L')
                home_pts = score.split('-')[0]
                away_pts = score.split('-')[1].replace('(OT)', '').strip()
            else:
                home = row[8]
                away = row[4]
                score = row[5].lstrip('W').lstrip('L')
                home_pts = score.split('-')[1].replace('(OT)', '').strip()
                away_pts = score.split('-')[0]
                
            fin_score = [int(home_pts),int(away_pts)]
            actual_scores.append([home,away, fin_score])
    return actual_scores
                
                
def predict_by_week(week):
    directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{2024}'
    csv_filename = os.path.join(directory_path, f'{2024}_Schedule.csv')
    predictions = []
    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[0] == str(week):
                predictions.append(predict_game(row[1],row[2]))
    return predictions

def check_winners():
    wins_right = 0
    home_margin = 0
    away_margin = 0
    season_games = 0
    for week_to_predict in range(1,5):
        predicted_games = predict_by_week(week_to_predict)
        actual_games = get_actual_scores(week_to_predict)
        predicted = [normalize_matchup(game) for game in predicted_games]
        actual = [normalize_matchup(game) for game in actual_games]
        actual_games_dict = {tuple(sorted([game[0], game[1]])): game[2] for game in actual}
        # Align matchups
        aligned_games = []
        for predicted_game in predicted:
            teams = tuple(sorted([predicted_game[0], predicted_game[1]]))
            if teams in actual_games_dict:
                aligned_games.append((predicted_game[0], predicted_game[1], predicted_game[2], actual_games_dict[teams]))

        # Print the aligned matchups with predicted and actual scores
        for game in aligned_games:
            predicted_score = game[2]
            actual_score = game[3]
            season_games += 1
            if predicted_score[0] > predicted_score[1] and actual_score[0] > actual_score[1]:
                wins_right +=1
            elif predicted_score[1] > predicted_score[0] and actual_score[1] > actual_score[0]:
                wins_right +=1

            home_margin += predicted_score[0] - actual_score[0]
            away_margin += predicted_score[1] - actual_score[1]
        
    print('Predicted games:' , wins_right, 'out of', season_games, 'Accuracy: ', (wins_right/season_games), '%')
    print("Avg Home Team Margin of error: ", (home_margin/season_games), "points")
    print("Avg Away Team Margin of error: ", (away_margin/season_games), "points")
    
def check_vs_spread():            
    games_played = 0
    s_right = 0
    o_right = 0
    for week_to_predict in range(1,5):
        directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{2024}'
        csv_filename = os.path.join(directory_path, f'{2024}_Week_{week_to_predict}.csv')
        with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] == 'Day':
                    continue
                games_played +=1
                home_attribute = row[3]
                home_team = ''
                away_team = ''
                home_is_fav = True
                if home_attribute == '@':
                    home_team = row[4]
                    away_team = row[8]
                else:
                    home_team = row[8]
                    away_team = row[4]
                    home_is_fav = False
                
                prediction = predict_game(home_team,away_team)
                if not home_is_fav:
                    prediction[2] = prediction[2][::-1] #flip the score
                    prediction = prediction[::-1] #flip teams
                    temp = prediction[0]
                    prediction.remove(temp)
                    prediction.append(temp)  
                spread = prediction[2][0] - prediction[2][1]
                if int(spread) > abs(float(row[6].split()[1].lstrip('-'))):
                    if row[6].split()[0] == 'W':
                        s_right += 1
                else:
                    if row[6].split()[0] == 'L':
                        s_right += 1
                
                predicted_total = prediction[2][0] + prediction[2][1]
                Over_or_Under ,Actual_total = row[9].split()
                if Over_or_Under == 'O' and predicted_total > float(Actual_total):
                    o_right +=1
                elif Over_or_Under == 'U' and predicted_total < float(Actual_total):
                    o_right +=1
    
    print('Spread Accuracy: ', s_right, 'Out of ', games_played, ': ' ,((s_right/games_played)*100), '%' )
    print('Over Accuracy: ', o_right, 'Out of ', games_played, ': ' ,((o_right/games_played)*100), '%' )
        
def normalize_matchup(game):
    team1, team2, score = game
    if team1 > team2:
        return [team2, team1, score[::-1]]  # Reverse score if teams are reversed
    return game           

def predict_game(Team_1, Team_2):
        factors = []  
        matches = getLastMatchups(10, Team_1, Team_2)[::-1]
        last_5 = getLastMatchups(5, Team_1, Team_2)[::-1]

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

        T1_opponent_pts_last_10 = get_individual_opponent_points(Team_1_last_10, Team_1)
        T2_opponent_pts_last_10 = get_individual_opponent_points(Team_2_last_10, Team_2)
        T1_opponent_pts_last_5 = get_individual_opponent_points(Team_1_last_5, Team_1)
        T2_opponent_pts_last_5 = get_individual_opponent_points(Team_2_last_5, Team_2)

        opponent_pts_last_10_predicted = predict_Score(T2_opponent_pts_last_10, T1_opponent_pts_last_10)
        opponent_pts_last_5_predicted = predict_Score(T2_opponent_pts_last_5, T1_opponent_pts_last_5)


        factors.append(opponent_pts_last_10_predicted) #last 10 scores of the opposing team factor 7
        factors.append(opponent_pts_last_5_predicted) #last 5 scores of the opposing team factor 8

        T1_Home_opponent_pts_last_10 = get_individual_opponent_points(Team_1_last_home_10, Team_1)
        T2_Away_opponent_pts_last_10 = get_individual_opponent_points(Team_2_last_away_10, Team_2)
        T1_Home_opponent_pts_last_5 = get_individual_opponent_points(Team_1_last_home_5, Team_1)
        T2_Away_opponent_pts_last_5 = get_individual_opponent_points(Team_2_last_away_5, Team_2)

        opponent_Home_pts_last_10_predicted = predict_Score(T2_Away_opponent_pts_last_10, T1_Home_opponent_pts_last_10)
        opponent_Home_pts_last_5_predicted = predict_Score(T2_Away_opponent_pts_last_5, T1_Home_opponent_pts_last_5)

        factors.append(opponent_Home_pts_last_10_predicted) #last 10 scores of the opposing team factor 9
        factors.append(opponent_Home_pts_last_5_predicted) #last 5 scores of the opposing team factor 10

        fin_score = get_Avg_of_factors(factors)

        #print(Team_1, fin_score[0])
        #print(Team_2, fin_score[1])
        
        return [Team_1, Team_2, [fin_score[0], fin_score[1]]]


#week_to_predict = 1
#prediction = predict_game(nfl_teams[31], nfl_teams[2])
#print(prediction)
#predict_super_bowl()
check_winners()
check_vs_spread()
