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
            if index == 0:
                csv_filename = os.path.join(directory_path, f'{year}_Total.csv')
            elif index == 1:
                csv_filename = os.path.join(directory_path, f'{year}_Team_Total.csv')
            elif index == 19 and int(year) <= 2021:
                csv_filename = os.path.join(directory_path, f'{year}_Playoffs.csv')
            elif index == 20:
                csv_filename = os.path.join(directory_path, f'{year}_Playoffs.csv')
            else:
                csv_filename = os.path.join(directory_path, f'{year}_Week_{index - 1}.csv')
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                csvwriter = csv.writer(csvfile)
                
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

def scrape_All_Years():
    #Doesn't take too long. I don't want it parallel just to keep everything organized nicely
    for year in tqdm(range(1953, 2024), desc="Scraping data", unit="year"):
        scrapePage(str(year))
        
scrape_All_Years()