import requests
from bs4 import BeautifulSoup
import time, random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import os
import csv

headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                        '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.google.com/',
        }

def respectful_sleep():
    time.sleep(random.uniform(3.2, 5.5))

def get_box_score_links(url):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
                  '(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')
    if response.status_code == 429:
        print(f'Too many requests in a short time url: {url}')
        return 429
    # Extract all hrefs that start with /boxscores/ and end with .htm
    boxscore_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.startswith('/boxscores/') and href.endswith('.htm'):
            boxscore_links.append("https://www.pro-football-reference.com" + href)

    # Remove duplicates just in case
    return list(set(boxscore_links))


def get_all_links():
    for year in range(2000,2025):
        weeks = 0
        if year >2022:
            weeks = 18
        elif year <= 2022 and year > 1990:
            weeks = 17
        elif year <= 1989 and year > 1978:
            weeks = 16
        elif year == 1993:
            weeks = 18
        elif year == 1982:
            weeks = 18
            
        for week in range(1,weeks):
            url = f'https://www.pro-football-reference.com/years/{year}/week_{week}.htm'
            box_scores = get_box_score_links(url)
            respectful_sleep()
            if box_scores == 429:
                break
            else:
                csv_filename = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/Simulation_Based_Prediction/box_scores_urls.txt'
                with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                            csvwriter = csv.writer(csvfile)
                            csvwriter.writerow([box_scores])
                            
                            
def get_espn_links():
        game_play_by_play_links = []
        csv_filename = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/Simulation_Based_Prediction/box_scores_urls.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Link','Year', 'Week'])
            for year in range(2010,2025):
                weeks = 0
                if year >2022:
                    weeks = 18
                elif year <= 2022 and year > 1990:
                    weeks = 17
                elif year <= 1989 and year > 1978:
                    weeks = 16
                elif year == 1993:
                    weeks = 18
                elif year == 1982:
                    weeks = 18
                    
                for week in range(1,(weeks+1)):
                    url = f"https://www.espn.com/nfl/scoreboard/_/week/{week}/year/{year}/seasontype/2"
                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    print(f"Year: {year}, Week: {week}")
                    if response.status_code == 200:
                        for a in soup.find_all('a', href=True):
                            href = a['href']
                            if href.startswith('/nfl/playbyplay/'):
                                link = f'https://www.espn.com{href}'
                                info = [link, year, week]
                                csvwriter.writerow(info)
                    else:
                        print(response.status_code)
                for week in range(1,5):
                    url = f"https://www.espn.com/nfl/scoreboard/_/week/{week}/year/{year}/seasontype/3"
                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    week_name = "Wildcard round"
                    if week == 2:
                        week_name = "Divisional round"
                    elif week == 3:
                        week_name = "Conference Championship"
                    elif week == 4: 
                        week_name = "Super Bowl"
                    print(f"Year: {year}, Week: {week_name}")
                    if response.status_code == 200:
                        for a in soup.find_all('a', href=True):
                            href = a['href']
                            if href.startswith('/nfl/playbyplay/'):
                                link = f'https://www.espn.com{href}'
                                info = [link, year, week_name]
                                csvwriter.writerow(info)
                    else:
                        print(response.status_code)
        return game_play_by_play_links

def get_all_plays(url):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    wait = WebDriverWait(driver, 20)

    # Wait until at least one panel header is visible
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "AccordionPanel__header")))

    # Click each panel header to expand all drives
    headers = driver.find_elements(By.CLASS_NAME, "AccordionPanel__header")
    for header in headers:
        try:
            driver.execute_script("arguments[0].scrollIntoView();", header)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", header)  # 💥 JS click avoids overlay issues
            time.sleep(0.4)
        except Exception as e:
            print(f"Click failed: {e}")

    time.sleep(1.5)  # let all drives load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    drives = soup.select("ul.PlayList")
    game_plays = []
    for i, ul in enumerate(drives, 1):
        drive = []
        for li in ul.select("li.PlayListItem"):
            headline = li.select_one("h3.PlayListItem__Headline")
            desc = li.select_one("span.PlayListItem__Description")
            if headline and desc:
                play = f"{headline.text.strip()} — {desc.text.strip()}"
                drive.append(play)
        game_plays.append(drive)
    return game_plays


