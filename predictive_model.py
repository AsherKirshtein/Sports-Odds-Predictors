import boto3
import pandas as pd
from io import StringIO
import re
import concurrent.futures


this_year = 2024
this_week = 7
# Initialize the S3 client
s3 = boto3.client('s3')

# Specify the bucket name and base prefix
bucket_name = 'sportspredictionbucket'
base_prefix = 'CSV/'

# Function to read CSV file from S3 and return it as a pandas DataFrame
def read_csv_from_s3(bucket, key):
    try:
        s3_object = s3.get_object(Bucket=bucket, Key=key)
        content = s3_object['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(content))
        return df
    except Exception as e:
        print(f"Error reading {key}: {e}")
        return None  

def extract_week_number(key):
    match = re.search(r'_Week_(\d+)\.csv', key)
    if match:
        return int(match.group(1))
    return -1 
     
def get_last_matchups(matchups, Team_1, Team_2):
    found = 0
    current_year = this_year
    last_matches = []
    while found < matchups:
        for year in range(current_year, 1954, -1):  # Range from 2024 to 1955 (step -1)
            prefix = f'{base_prefix}{year}/'
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            # Check if there are files in the folder
            if 'Contents' in response:
                sorted_contents = sorted(
                response['Contents'], 
                key=lambda obj: extract_week_number(obj['Key']),
                reverse=True
                )  
                for obj in sorted_contents:
                    key = obj['Key']
                    if key.endswith('.csv') and 'Week' in key:  # Only process CSV files
                        df = read_csv_from_s3(bucket_name, key)
                        if df is not None:
                            favorites = df['Favorite']
                            under_dogs = df['Underdog']
                            is_fav_home = df['Location']
                            is_underdog_home = df['Opponent']
                            games_this_week = len(favorites)
                            for game in range(0, games_this_week):
                                if is_fav_home[game] == '@':
                                   home = favorites[game]
                                   away = under_dogs[game]
                                elif is_underdog_home[game] == '@':
                                    away = favorites[game]
                                    home = under_dogs[game]
                                else:
                                    away = favorites[game]
                                    home = under_dogs[game]
                                if (Team_1 == home or Team_1 == away) and (Team_2 == home or Team_2 == away):
                                    last_matches.append(df.iloc[game])
                                    found +=1
            if found >= matchups:
                return last_matches
            
def get_last_matches_home_away(matchups, Team_1, Team_2):
    found = 0
    current_year = this_year
    last_matches = []
    while found < matchups:
        for year in range(current_year, 1954, -1):  # Range from 2024 to 1955 (step -1)
            prefix = f'{base_prefix}{year}/'
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            # Check if there are files in the folder
            if 'Contents' in response:
                sorted_contents = sorted(
                response['Contents'], 
                key=lambda obj: extract_week_number(obj['Key']),
                reverse=True
                )  
                for obj in sorted_contents:
                    key = obj['Key']
                    if key.endswith('.csv') and 'Week' in key:  # Only process CSV files
                        df = read_csv_from_s3(bucket_name, key)
                        if df is not None:
                            favorites = df['Favorite']
                            under_dogs = df['Underdog']
                            is_fav_home = df['Location']
                            is_underdog_home = df['Opponent']
                            games_this_week = len(favorites)
                            for game in range(0, games_this_week):
                                if is_fav_home[game] == '@':
                                   home = favorites[game]
                                   away = under_dogs[game]
                                elif is_underdog_home[game] == '@':
                                    away = favorites[game]
                                    home = under_dogs[game]
                                if Team_1 == home  and Team_2 == away:
                                    last_matches.append(df.iloc[game])
                                    found +=1
            if found >= matchups:
                return last_matches
            
def get_Team_Score_by_last_games(games, Team):            
    found = 0
    current_year = this_year
    last_matches = []
    while found < games:
        for year in range(current_year, 1954, -1):  # Range from 2024 to 1955 (step -1)
            prefix = f'{base_prefix}{year}/'
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            # Check if there are files in the folder
            if 'Contents' in response:
                sorted_contents = sorted(
                response['Contents'], 
                key=lambda obj: extract_week_number(obj['Key']),
                reverse=True
                )  
                for obj in sorted_contents:
                    key = obj['Key']
                    if key.endswith('.csv') and 'Week' in key:  # Only process CSV files
                        df = read_csv_from_s3(bucket_name, key)
                        if df is not None:
                            favorites = df['Favorite']
                            under_dogs = df['Underdog']
                            games_this_week = len(favorites)
                            for game in range(0, games_this_week):
                                if Team == favorites[game]  or Team == under_dogs[game]:
                                    last_matches.append(df.iloc[game])
                                    found +=1
            if found >= games:
                return last_matches
            
def get_Team_Score_by_last_home_games(games, Team):
    found = 0
    current_year = this_year
    last_matches = []
    while found < games:
        for year in range(current_year, 1954, -1):  # Range from 2024 to 1955 (step -1)
            prefix = f'{base_prefix}{year}/'
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            # Check if there are files in the folder
            if 'Contents' in response:
                sorted_contents = sorted(
                response['Contents'], 
                key=lambda obj: extract_week_number(obj['Key']),
                reverse=True
                )  
                for obj in sorted_contents:
                    key = obj['Key']
                    if key.endswith('.csv') and 'Week' in key:  # Only process CSV files
                        df = read_csv_from_s3(bucket_name, key)
                        if df is not None:
                            favorites = df['Favorite']
                            under_dogs = df['Underdog']
                            is_fav_home = df['Location']
                            is_underdog_home = df['Opponent']
                            games_this_week = len(favorites)
                            for game in range(0, games_this_week):
                                if is_fav_home[game] == '@':
                                   home = favorites[game]
                                   away = under_dogs[game]
                                elif is_underdog_home[game] == '@':
                                    away = favorites[game]
                                    home = under_dogs[game]
                                if Team == home:
                                    last_matches.append(df.iloc[game])
                                    found +=1
            if found >= games:
                return last_matches
            
def get_Team_Score_by_last_away_games(games, Team):
    found = 0
    current_year = this_year
    last_matches = []
    while found < games:
        for year in range(current_year, 1954, -1):  # Range from 2024 to 1955 (step -1)
            prefix = f'{base_prefix}{year}/'
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
            # Check if there are files in the folder
            if 'Contents' in response:
                sorted_contents = sorted(
                response['Contents'], 
                key=lambda obj: extract_week_number(obj['Key']),
                reverse=True
                )  
                for obj in sorted_contents:
                    key = obj['Key']
                    if key.endswith('.csv') and 'Week' in key:  # Only process CSV files
                        df = read_csv_from_s3(bucket_name, key)
                        if df is not None:
                            favorites = df['Favorite']
                            under_dogs = df['Underdog']
                            is_fav_home = df['Location']
                            is_underdog_home = df['Opponent']
                            games_this_week = len(favorites)
                            for game in range(0, games_this_week):
                                if is_fav_home[game] == '@':
                                   home = favorites[game]
                                   away = under_dogs[game]
                                elif is_underdog_home[game] == '@':
                                    away = favorites[game]
                                    home = under_dogs[game]
                                if Team == away:
                                    last_matches.append(df.iloc[game])
                                    found +=1
            if found >= games:
                return last_matches
           
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

def predict(Team_1, Team_2):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Start the operations in parallel
        future_last_5_matchups = executor.submit(get_last_matchups, 5, Team_1, Team_2)
        future_last_10_matchups = executor.submit(get_last_matchups, 10, Team_1, Team_2)
        future_last_5_matchups_H_A = executor.submit(get_last_matches_home_away, 5, Team_1, Team_2)
        future_last_10_matchups_H_A = executor.submit(get_last_matches_home_away, 10, Team_1, Team_2)
        future_last_5_games_T1 = executor.submit(get_Team_Score_by_last_games, 5, Team_1)
        future_last_5_games_T2 = executor.submit(get_Team_Score_by_last_games, 5, Team_2)
        future_last_10_games_T1 = executor.submit(get_Team_Score_by_last_games, 10, Team_1)
        future_last_10_games_T2 = executor.submit(get_Team_Score_by_last_games, 10, Team_2)
        future_last_20_games_T1 = executor.submit(get_Team_Score_by_last_games, 20, Team_1)
        future_last_20_games_T2 = executor.submit(get_Team_Score_by_last_games, 20, Team_2)

        # Retrieve the results once they are done
        last_5_matchups = future_last_5_matchups.result()
        last_10_matchups = future_last_10_matchups.result()
        last_5_matchups_H_A = future_last_5_matchups_H_A.result()
        last_10_matchups_H_A = future_last_10_matchups_H_A.result()
        last_5_games_T1 = future_last_5_games_T1.result()
        last_5_games_T2 = future_last_5_games_T2.result()
        last_10_games_T1 = future_last_10_games_T1.result()
        last_10_games_T2 = future_last_10_games_T2.result()
        last_20_games_T1 = future_last_20_games_T1.result()
        last_20_games_T2 = future_last_20_games_T2.result()
    
    print(last_10_matchups)
    
    
    


                     
#get_last_matchups(5, nfl_teams[15], nfl_teams[27])
#get_Team_Score_by_last_games(5, nfl_teams[27])
#get_Team_Score_by_last_home_games(5, nfl_teams[27])
#get_Team_Score_by_last_away_games(5, nfl_teams[27])

predict(nfl_teams[15], nfl_teams[27])