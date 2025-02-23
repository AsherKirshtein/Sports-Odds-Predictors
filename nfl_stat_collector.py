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

def get_All_Player_data():
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    for letter in range(97, 123):  # ASCII values of 'a' to 'z'
        url_letter = chr(letter)
        url = f'https://www.profootballarchives.com/nflplayers-{url_letter}.html'
        print(f"Fetching: {url}")
        driver.get(url)

        # Try to locate the specific <tr> element
        try:
            tr_elements = driver.find_elements(By.XPATH, "/html/body/div[5]/table/tbody/tr")
            
            # Print all rows found
            for tr in tr_elements:
                row_text = tr.text.strip()
                row_parts = row_text.split()
                if len(row_parts) >= 7:
                    name = " ".join(row_parts[:2])  # Name (First Last)
                    college = row_parts[2]  # College
                    years_played = row_parts[3]  # Years played
                    first_season = row_parts[4]  # First season
                    last_season = row_parts[5]  # Last season
                    games_played = row_parts[6]  # Games played
                    games_started = row_parts[7] if len(row_parts) > 7 else "0"  # Games started (default to 0)
                    
                try:
                    a_tag = tr.find_element(By.XPATH, "./td[1]/a")  # Find the <a> within the row
                    player_link = a_tag.get_attribute("href")
                except:
                    player_link = "No Link"
                
                directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/All_PLayer_Data'
                file_path = os.path.join(directory_path, f'Last_Name_{url_letter.upper()}.csv')
                with open(file_path, "a", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if f.tell() == 0:
                        writer.writerow(["Name", "College", "Years_Played", "First_Season", "Last_Season", "Games_Played", "Games_Started", "Link"])
                    if name != "Player":
                        writer.writerow([name, college, years_played, first_season, last_season, games_played, games_started, player_link])
                        print(f"Saved: {name}, {college}, {years_played}, {first_season}, {last_season}, {games_played}, {games_started}, {player_link}")

        except Exception as e:
            print(f"Error on {url}: {e}")

    # Close the browser
    driver.quit()

# Run the function
get_All_Player_data()
