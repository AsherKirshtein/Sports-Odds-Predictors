import requests
from bs4 import BeautifulSoup
import time, random
import psycopg2
from concurrent.futures import ThreadPoolExecutor
import re
from tqdm import tqdm
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

    # Click each panel header to expand all drives EXCEPT the first one
    headers = driver.find_elements(By.CLASS_NAME, "AccordionPanel__header")
    for i, header in enumerate(headers):
        if i == 0:
            continue  # skip clicking the first one — it's already open
        try:
            driver.execute_script("arguments[0].scrollIntoView();", header)
            time.sleep(0.2)
            driver.execute_script("arguments[0].click();", header)
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
 
def get_drive_results(link): 
    options = Options()
    options.add_argument('--headless')  # Remove this line if you want to see the browser
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    
    driver.get(link)
    soup = BeautifulSoup(driver.page_source, 'html.parser')   
    headers = soup.select('div.AccordionHeader')

    drive_results = []

    for header in headers:
        team_logo_img = header.select_one('.AccordionHeader__Left__TeamLogoContainer img')
        team_with_possession = team_logo_img['alt'] if team_logo_img else 'Unknown'

        headline = header.select_one('.AccordionHeader__Left__Drives__Headline')
        description = header.select_one('.AccordionHeader__Left__Drives__Description')

        away_team = header.select_one('.AccordionHeader__Right__AwayTeam__Name')
        away_score = header.select_one('.AccordionHeader__Right__AwayTeam__Score')

        home_team = header.select_one('.AccordionHeader__Right__HomeTeam__Name')
        home_score = header.select_one('.AccordionHeader__Right__HomeTeam__Score')

        drive_results.append({
            "possessing_team": team_with_possession,
            "summary": headline.text.strip() if headline else 'N/A',
            "description": description.text.strip() if description else 'N/A',
            "away_team": away_team.text.strip() if away_team else '',
            "away_score": away_score.text.strip() if away_score else '',
            "home_team": home_team.text.strip() if home_team else '',
            "home_score": home_score.text.strip() if home_score else ''
        })

    return drive_results

def write_to_db(info):
    conn = psycopg2.connect(
    host="localhost",        # or your EC2 IP / Supabase URL
    port="5432",
    dbname="nfl_data",
    user="asherkirshtein",
    password="your_password"
    )
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO play_by_play (
            quarter, down, to_go, location, time, formation, play_type,
            part_of_field, completion, yards_gained, spot_of_ball,
            passer, runner, receiver, possession, summary, home_score, away_score, week,
            year, play_number, Home_Team, Away_Team
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, info)

    conn.commit()
    cur.close()
    conn.close()


def scrape_row(row):
                    d_results = get_drive_results(row[0])
                    week = row[2]
                    year = row[1]
                    Away_Team = d_results[0]['away_team']
                    Home_Team = d_results[0]['home_team']
                    plays = get_all_plays(row[0])
                    drive_indexer = 0
                    play_number = 0
                    for drive in plays:
                            play_number+=1
                            end_of_drive_info =d_results[drive_indexer]
                            write_me = [None] * 23
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
                                elif outcome[index] == "(Shotgun)":
                                    formation = "Shotgun"
                                    index += 1
                                index += 1
                                passer = ''
                                runner = ''
                                receiver = ''
                                names = [token for token in outcome if re.search(r'[A-Za-z]\.[A-Za-z]', token)]
                                if outcome[10] != 'Timeout':
                                    play_type, yards_gained, spot_of_ball = get_play_type(outcome, index)
                                    p = play_type.split(" ")
                                    play_type = p[0]
                                    completion = ""
                                    part_of_field = ""
                                    if play_type == 'pass':
                                        completion = p[-1]
                                        part_of_field = ' '.join(str(x) for x in p[1:-1])
                                        passer = names[0]
                                        if len(names) > 1:
                                            receiver = names[1]
                                    elif play_type == 'run':
                                        part_of_field = ' '.join(str(x) for x in p[1:])
                                        runner = names[0]
                                    
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
                                    
                                    write_me[11] = passer
                                    write_me[12] = runner
                                    write_me[13] = receiver
                                    
                                    write_me[14] = end_of_drive_info['possessing_team']
                                    write_me[15] = end_of_drive_info['summary']
                                    
                                    write_me[16] = end_of_drive_info['home_score']
                                    write_me[17] = end_of_drive_info['away_score']
                                    write_me[18] = week
                                    write_me[19] = year
                                    write_me[20] = play_number
                                    write_me[21] = Home_Team
                                    write_me[22] = Away_Team
                                    
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
                                    
                                    write_me[14] = end_of_drive_info['possessing_team']
                                    write_me[15] = end_of_drive_info['summary']
                                    
                                    write_me[16] = end_of_drive_info['home_score']
                                    write_me[17] = end_of_drive_info['away_score']
                                    
                                    write_me[18] = week
                                    write_me[19] = year
                                    write_me[20] = play_number
                                    write_me[21] = Home_Team
                                    write_me[22] = Away_Team
                                    
                                write_to_db(write_me)
                            drive_indexer += 1            

    
def get_play_by_play():
    csv_filename = '/Users/asherkirshtein/Desktop/Sports Odds Predictors/Simulation_Based_Prediction/box_scores_urls.csv'

    with open(csv_filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = list(csv.reader(csvfile))  # Convert to list so tqdm knows the total
        for row_counter, row in enumerate(tqdm(reader, desc="Scraping rows"), start=1):
            try:
                if 'Link' in row[0]:  # cleaner header check
                    continue
                scrape_row(row)
            except Exception as e:
                print(f"❌ Failed on row {row_counter}: {row}")
                print(f"Error: {e}")
                                
                               
            
get_play_by_play()