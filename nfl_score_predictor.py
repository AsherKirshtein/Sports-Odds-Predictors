import psycopg2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

# Database connection setup
DB_CONFIG = {
    "dbname": "nfl_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost"
}

def get_last_away_game_scores(team_name, amount):
    """Fetch the last 10 home game outcomes with team and opponent scores."""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    location = team_name.split(" ", 3)[:-1]
    if len(location) > 1:
        location = location[0] + location[1]
    else:
        location = location[0]
    cur.execute("""
        SELECT 
            game_date, 
            CASE 
                WHEN favorite = %s THEN underdog 
                ELSE favorite 
            END AS opponent, 
            score
        FROM nfl_games
        WHERE location != %s  -- Ensure it's an away game
        AND (favorite = %s OR underdog = %s)  -- Ensure team played
        ORDER BY game_date DESC
        LIMIT %s;
    """, (team_name, location, team_name, team_name, amount))

    games = cur.fetchall()
    
    cur.close()
    conn.close()

    # Process score to extract team and opponent scores
    formatted_games = []
    for game in games:
        game_date, opponent, score = game
        score = score.lstrip("W")
        score = score.lstrip("L")
        score = score.lstrip("T")
        score = score.strip("(OT)")
        # Extract team and opponent scores from the "score" field
        try:
            team_score, opponent_score = map(int, score.split('-'))  
        except ValueError:
            team_score, opponent_score = None, None  # Handle cases where the score isn't in "XX-XX" format
        
        formatted_games.append({
            "date": game_date,
            "opponent": opponent,
            "team_score": team_score,
            "opponent_score": opponent_score
        })

    return formatted_games

def get_last_home_game_scores(team_name, amount):
    """Fetch the last 10 home game outcomes with team and opponent scores."""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    location = team_name.split(" ", 3)[:-1]
    if len(location) > 1:
        location = location[0] + location[1]
    else:
        location = location[0]
        
    cur.execute("""
        SELECT 
            game_date, 
            CASE 
                WHEN favorite = %s THEN underdog 
                ELSE favorite 
            END AS opponent, 
            score
        FROM nfl_games
        WHERE location = %s  -- Ensure team played at home
        ORDER BY game_date DESC
        LIMIT %s;
    """, (team_name, location, amount))

    games = cur.fetchall()
    
    cur.close()
    conn.close()

    # Process score to extract team and opponent scores
    formatted_games = []
    for game in games:
        game_date, opponent, score = game
        score = score.lstrip("W")
        score = score.lstrip("L")
        score = score.lstrip("T")
        score = score.strip("(OT)")
        # Extract team and opponent scores from the "score" field
        try:
            team_score, opponent_score = map(int, score.split('-'))  
        except ValueError:
            team_score, opponent_score = None, None  # Handle cases where the score isn't in "XX-XX" format
        
        formatted_games.append({
            "date": game_date,
            "opponent": opponent,
            "team_score": team_score,
            "opponent_score": opponent_score
        })

    return formatted_games

def get_last_matchups(team1, team2, amount):
    """Fetch the last `amount` matchups between two teams."""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Query to fetch last matchups
    cur.execute("""
        SELECT 
            game_date, 
            score, 
            location,
            favorite
        FROM nfl_games
        WHERE 
            (favorite = %s AND underdog = %s) OR 
            (favorite = %s AND underdog = %s)
        ORDER BY game_date DESC
        LIMIT %s;
    """, (team1, team2, team2, team1, amount))

    games = cur.fetchall()
    
    cur.close()
    conn.close()
    formatted_games = []
    for game in games:
        game_date, score, location, favorite = game
        score = score.lstrip("W")
        score = score.lstrip("L")
        score = score.lstrip("T")
        score = score.strip("(OT)")
        try:
            team_score, opponent_score = map(int, score.split('-'))  
        except ValueError:
            team_score, opponent_score = None, None  # Handle cases where the score isn't in "XX-XX" format
        
        
        if favorite != team1:
            opponent_score, team_score = map(int, score.split('-'))
        
        formatted_games.append({
            "date": game_date,
            "opponent": team2,
            "team_score": team_score,
            "opponent_score": opponent_score
        })
    return formatted_games

def get_last_game_scores(team_name, amount):
    """Fetch the last 10 game outcomes with team and opponent scores."""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Fetch the last 10 games, extracting scores correctly
    cur.execute("""
        SELECT 
            game_date, 
            CASE 
                WHEN favorite = %s THEN underdog 
                ELSE favorite 
            END AS opponent, 
            score
        FROM nfl_games
        WHERE favorite = %s OR underdog = %s
        ORDER BY game_date DESC
        LIMIT %s;
    """, (team_name, team_name, team_name, amount,))

    games = cur.fetchall()
    
    cur.close()
    conn.close()

    # Process score to extract team and opponent scores
    formatted_games = []
    for game in games:
        game_date, opponent, score = game
        score = score.lstrip("W")
        score = score.lstrip("L")
        score = score.lstrip("T")
        score = score.strip("(OT)")
        # Extract team and opponent scores from the "score" field
        try:
            team_score, opponent_score = map(int, score.split('-'))  
        except ValueError:
            team_score, opponent_score = None, None  # Handle cases where the score isn't in "XX-XX" format
        
        formatted_games.append({
            "date": game_date,
            "opponent": opponent,
            "team_score": team_score,
            "opponent_score": opponent_score
        })

    return formatted_games

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

