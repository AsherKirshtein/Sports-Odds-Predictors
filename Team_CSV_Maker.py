import csv
from tqdm import tqdm
import re
from collections import defaultdict
import os

def get_records_for_year(year):
    directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{year}'
    file_path = f'{directory_path}/{year}_Total.csv'
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
    organized_data = organize_data_by_week(all_time_records)
    return organized_data

def organize_data_by_week(data):
    # Create a dictionary to hold the data for each week
    weeks = {}
    playoffs = []

    for week_data in data:
        for entry in week_data:
            week_number = entry[0]
            if week_number.lower() == "playoffs":
                playoffs.append(entry)
            else:
                if week_number not in weeks:
                    weeks[week_number] = []
                weeks[week_number].append(entry)

    # Sort the weeks numerically and then add playoffs at the end
    sorted_weeks = dict(sorted(weeks.items(), key=lambda x: int(x[0])))
    
    # If there are any playoffs entries, add them at the end
    if playoffs:
        sorted_weeks["Playoffs"] = playoffs

    return sorted_weeks
   
def add_all_records_together():
    all_time = getAllWeekRecords()
    return combine_records(all_time)
    
   
#starting from 1953

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

def combine_records(organized_data):
    combined_records = defaultdict(lambda: [0, 0, 0])  # Holds cumulative wins, losses, ties
    result = []

    for week, entries in organized_data.items():
        weekly_totals = [0] * 9  # Initialize weekly totals for 9 categories
        for entry in entries:
            for idx, record_str in enumerate(entry[1:], start=0):
                if record_str == "--":
                    continue

                wins, losses, ties = parse_record(record_str)
                combined_records[idx][0] += wins
                combined_records[idx][1] += losses
                combined_records[idx][2] += ties

                weekly_totals[idx] = format_record(combined_records[idx][0], combined_records[idx][1], combined_records[idx][2])

        result.append([week] + weekly_totals)

    return result

def write_combined_records_to_csv(combined_records, output_file):
    headers = [
        "Week", "Favorites_StraightUp", "Favorites_vs_Spread", "Home_Records",
        "Home_vs_Spread", "Home_Favorites", "Home_Favorites_vs_Spread", "Home_Underdogs",
        "Home_Underdogs_vs_Spread", "Over/Unders"
    ]

    with open(output_file, mode='w', newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(headers)
        csvwriter.writerows(combined_records)


def write_combined_records_to_csv(output_file):
    headers = [
        "Week", "Favorites_StraightUp", "Favorites_vs_Spread", "Home_Records",
        "Home_vs_Spread", "Home_Favorites", "Home_Favorites_vs_Spread", "Home_Underdogs",
        "Home_Underdogs_vs_Spread", "Over/Unders"
    ]

    combined_records = add_all_records_together()

    with open(output_file, mode='w', newline='') as file:
        csvwriter = csv.writer(file)
        csvwriter.writerow(headers)
        csvwriter.writerows(combined_records)
        
directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/AllTime'

os.makedirs(directory_path, exist_ok=True)

file_path = f'{directory_path}/By_Week_Total_last_5.csv'

write_combined_records_to_csv(file_path)