import os
import csv
from tqdm import tqdm
from datetime import datetime

def get_game_location(row_info):
    if(row_info[3] == "Location"):
        return "NaN", "NaN" 
    elif row_info[3] == "@":
        location = row_info[4]
        location = location.split(" ", 3)[:-1]
        if len(location) > 1:
            location = location[0]+ location[1]
        elif len(location) == 1:
            location = location[0]
        date = datetime.strptime(row_info[1], "%b %d, %Y")
        hour, minute = map(int, row_info[2].split(":"))
        if hour < 12:  # Assuming all given times are PM
            hour += 12 
        date = date.replace(hour=hour, minute=minute) 
        return location, date
    else:
        location = row_info[8]
        location = location.split(" ", 3)[:-1]
        if len(location) > 1:
            location = location[0]+ location[1]
        elif len(location) == 1:
            location = location[0]
        date = datetime.strptime(row_info[1], "%b %d, %Y")
        hour, minute = map(int, row_info[2].split(":"))
        if hour < 12:  # Assuming all given times are PM
            hour += 12 
        date=date.replace(hour=hour, minute=minute)
        return location, date
         

def get_Games(condition):
    
    for year in tqdm(range(1990, 2025), desc=f'Getting {condition} games', unit="year"):
        directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{year}'
        current_week=1
        if year > 2021:
            current_week = 18
        elif year == 1987:
            current_week = 16
        elif year == 1982:
                current_week = 10
        elif year > 1977:
                current_week = 17
        else:
                current_week = 15
        while current_week > 0:
            file = directory_path + f'/{year}_Week_{current_week}.csv'
            current_week -= 1
            with open(file, "r", encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    location, date = get_game_location(row)
                    if location == "NaN":
                        continue
                    else: 
                        print(location, date)
        


get_Games("k")