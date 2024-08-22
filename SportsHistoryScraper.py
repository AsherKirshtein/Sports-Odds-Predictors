import requests
from bs4 import BeautifulSoup
import os
import csv
from tqdm import tqdm


def scrapePage(year):
    url = 'https://www.sportsoddshistory.com/nfl-game-season/?y=' + str(year)
    response = requests.get(url)
    if response.status_code == 200:
        
        directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{year}'
        os.makedirs(directory_path, exist_ok=True)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Find all <tbody> elements
        all_tbody = soup.find_all('tbody')
        # Function to print the content of a tbody 
        def write_tbody_content(tbody, index):
            # Create a CSV file for each tbody element
            header_Type = -1
            if index == 0:
                csv_filename = os.path.join(directory_path, f'{year}_Total.csv')
                header_Type = 1
            elif index == 1:
                csv_filename = os.path.join(directory_path, f'{year}_Team_Total.csv')
                header_Type = 2
            elif index == 19 and int(year) <= 2021:
                csv_filename = os.path.join(directory_path, f'{year}_Playoffs.csv')
                header_Type = 3
            elif index == 20:
                csv_filename = os.path.join(directory_path, f'{year}_Playoffs.csv')
                header_Type = 3
            else:
                csv_filename = os.path.join(directory_path, f'{year}_Week_{index - 1}.csv')
                header_Type = 4
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                writeHeader(header_Type, csvwriter)
                # Write each row's data to the CSV file
                for row in tbody.find_all('tr'):
                    cells = row.find_all('td')
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    csvwriter.writerow(row_data)
        # Iterate through all found <tbody> elements and print their contents
        for index, tbody in enumerate(all_tbody):
            write_tbody_content(tbody, index)
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

def writeHeader(header_Type, csvwriter):
    if header_Type == 1 or header_Type == 2:
        csvwriter.writerow([
            "Week", 
            "Favorites_StraightUp", 
            "Favorites_vs_Spread", 
            "Home_Records", 
            "Home_vs_Spread", 
            "Home_Favorites", 
            "Home_Favorites_vs_Spread", 
            "Home_Underdogs", 
            "Home_Underdogs_vs_Spread", 
            "Over/Unders",
            "Additional Notes"
        ])
    elif header_Type == 4:
        csvwriter.writerow([
            'Day', 
            'Date', 
            'Time(ET)',
            'Location', 
            'Favorite', 
            'Score', 
            'Spread',
            'Opponent', 
            'Underdog', 
            'Over/Under',
            "Additional Notes"
        ])
    elif header_Type == 3:
        csvwriter.writerow([
            'Round', 
            'Day', 
            'Date', 
            'Time(ET)',
            'Location', 
            'Favorite', 
            'Score', 
            'Spread',
            'Opponent', 
            'Underdog', 
            'Over/Under'
        ])


def scrape_All_Years():
    #Doesn't take too long. I don't want it parallel just to keep everything organized nicely
    for year in tqdm(range(1953, 2024), desc="Scraping data", unit="year"):
        scrapePage(str(year))
        
scrape_All_Years()