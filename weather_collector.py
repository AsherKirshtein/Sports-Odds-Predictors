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



nfl_teams = [
    "Arizona Cardinals", #0
    "Atlanta Falcons", #1
    "Baltimore Ravens", #2
    "Buffalo Bills", #3
    "Carolina Panthers", #4
    "Chicago Bears", #5
    "Cincinnati Bengals", #6
    "Cleveland Browns", #7
    "Dallas Cowboys", #8
    "Denver Broncos", #9
    "Detroit Lions", #10
    "Green Bay Packers", #11
    "Houston Texans", #12
    "Indianapolis Colts", #13
    "Jacksonville Jaguars", #14
    "Kansas City Chiefs", #15
    "Las Vegas Raiders", #16
    "Los Angeles Chargers", #17
    "Los Angeles Rams", #18
    "Miami Dolphins", #19
    "Minnesota Vikings", #20
    "New England Patriots", #21
    "New Orleans Saints", #22
    "New York Giants", #23
    "New York Jets", #24
    "Philadelphia Eagles", #25
    "Pittsburgh Steelers", #26
    "San Francisco 49ers", #27
    "Seattle Seahawks", #28
    "Tampa Bay Buccaneers", #29
    "Tennessee Titans", #30
    "Washington Commanders" #31
]

current_week_this_year = 18
current_year = 2025

Team_Weather_Url =[
     "https://www.wunderground.com/history/daily/us/az/phoenix/KPHX/date/",
     "https://www.wunderground.com/history/daily/us/ga/atlanta/KATL/date/",
     "https://www.wunderground.com/history/daily/us/md/glen-burnie/KBWI/date/",
     "https://www.wunderground.com/history/daily/us/ny/cheektowaga/KBUF/date/",
     "https://www.wunderground.com/history/daily/us/nc/charlotte/KCLT/date/",
     "https://www.wunderground.com/history/daily/us/il/chicago/KMDW/date/",
     "https://www.wunderground.com/history/daily/us/oh/cincinnati/KLUK/date/",
     "https://www.wunderground.com/history/daily/us/oh/cleveland/KCLE/date/",
     "https://www.wunderground.com/history/daily/us/tx/grapevine/KDFW/date/",
     "https://www.wunderground.com/history/daily/us/co/broomfield/KBJC/date/",
     "https://www.wunderground.com/history/daily/us/mi/detroit/KDET/date/",
     "https://www.wunderground.com/history/daily/us/wi/hobart/KGRB/date/",
     "https://www.wunderground.com/history/daily/us/tx/houston/KHOU/date/",
     "https://www.wunderground.com/history/daily/us/in/indianapolis/KIND/date/",
     "https://www.wunderground.com/history/daily/us/fl/jacksonville/KJAX/date/",
     "https://www.wunderground.com/history/daily/us/mo/kansas-city/KMCI/date/",
     "https://www.wunderground.com/history/daily/us/nv/las-vegas/KLAS/date/",
     "https://www.wunderground.com/history/daily/us/ca/hawthorne/KHHR/date/",
     "https://www.wunderground.com/history/daily/us/ca/hawthorne/KHHR/date/",
     "https://www.wunderground.com/history/daily/us/fl/opa-locka/KOPF/date/",
     "https://www.wunderground.com/history/daily/us/mn/fort-snelling/KMSP/date/",
     "https://www.wunderground.com/history/daily/us/ma/east-boston/KBOS/date/",
     "https://www.wunderground.com/history/daily/us/la/kenner/KMSY/date/",
     "https://www.wunderground.com/history/daily/us/nj/moonachie/KTEB/date/",
     "https://www.wunderground.com/history/daily/us/nj/moonachie/KTEB/date/",
     "https://www.wunderground.com/history/daily/us/pa/essington/KPHL/date/",
     "https://www.wunderground.com/history/daily/us/pa/imperial/KPIT/date/",
     "https://www.wunderground.com/history/daily/us/ca/san-jose/KSJC/date/",
     "https://www.wunderground.com/history/daily/us/wa/seattle/KBFI/date/",
     "https://www.wunderground.com/history/daily/us/fl/tampa/KTPA/date/",
     "https://www.wunderground.com/history/daily/us/tn/nashville/KBNA/date/",
     "https://www.wunderground.com/history/daily/us/va/arlington/KDCA/date/",
]


def get_game_days(Team, Earliest_year):
    game_times = []
    for year in range(Earliest_year, current_year):
        directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{year}'
        week_range = 18
        if year >= 2022:
            week_range = 19
        for week in range(1,week_range):
            file = directory_path + f'/{year}_Week_{week}.csv'
            with open(file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    date = format_date(row['Date'])
                    time = row['Time(ET)']
                    favorite = row['Favorite']
                    under_dog = row['Underdog']
                    if (Team == favorite and row["Location"].__contains__("@")) or (Team == under_dog and row["Opponent"].__contains__("@")):
                        game_times.append(date + ';' + time)
    return game_times
                
 
def get_conditions(location_url, date):
    day, time = date.split(";", 2)
    real_url = location_url + day
    df = scrape_table(real_url)
    hour, minute = time.split(":", 2)
    start_time = time + ' PM'
    end_time = str((int(hour) + 3)) + ":" + "59" + ' PM'
    df[0] = df[0].apply(lambda x: datetime.strptime(x, "%I:%M %p").time())
    # Define start and end times
    s_time = datetime.strptime(start_time, "%I:%M %p").time()
    e_time = datetime.strptime(end_time, "%I:%M %p").time()
    filtered_df = df[(df[0] >= s_time) & (df[0] <= e_time)]
    return filtered_df
                  
                    
def format_date(date):
    date_obj = datetime.strptime(date, "%b %d, %Y")
    return f"{date_obj.year}-{date_obj.month}-{date_obj.day}"

            
        

def scrape_table(url):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the URL
        driver.get(url)
        
        # Wait for the table to be present (timeout after 10 seconds)
        table_body_xpath = "/html/body/app-root/app-history/one-column-layout/wu-header/sidenav/mat-sidenav-container/mat-sidenav-content/div[2]/section/div[2]/div[1]/div[5]/div[1]/div/lib-city-history-observation/div/div[2]/table/tbody"
        
        table_body = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, table_body_xpath))
        )
        # Get all rows
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        # Extract data from rows
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells]
            data.append(row_data)
        # Convert to DataFrame
        df = pd.DataFrame(data)
        return df
        
    finally:
        # Always close the driver
        driver.quit()


def find_weather_by_team():
    for index in range(0,32):
        directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/Weather_Data'
        place = re.sub(r'[^a-zA-Z0-9]', '',str(nfl_teams[index].split()[:-1]))
        file_path = os.path.join(directory_path, f'{place}_weather.csv')  # Change the filename as needed
        print("Collecting data for ", nfl_teams[index])
        dates = get_game_days(nfl_teams[index], 2000)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("Date, Time, Temperature, Dew Point,Humidity, Wind, Wind Speed, Wind Gust, Pressure, Precip., Condition\n")
            for date in dates:
                print(date)
                try:
                    conditions = get_conditions(Team_Weather_Url[index], date)
                    for _, row in conditions.iterrows():
                        row_data = [str(date.split(";", 2)[0])] + row.astype(str).tolist()
                        f.write(",".join(row_data) + "\n")
                except:
                    continue
        
        
                
    
find_weather_by_team()
