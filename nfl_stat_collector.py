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

def parse_player_row(row_text, player_link):
        words = row_text.split()

        # Identify where the first numeric year appears
        for i, word in enumerate(words):
            if word.isdigit():  # First year (e.g., "1995")
                college = " ".join(words[1:i])  # Everything between Name and first year
                name = words[0]  # First word is usually the last name
                first_season = words[i]  # First year
                last_season = words[i+1]  # Second year
                games_played = words[i+2]  # Games played
                games_started = words[i+3] if len(words) > i+3 else "0"  # Handle missing value

                return [name, college, first_season, last_season, games_played, games_started, player_link]

        return None  # Return None if the format is incorrect

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
                    parsed_data = parse_player_row(row_text, player_link)
                    if parsed_data:
                        writer.writerow(parsed_data)
                        print(f"Saved: {parsed_data}")

        except Exception as e:
            print(f"Error on {url}: {e}")
    # Close the browser
    driver.quit()
    
    


# Run the function
get_All_Player_data()
