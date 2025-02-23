from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
import csv
from datetime import datetime
import re

team_abbr_map = {
    "ARZ": "Arizona_Cardinals",
    "ATL": "Atlanta_Falcons",
    "BAL": "Baltimore_Ravens",
    "BUF": "Buffalo_Bills",
    "CAR": "Carolina_Panthers",
    "CHI": "Chicago_Bears",
    "CIN": "Cincinnati_Bengals",
    "CLE": "Cleveland_Browns",
    "DAL": "Dallas_Cowboys",
    "DEN": "Denver_Broncos",
    "DET": "Detroit_Lions",
    "GB": "Green_Bay_Packers",
    "HOU": "Houston_Texans",
    "IND": "Indianapolis_Colts",
    "JAX": "Jacksonville_Jaguars",
    "KC": "Kansas_City_Chiefs",
    "LV": "Las_Vegas_Raiders",
    "LAC": "Los_Angeles_Chargers",
    "LAR": "Los_Angeles_Rams",
    "MIA": "Miami_Dolphins",
    "MIN": "Minnesota_Vikings",
    "NE": "New_England_Patriots",
    "NO": "New_Orleans_Saints",
    "NYG": "New_York_Giants",
    "NYJ": "New_York_Jets",
    "PHI": "Philadelphia_Eagles",
    "PIT": "Pittsburgh_Steelers",
    "SF": "San_Francisco_49ers",
    "SEA": "Seattle_Seahawks",
    "TB": "Tampa_Bay_Buccaneers",
    "TEN": "Tennessee_Titans",
    "WAS": "Washington_Commanders"
}

def get_all_links():
    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the URL
    driver.get("https://www.ourlads.com/nfldepthcharts/")
    roster_links = []
    depth_chart_links = []
    try:
        xpaths = [
            '//main/div[8]/div[1]/div',  # First XPath
            '//main/div[8]/div[2]/div'
        ]
        for xpath in xpaths:
            containers = driver.find_elements(By.XPATH, xpath)  # More general XPath
            # Loop through each container and extract links
            for container in containers:
                links = container.find_elements(By.TAG_NAME, "a")  # Find all <a> tags inside
                for link in links:
                    href = link.get_attribute("href")
                    if href:
                        if "roster" in href.lower():  # Convert to lowercase for case-insensitive check
                            roster_links.append(href)
                        elif "depthchart" in href.lower():
                            depth_chart_links.append(href)    
    except Exception as e:
        print(f"Error fetching links: {e}")

    # Close the browser
    driver.quit()
    return roster_links, depth_chart_links

def clean_row_data(row):
    if len(row) >= 3:  # Ensure there are enough elements to remove
        del row[-3]  # Remove 3rd-to-last element
        del row[-2]  # Remove 2nd-to-last element
    if len(row) > 2:  # Ensure we have enough elements to swap
        row[0], row[2] = row[2], row[0]  # Swap the 1st and 3rd elements
    return row

def update_rosters():
    roster_links, depthchart_links = get_all_links()
    base_directory="/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/Current_NFL_Rosters"
    for link in roster_links:
        chrome_options = Options()
        chrome_options.add_argument('--headless') 
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(link)
        os.makedirs(base_directory, exist_ok=True)
        team_abbr = link.split("/")[-1]  # Extracts BUF, MIA, NE, etc.
        team_name = team_abbr_map.get(team_abbr, f"Unknown_{team_abbr}")  # Defaults to Unknown_{abbr} if not found
        team_folder = os.path.join(base_directory, team_name)
        os.makedirs(team_folder, exist_ok=True)
        print(f"Folder created: {team_folder}")
        csv_info = []
        try:
            table_xpath = "/html/body/form/div[5]/div[2]/div[4]/div/div/div[3]/div/div/table/tbody"
            table = driver.find_element(By.XPATH, table_xpath)
            rows = table.find_elements(By.TAG_NAME, "tr")
            for i, row in enumerate(rows, start=1): 
                cells = row.find_elements(By.TAG_NAME, "td")
                row_data = [cell.text.strip() for cell in cells]
                if len(row_data) > 2:  # Ensure valid data
                    data = clean_row_data(row_data)
                    csv_info.append(data)
            position_priority = {"QB": 1, "RB": 2, "WR": 3, "TE": 4}
            sorted_players = sorted(csv_info, key=lambda x: position_priority.get(x[0], 99))
            file_path = os.path.join(team_folder, f"{team_name}_roster.csv")
            with open(file_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Jersey Number","Player", "Position","Date_of_Birth", "Age", "Height", "Weight", "School", "Years_In_NFL"])
                for player in sorted_players:
                    writer.writerow(player)   
        except Exception as e:
            print(f"Error extracting data from {link}: {e}")
    # Close the browser
    driver.quit()
        
update_rosters()