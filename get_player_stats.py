import requests
from bs4 import BeautifulSoup
import csv
import re
import psycopg2


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


def get_player_positions(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")
    positions = soup.findAll("table", class_="table sortable-table")
    QB = []
    RB = []
    WR = []
    TE = []
    for p in range(len(positions)):
        player_links = positions[p].select("td.name-col a")
        player_names = [link.text.strip() for link in player_links]
        # Filter out empty names if any
        player_names = [name for name in player_names if name]
        if p == 0:
            QB.append(player_names)
        elif p == 1:
            RB.append(player_names)
        elif p == 2: 
            WR.append(player_names)
        elif p == 3:
            TE.append(player_names)
    return QB, RB, WR, TE

def player_position(name, QB, RB, WR, TE):
    if any(name in sublist for sublist in QB):  
        return "QB"
    elif any(name in sublist for sublist in RB):
        return "RB"
    elif any(name in sublist for sublist in WR):
        return "WR"
    elif any(name in sublist for sublist in TE):
        return "TE"

def get_RB_stats(stats):
    try:
        rushes, rushyards, rushTds, receptions, receivingyards, receivingTDs = stats.split("-", 5)
        return rushes, rushyards, rushTds, receptions, receivingyards, receivingTDs
    except ValueError:
        return "DNP"
    
def get_QB_stats(stats):
    try:
        passyards, passTDs, Ints, rushes, rushyards, rushTds = stats.split("-", 5)
        return passyards, passTDs, Ints, rushes, rushyards, rushTds
    except ValueError:
        return "DNP"
    
def get_WR_stats(stats):
    try:
        rushes, rushyards, rushTds, receptions, receivingyards, receivingTDs = stats.split("-", 5)
        return rushes, rushyards, rushTds, receptions, receivingyards, receivingTDs
    except ValueError:
        return "DNP"
    
def get_TE_stats(stats):
    try:
        receptions, receivingyards, receivingTDs = stats.split("-", 3)
        return receptions, receivingyards, receivingTDs
    except ValueError:
        return "DNP"

def get_opponent_and_location(team, week, year):
    directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{year}/'
    file = directory_path + f'{year}_Week_{week}.csv'
    with open(file, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        for line in reader:
            date = line[1]
            if line[4] == team:
                opponent = line[8]
                if line[3] != "":
                    location = line[4]
                else:
                    location = line[8]
                return opponent, location, date
            elif line[8] == team:
                opponent = line[4]
                if line[3] != "":
                    location = line[4]
                else:
                    location = line[8]
                return opponent, location, date
        return "BYE", "None", date
                
    
    
def add_stats_to_db(position, player, player_stats, year, team_abbr):
    conn = psycopg2.connect(
    dbname="nfl_db",
    user="postgres",
    password="password",
    host="localhost"
    )
    cur = conn.cursor()
    team = team_abbr_map[team_abbr]
    for week in range(len(player_stats)):
        opponent, location, date = get_opponent_and_location(team_abbr_map[team_abbr],(week+1), year)
        if opponent == "BYE":
            continue
        player_stats[week] = player_stats[week].replace("--", "-")
        player_stats[week] = player_stats[week].lstrip("-")
        if position == "QB":
            stats = get_QB_stats(player_stats[week])
            if len(stats) < 5:
                continue
            cur.execute("""
                            INSERT INTO player_stats (position, player, team, pass_yards, pass_touchdowns, interceptions, rush_attempts, rush_yards, rush_touchdowns, week, opponent, location, game_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (position, player, team, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], (week+1), opponent, location, date))
            print(f"{year}: Added stats for {position} {player} week {(week+1)}")
        elif position == "RB":
            stats = get_RB_stats(player_stats[week])
            if len(stats) < 5:
                continue
            cur.execute("""
                            INSERT INTO player_stats (position, player, team, rush_attempts, rush_yards, rush_touchdowns, receptions, receiving_yards, receiving_touchdowns, week, opponent, location, game_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (position, player, team, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], (week+1), opponent, location, date))
           
            print(f"{year}: Added stats for {position} {player} week {(week+1)}")
        elif position == "WR":
            stats = get_WR_stats(player_stats[week])
            if len(stats) < 5:
                continue
            cur.execute("""
                            INSERT INTO player_stats (position, player, team, rush_attempts, rush_yards, rush_touchdowns, receptions, receiving_yards, receiving_touchdowns, week, opponent, location, game_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (position, player, team, stats[0], stats[1], stats[2], stats[3], stats[4], stats[5], (week+1), opponent, location, date))
            print(f"{year}: Added stats for {position} {player} week {(week+1)}")
        elif position == "TE":
            stats = get_TE_stats(player_stats[week])
            if len(stats) < 3:
                continue
            if stats == "DNP":
                continue
            cur.execute("""
                            INSERT INTO player_stats (position, player, team, receptions, receiving_yards, receiving_touchdowns, week, opponent, location, game_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (position, player, team, stats[0], stats[1], stats[2], (week+1), opponent, location, date))
            print(f"{year}: Added stats for {position} {player} week {(week+1)}")
    conn.commit()
    cur.close()
    conn.close()    
    return

def get_stats_by_year(year, team): 
    url = f'https://www.footballguys.com/stats/game-logs/teams?team={team}&year={year}'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    # Find the <th> element with class "data-header" and text "@ BUF"
    player_names = soup.findAll("td", class_="sticky-col name-header sticky-reg name-col")
    stats = soup.findAll("td", class_="data-col")
    QB,WR,RB,TE = get_player_positions(url)
    # Print the extracted text
    stat_index = 0
    if year < 2022:
        weeks = 17
    else:
        weeks = 18
        
    for p in player_names:
        player = p.text.strip()
        position = player_position(player, QB, WR, RB, TE)
        player_stats = []
        for i in range(stat_index*weeks, (stat_index*weeks)+weeks):
            stat_text = stats[i].get_text(separator="-").strip()
            player_stats.append(stat_text)
        add_stats_to_db(position, player, player_stats, year, team)
        stat_index+=1
    
                                


def get_all_teams_and_players():
    for year in range(2002, 2025):
        for team in team_abbr_map:
            get_stats_by_year(year, team)

get_all_teams_and_players()