NFC_WEST = [ "Arizona Cardinals", "San Francisco 49ers", "Seattle Seahawks", "Los Angeles Rams"]
NFC_EAST = [ "New York Giants", "Philadelphia Eagles", "Washington Commanders", "Dallas Cowboys"]
NFC_SOUTH = [ "Tampa Bay Buccaneers", "New Orleans Saints", "Carolina Panthers", "Atlanta Falcons"]
NFC_NORTH = [ "Chicago Bears", "Detroit Lions", "Minnesota Vikings", "Green Bay Packers"]

AFC_NORTH = [ "Baltimore Ravens", "Pittsburgh Steelers",  "Cincinnati Bengals", "Cleveland Browns"]
AFC_EAST = [ "Buffalo Bills", "Miami Dolphins", "New York Jets", "New England Patriots"]
AFC_SOUTH = [ "Houston Texans", "Indianapolis Colts", "Jacksonville Jaguars", "Tennessee Titans"]
AFC_WEST = [ "Kansas City Chiefs", "Los Angeles Chargers", "Denver Broncos",  "Las Vegas Raiders"]

def divisional_rivals(t1,t2):
    if NFC_EAST.__contains__(t1) and NFC_EAST.__contains__(t2):
        return True
    if NFC_WEST.__contains__(t1) and NFC_WEST.__contains__(t2):
        return True
    if NFC_SOUTH.__contains__(t1) and NFC_SOUTH.__contains__(t2):
        return True
    if NFC_NORTH.__contains__(t1) and NFC_NORTH.__contains__(t2):
        return True
    if AFC_EAST.__contains__(t1) and AFC_EAST.__contains__(t2):
        return True
    if AFC_WEST.__contains__(t1) and AFC_WEST.__contains__(t2):
        return True
    if AFC_SOUTH.__contains__(t1) and AFC_SOUTH.__contains__(t2):
        return True
    if AFC_NORTH.__contains__(t1) and AFC_NORTH.__contains__(t2):
        return True
    return False
    
def predict(games):
    df = pd.DataFrame(games)

    # ✅ Assign each game a sequential game index (instead of using dates)
    df['game_index'] = np.arange(len(df))

    # Define Features (X) and Target (y) for team score and opponent score
    X = df[['game_index']]  # ✅ Use game index instead of date
    y_team = df['team_score']  # Team's score
    y_opponent = df['opponent_score']  # Opponent's score

    # ✅ Apply Min-Max Scaling to the `game_index` feature
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # Train separate linear regression models for team and opponent scores
    model_team = LinearRegression()
    model_opponent = LinearRegression()

    model_team.fit(X_scaled, y_team)
    model_opponent.fit(X_scaled, y_opponent)

    # ✅ Predict next game's score based on game index (not date)
    next_game_index = len(df)  # Next game is sequentially the next one
    next_game_scaled = scaler.transform(pd.DataFrame([[next_game_index]], columns=['game_index']))  # ✅ Fixed

    predicted_team_score = model_team.predict(next_game_scaled)[0]
    predicted_opponent_score = model_opponent.predict(next_game_scaled)[0]

    return predicted_team_score, predicted_opponent_score

def predict_rivals(team_1, team_2):
    team_1_last_games = predict(get_last_game_scores(team_1, 10))
    team_2_last_games = predict(get_last_game_scores(team_2, 10))
    team_1_last_home_games = predict(get_last_home_game_scores(team_1, 10))
    team_2_last_away_games = predict(get_last_away_game_scores(team_2, 10))
    matchups = predict(get_last_matchups(team_1, team_2, 10))
    
    team_1_avg = ((matchups[0]*2) + team_1_last_games[0] + team_1_last_home_games[0] + team_2_last_games[1] + team_2_last_away_games[1])//6
    team_2_avg = ((matchups[1]*2) + team_1_last_games[1] + team_1_last_home_games[1] + team_2_last_games[0] + team_2_last_away_games[0])//6
    
    return team_1_avg, team_2_avg
    
def predict_score(team_1, team_2):
    
    if divisional_rivals(team_1, team_2):
        return predict_rivals(team_1,team_2)
    
    team_1_last_games = predict(get_last_game_scores(team_1, 10))
    team_2_last_games = predict(get_last_game_scores(team_2, 10))
    team_1_last_home_games = predict(get_last_home_game_scores(team_1, 10))
    team_2_last_away_games = predict(get_last_away_game_scores(team_2, 10))
    
    
    team_1_avg = (team_1_last_games[0] + team_1_last_home_games[0] + team_2_last_games[1] + team_2_last_away_games[1])//4
    team_2_avg = (team_1_last_games[1] + team_1_last_home_games[1] + team_2_last_games[0] + team_2_last_away_games[0])//4
    
    return team_1_avg, team_2_avg


def power_rank():
    victories = {}
    for filler in range(0, 32):
        victories[nfl_teams[filler]] = 0
        
    for t1 in range(0, 32):
        for t2 in range(0, 32):
            if t2 == t1:
                continue
            team_1 = nfl_teams[t1]
            team_2 = nfl_teams[t2]
            
            t1_score, t2_score = predict_score(team_1, team_2)
            if t1_score > t2_score:
                victories[nfl_teams[t1]] += 1
            else:
                victories[nfl_teams[t2]] += 1
    

    
            
        
power_rank()