import requests
from bs4 import BeautifulSoup
import re


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

def get_stats_by_year(year): 
    url = f'https://www.footballguys.com/stats/game-logs/teams?team=ARI&year={year}'
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "lxml")

    # Find the <th> element with class "data-header" and text "@ BUF"
    player_names = soup.findAll("td", class_="sticky-col name-header sticky-reg name-col")
    stats = soup.findAll("td", class_="data-col")
    QB,WR,RB,TE = get_player_positions(url)
    # Print the extracted text
    stat_index = 0
    for p in player_names:
        player = p.text.strip()
        position = player_position(player, QB, WR, RB, TE)
        player_stats = []
        for i in range(stat_index*18, (stat_index*18)+18):
            stat = stats[i].text.strip()
            player_stats.append(stat)
        print(position, player, player_stats)
        stat_index+=1
            
    
                                
def add_stats_to_db():
    return


get_stats_by_year(2024)