team_abbr_map = {
    "ARI": "Arizona Cardinals",
    "ATL": "Atlanta Falcons",
    "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills",
    "CAR": "Carolina Panthers",
    "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals",
    "CLE": "Cleveland Browns",
    "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos",
    "DET": "Detroit Lions",
    "GB": "Green Bay Packers",
    "HOU": "Houston Texans",
    "IND": "Indianapolis Colts",
    "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs",
    "LV": "Las Vegas Raiders",
    "LAC": "Los Angeles Chargers",
    "LAR": "Los Angeles Rams",
    "MIA": "Miami Dolphins",
    "MIN": "Minnesota Vikings",
    "NE": "New England Patriots",
    "NO": "New Orleans Saints",
    "NYG": "New York Giants",
    "NYJ": "New York Jets",
    "PHI": "Philadelphia Eagles",
    "PIT": "Pittsburgh Steelers",
    "SF": "San Francisco 49ers",
    "SEA": "Seattle Seahawks",
    "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans",
    "WAS": "Washington Commanders"
}

def get_teams(plays):
    teams = set()
    for drive in plays:
        for play in drive:
            team = play.split(" ", 10)[4]
            if team_abbr_map.__contains__(team):
                teams.add(team_abbr_map[team])
        if len(teams) == 2:
            team_list = list(teams)  # or tuple(teams)
            return team_list[0], team_list[1]

def get_play_type(play, index):
        playtype = play[index]
        yards_gained = 0
        spot_of_ball = play[4] + " " + play[5]
        if playtype == 'sacked':
            yards_gained = play[index+5]
            spot_of_ball = play[index + 2] + " " + play[index+3]
        if playtype == 'FUMBLES':
            index += 11
            playtype = play[index]
        if 'INTERCEPTED' in play and 'to' in play:
            playtype = f'pass {play[index]} {play[index + 1]} {play[index + 2]} (intercepted)'
            i = play.index('to')
            spot_of_ball = play[i+1] + " " + play[i+2]
            yards_gained = 0
        elif playtype == 'right' or playtype == 'left':
            playtype = f'run {play[index]} {play[index + 1]}'
            if play[-1] == 'TOUCHDOWN.':
                yards_gained = play[index+2]
                spot_of_ball = 'PAT'
            else:
                yards_gained = play[index+6]
                spot_of_ball = play[index+3] + " " + play[index+4]
        elif playtype == 'up':
            playtype = 'run middle'
        elif playtype == 'pass':
            if play[index + 1] == 'incomplete':
                playtype = f'{play[index]} {play[index+2]} ({play[index+1]})'
            else:
                playtype = f'{play[index]} {play[index + 1]} {play[index + 2]} (complete)'
                if play[index + 8] == 'TOUCHDOWN.':
                    yards_gained = play[index + 6]
                    spot_of_ball = -1
                else:
                    yards_gained = play[index+9]
                    spot_of_ball = play[index+6] + " " + play[index+7]
        elif playtype == 'punts':
            playtype = 'punt'
            yards_gained = play[index+1]
            spot_of_ball = play[index + 4] + " " +play[index + 5]
        
        elif playtype == 'kneels':
            yards_gained = play[index + 5]
            spot_of_ball = play[index + 2] + " " + play[index + 3]
        elif playtype.isdigit():
            yards = playtype
            if play[index + 5] == 'No' and play[index + 6] == 'Good,':
                playtype = f'field goal miss {play[index + 7]} {play[index + 8]} ({yards} yards)'
            else:
                playtype = f'field goal make ({yards} yards)'
                spot_of_ball = -1
        
        if spot_of_ball == 'pushed ob':
            spot_of_ball = spot_of_ball = play[index+5] + " " + play[index+6]
        if spot_of_ball == 'ob at':
            i = play.index('at')+1
            spot_of_ball = play[i] + " " + play[i+1]
            yards_gained = play[index+3]
            
        if yards_gained == 'no':
            yards_gained = 0
            
        return playtype, yards_gained, spot_of_ball
    
