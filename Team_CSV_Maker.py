import csv
from tqdm import tqdm
import re
from collections import defaultdict
import os

def get_records_for_year(year):
    directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{year}'
    file_path = f'{directory_path}/{year}_Team_Total.csv'
    records = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        # Use the csv.reader to read the file
        csvreader = csv.reader(file)
        
        # Read the header (first row)
        header = next(csvreader)
        
        # Read each row in the csv file
        for row in csvreader:
            records.append(row)
    return records
    
    
def getAllWeekRecords():
    all_time_records = []
    for year in tqdm(range(2019, 2024), desc="Scraping data", unit="year"):
        all_time_records.append(get_records_for_year(year))
    return all_time_records

def sort_by_team(data):
    team_records = {}

    for year in data:
        for entry in year:
            if isinstance(entry, list) and len(entry) > 0:
                team_name = entry[0]  # Extract the team name (should be a string)
                records = entry[1:]  # Extract the records

                if not isinstance(team_name, str):
                    print(f"Error: Team name is not a string. It is: {type(team_name)}")
                    continue  # Skip to the next entry if team_name is not a string

                if team_name not in team_records:
                    team_records[team_name] = []

                team_records[team_name].append(records)
    return team_records
        
            
# Calculate and print the team totals

def combine_records(organized_data):
    combined_records = defaultdict(lambda: [0, 0, 0])  # Holds cumulative wins, losses, ties
    result = []
    for team, entries in organized_data.items():
        team_totals = [0] * 9  # Initialize weekly totals for 9 categories
        for entry in entries:
            for idx, record_str in enumerate(entry):
                if record_str == "--":
                    continue
                wins, losses, ties = parse_record(record_str)
                combined_records[idx][0] += wins
                combined_records[idx][1] += losses
                combined_records[idx][2] += ties
                
                team_totals[idx] = format_record(combined_records[idx][0], combined_records[idx][1], combined_records[idx][2])
        combined_records = defaultdict(lambda: [0, 0, 0]) 
        result.append([team] + team_totals)

    return result

def parse_record(record_str):
    """Parse a record string like '10-2 (83.3%)' into wins, losses, and ties."""
    match = re.match(r"(\d+)-(\d+)(?:-(\d+))?", record_str)
    if match:
        wins = int(match.group(1))
        losses = int(match.group(2))
        ties = int(match.group(3)) if match.group(3) else 0
        return wins, losses, ties
    return 0, 0, 0

def calculate_percentage(wins, losses, ties):
    total_games = wins + losses + ties
    if total_games == 0:
        return 0.0
    return (wins + 0.5 * ties) / total_games * 100

def format_record(wins, losses, ties):
    percentage = calculate_percentage(wins, losses, ties)
    return f"{wins}-{losses}-{ties} ({percentage:.1f}%)"

data = getAllWeekRecords()
sorted_by_team  = sort_by_team(data)
combine_records(sorted_by_team)

def write_combined_records_to_csv(output_file, records):
    headers = [
        "Team", "Favorites_StraightUp", "Favorites_vs_Spread", "Home_Records",
        "Home_vs_Spread", "Home_Favorites", "Home_Favorites_vs_Spread", "Home_Underdogs",
        "Home_Underdogs_vs_Spread", "Over/Unders"
    ]

    with open(output_file, mode='w', newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(headers)
        csvwriter.writerows(records)
        
directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/AllTime'

os.makedirs(directory_path, exist_ok=True)

file_path = f'{directory_path}/By_Team_Total_Last_5.csv'

write_combined_records_to_csv(file_path, combine_records(sorted_by_team))