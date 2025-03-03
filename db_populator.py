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
        if "(OT)" in score_str:
            score_str = score_str.replace("(OT)", "").strip()
        favorite_score, underdog_score = map(int, score_str.split("-"))  # Extract numeric scores
        return favorite_score, underdog_score
    except ValueError:
        #print(f"Warning: Invalid score format '{score_str}'. Defaulting to (0, 0)")
        return 0, 0  # Default if parsing fails
   

def convert_spread(spread_value):
    """
    Uses the existing 'W' or 'L' in the spread value to determine the spread result.
    - Extracts 'W' or 'L' to set 'Win' or 'Loss'.
    - Removes the 'W' or 'L' before converting the spread to a float.
    - Converts 'PK' (Pick'em) to 0.0.
    """
    try:
        spread_result = "Unknown"

        # Check if spread_value contains 'W' or 'L' at the beginning
        if spread_value.startswith("W"):
            spread_result = "Win"
        elif spread_value.startswith("L"):
            spread_result = "Loss"
        else:
            spread_result = "Push"

        # Remove 'W' or 'L' and clean the value
        cleaned_spread = spread_value.replace("W", "").replace("L", "").strip()

        # Convert 'PK' (Pick'em) to 0.0, otherwise convert to float
        cleaned_spread = 0.0 if "PK" in cleaned_spread else float(cleaned_spread)

        return cleaned_spread, spread_result

    except ValueError:
        #print(f"Warning: Invalid spread value '{spread_value}'. Defaulting to 0.0")
        return 0.0, "Push"

    
    
def safe_float(value, default=0.0):
    """Convert value to float safely, returning default if conversion fails."""
    try:
        return float(value)
    except (ValueError, TypeError):
        #print(f"Warning: Invalid numeric value '{value}', defaulting to {default}")
        return default
    
    
    
def clean_numeric(value):
    try:
        return float(value.split(" ")[0])  # Extracts only the number part
    except (ValueError, IndexError):
        return None  # Returns None if conversion fail
    
def populate_weather():
    conn = psycopg2.connect(
    dbname="nfl_db",
    user="postgres",
    password="password",
    host="localhost"
    )
    cur = conn.cursor() 
    directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/Weather_Data/'
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)  # Get full path
        if os.path.isfile(file_path):  # Check if it's a file (not a folder)
            print(filename)
            with open(file_path, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                for line in reader:
                    if line[0] == 'Date':
                        continue
                    else:
                        weather_date = line[0]
                        weather_time = line[1]
                        temperature = clean_numeric(line[2])
                        dew_point = clean_numeric(line[3])
                        humidity = clean_numeric(line[4])
                        wind_direction = line[5]  # Keep as string (e.g., 'NE')
                        wind_speed = clean_numeric(line[6])
                        wind_gust = clean_numeric(line[7])
                        pressure = clean_numeric(line[8])
                        precipitation = clean_numeric(line[9])
                        condition = line[10]  # Weather condition (e.g., "Cloudy")

                        # Insert into database
                        cur.execute("""
                            INSERT INTO weather_data (weather_date, weather_time, temperature, dew_point, humidity, wind_direction, wind_speed, wind_gust, pressure, precipitation, condition)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (weather_date, weather_time, temperature, dew_point, humidity, wind_direction, wind_speed, wind_gust, pressure, precipitation, condition))
    conn.commit()
    cur.close()
    conn.close()
   
def get_over_under_result(over_under):
    try:
        indicator = str(over_under)[0].upper()  # Convert to uppercase to avoid case issues
        if indicator == 'O':
            return "Over"
        elif indicator == 'U':
            return "Under"
        else:
            return "Push"  # In case of unexpected input
    except (TypeError, IndexError):
        
        return "Unknown"  # Handles cases where input is None or too short
            
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
                                    spread, spread_result = convert_spread(line[7])
                                    underdog = line[9]
                                    if line[10] != "":
                                        over_under = line[10].split(" ")[1]
                                    spread = safe_float(spread)
                                    over_under_result = get_over_under_result(line[10])
                                    over_under = safe_float(over_under)
                                    cur.execute("""
                                        INSERT INTO playoff_games (round, game_date, day, game_time, location, favorite, score, spread, spread_result, underdog, over_under, over_under_result)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (round_name, date, day, time, location, favorite, score, float(spread), spread_result, underdog, float(over_under), over_under_result))

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
                                    spread, spread_result = convert_spread(line[6])
                                    underdog = line[8]
                                    if line[9] != "":
                                        over_under = line[9].split(" ")[1]
                                    spread = safe_float(spread)
                                    over_under_result = get_over_under_result(line[9])
                                    over_under = safe_float(over_under)
                                    cur.execute("""
                                        INSERT INTO nfl_games (game_date, day, game_time, location, favorite, score, spread, spread_result, underdog, over_under, over_under_result)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """, (date, day, time, location, favorite, score, float(spread), spread_result, underdog, float(over_under), over_under_result))
    conn.commit()
    cur.close()
    conn.close()
                                
