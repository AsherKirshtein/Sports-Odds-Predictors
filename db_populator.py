import os
import csv
from datetime import datetime
from tqdm import tqdm
import psycopg2


def get_playoff_location(row):
    if row[4] == "@":
        loc = row[5].split(" ", 3)[:-1]
    else:
        loc = row[9].split(" ", 3)[:-1] 
    if len(loc) > 2:
        return loc[0]+loc[1]
    else:
        return loc[0]
    
def get_location(row):
    if row[3] == "@":
        loc = row[4].split(" ", 3)[:-1]
    else:
        loc = row[8].split(" ", 3)[:-1] 
    if len(loc) > 1:
        return loc[0]+loc[1]
    else:
        return loc[0]
   
   
def extract_scores(score_str):
    """
    Extracts numeric scores from a formatted score string like 'L 24-27' or 'W 28-21'.
    Returns (favorite_score, underdog_score) as integers.
    """
    try:
        score_str = score_str.replace("W", "").replace("L", "").strip()  # Remove W/L indicators
        favorite_score, underdog_score = map(int, score_str.split("-"))  # Extract numeric scores
        return favorite_score, underdog_score
    except ValueError:
        print(f"Warning: Invalid score format '{score_str}'. Defaulting to (0, 0)")
        return 0, 0  # Default if parsing fails
   

def convert_spread(spread_value, favorite_score, underdog_score):
    """
    Cleans the spread and determines if the favorite covered it.
    - Removes 'W' or 'L' from spread.
    - Converts 'PK' (Pick'em) to 0.0.
    - Compares scores to determine if the favorite covered.
    """
    try:
        # Remove 'W' or 'L' from spread value
        spread_value = spread_value.replace("W", "").replace("L", "").strip()

        # Convert 'PK' to 0.0, otherwise cast to float
        cleaned_spread = 0.0 if "PK" in spread_value else float(spread_value)

        # Determine if the spread hit
        margin = favorite_score - underdog_score  # Calculate point difference
        if margin > cleaned_spread:
            spread_result = "Win"  # Favorite covered
        elif margin == cleaned_spread:
            spread_result = "Push"  # Exactly on the spread
        else:
            spread_result = "Loss"  # Favorite did not cover

        return cleaned_spread, spread_result

    except ValueError:
        print(f"Warning: Invalid spread value '{spread_value}'. Defaulting to 0.0")
        return 0.0, "Unknown"
    
    
def safe_float(value, default=0.0):
    """Convert value to float safely, returning default if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        print(f"Warning: Invalid numeric value '{value}', defaulting to {default}")
        return default
    
 
def populate_weather(): 
    directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/Weather_Data/'
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)  # Get full path
        if os.path.isfile(file_path):  # Check if it's a file (not a folder)
            print(filename)
            
def populate_db():
    conn = psycopg2.connect(
    dbname="nfl_db",
    user="postgres",
    password="password",
    host="localhost"
    )
    cur = conn.cursor()
    for year in tqdm(range(1985, 2025), desc="Populating Database", unit="year"):
        directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{year}'
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)  # Get full path
            if os.path.isfile(file_path):  # Check if it's a file (not a folder)
                if file_path.__contains__("Schedule") or file_path.__contains__("Total"):
                    continue
                print(file_path)
                with open(file_path, "r", encoding="utf-8", newline="") as f:
                            w_reader = csv.reader(f)
                            if file_path.__contains__("Playoffs"):
                                for line in w_reader:
                                    if line[0] == "Round" or line[0] == "Day":
                                        continue
                                    round_name = line[0]
                                    date = line[2]
                                    day = line[1]
                                    time = datetime.strptime(line[3] + " PM", "%I:%M %p").strftime("%H:%M")
                                    location = get_playoff_location(line)
                                    favorite = line[5]
                                    score = line[6]
                                    favorite_score, underdog_score = extract_scores(score)
                                    spread, spread_result = convert_spread(line[7], favorite_score, underdog_score)
                                    underdog = line[9]
                                    if line[10] != "":
                                        over_under = line[10].split(" ")[1]
                                    spread = safe_float(spread)
                                    over_under = safe_float(over_under)
                                    cur.execute("""
                                        INSERT INTO playoff_games (round, game_date, day, game_time, location, favorite, score, spread, spread_result, underdog, over_under)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (round_name, date, day, time, location, favorite, score, float(spread), spread_result, underdog, float(over_under)))

                            else:
                                for line in w_reader:
                                    if line[0] == "Day":
                                        continue
                                    date = line[1]
                                    day = line[0]
                                    time = datetime.strptime(line[2] + " PM", "%I:%M %p").strftime("%H:%M")
                                    location = get_location(line)
                                    favorite = line[4]
                                    score = line[5]
                                    favorite_score, underdog_score = extract_scores(score)
                                    spread, spread_result = convert_spread(line[6], favorite_score, underdog_score)
                                    underdog = line[8]
                                    if line[9] != "":
                                        over_under = line[9].split(" ")[1]
                                    spread = safe_float(spread)
                                    over_under = safe_float(over_under)
                                    cur.execute("""
                                        INSERT INTO nfl_games (game_date, day, game_time, location, favorite, score, spread, spread_result, underdog, over_under)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (date, day, time, location, favorite, score, float(spread), spread_result, underdog, float(over_under)))
    conn.commit()
    cur.close()
    conn.close()
                                
                                
                                
populate_weather()