def get_play_by_play():
        csv_filename = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/Simulation_Based_Prediction/box_scores_urls.csv'
        csv_error_file = '/Users/asherkirshtein/Desktop/Sports Odds Predictors/Simulation_Based_Prediction/csv_play_by_play/errors.txt'
        with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                try:
                    if row.__contains__('Link'):
                        continue
                    plays = get_all_plays(row[0])
                    t1, t2 = get_teams(plays)
                    t1 = t1.split(" ")[-1]
                    t2 = t2.split(" ")[-1]
                    d_path = '/Users/asherkirshtein/Desktop/Sports Odds Predictors/Simulation_Based_Prediction/csv_play_by_play/'
                    file_name = d_path + f'{t1}_vs_{t2}_{row[1]}_{row[2]}.csv'
                    print(file_name)
                    
                    with open(file_name, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Quarter','Down', 'To Go', 'Location', 'Time', 'Formation', 'Play Type',
                                        'Part of Field', 'Completion', 'Yards Gained', 'Spot of Ball'])  # optional header
                        for drive in plays:
                            write_me = [None] * 11
                            for play in drive:
                                outcome = play.split(" ")
                                down = outcome[0]
                                if down == "&":
                                    continue
                                to_go = outcome[2]
                                location = ""
                                if '50' in outcome:
                                    i = outcome.index('50')
                                    outcome.insert(i, "THE")
                                else:
                                    location = outcome[4] + " " +outcome[5]
                                time = outcome[7].lstrip("(")
                                quarter = outcome[9].strip(")")
                                index = 10
                                formation = ""
                                
                                if outcome[10] == 'Timeout':
                                    play_type = f'{outcome[10]} {outcome[11]} by {outcome[13]}' 
                                    timeout_number = outcome[11]
                                    team_to_call_to = outcome[13]
                                elif outcome[index] == "(Shotgun)":
                                    formation = "Shotgun"
                                    index += 1
                                player = outcome[index]
                                index += 1
                                
                                
                                if outcome[10] != 'Timeout':
                                    play_type, yards_gained, spot_of_ball = get_play_type(outcome, index)
                                    p = play_type.split(" ")
                                    play_type = p[0]
                                    completion = ""
                                    part_of_field = ""
                                    if play_type == 'pass':
                                        completion = p[-1]
                                        part_of_field = ' '.join(str(x) for x in p[1:-1])
                                    elif play_type == 'run':
                                        part_of_field = ' '.join(str(x) for x in p[1:])
                                        
                                    
                                    write_me[0] = quarter
                                    write_me[1] = down
                                    write_me[2] = to_go
                                    write_me[3] = location
                                    write_me[4] = time
                                    
                                    write_me[5] = formation
                                    write_me[6] = play_type
                                    write_me[7] = part_of_field
                                    write_me[8] = completion
                                    write_me[9] = yards_gained
                                    write_me[10] = spot_of_ball
                                    
                                else:
                                    
                                    write_me[0] = quarter
                                    write_me[1] = down
                                    write_me[2] = to_go
                                    write_me[3] = location
                                    write_me[4] = time
                                    
                                    write_me[5] = formation
                                    write_me[6] = ""
                                    write_me[7] = ""
                                    write_me[8] = ""
                                    write_me[9] = ""
                                    write_me[6] = play_type + " " + timeout_number
                                
                                
                    
                                writer.writerow(write_me)
                except:
                    with open(csv_error_file, 'w', newline='') as wr:
                                writer = csv.writer(wr)
                                writer.writerow(play)
                               
            
get_play_by_play()