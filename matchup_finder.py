import csv
import os

def combine_record(record):
    # Split the record by space to separate the prefix from the numbers
    parts = record.split()
    score = parts[1]
    num1_str, num2_str = score.split('-')
    return (int(num1_str) + int(num2_str))

def get_Score_Difference(score):
    parts = score.split()
    game_score = parts[1]
    num1_str, num2_str = game_score.split('-')
    return (int(num1_str) - int(num2_str))


def getLastMatchups(amount, team_1, team_2):
    found = 0
    current_year = 2023
    current_week = 18
    matchups = []
    while found < amount:
        try:
            directory_path = f'/Users/asherkirshtein/Desktop/Sports Odds Predictors/CSV/{current_year}'
            csv_filename = os.path.join(directory_path, f'{current_year}_Week_{current_week}.csv')
            with open(csv_filename, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    favorite = row[4]
                    underdog = row[8]
                    if (favorite == team_1 or favorite == team_2) and (underdog == team_1 or underdog == team_2):
                        matchups.append(row)
                        print(row)
                        found+=1
                        
            current_week-=1
            if current_week == 0:
                current_year -=1
                if current_year > 2021:
                    current_week = 18
                elif current_year == 1987:
                    current_week = 16
                elif current_year == 1982:
                    current_week = 10
                elif current_year > 1977:
                    current_week = 17
                else:
                    current_week = 15
        except:
            print("Error found")
            return matchups
    return matchups


def get_Spread_Info(matches):
    total = len(matches)
    favorite_covers = 0
    spread_avg = 0
    for game in matches:
        spread = game[6].split()[1]
        score = game[5]
        spread_hit = get_Score_Difference(score) + float(spread)
        spread_avg += spread_hit
        if spread_hit > 0:
            favorite_covers += 1
        elif spread_hit == 0:
            favorite_covers += 0.5
    
    parts = [] 
    parts.append(f"Favorite vs spread: {favorite_covers} wins out of {total}")
    parts.append(f"Favorite covers spread {((favorite_covers/total)*100):.2f}%")
    spread_avg /= total
    if spread_avg < 0:
        parts.append(f"Favorite misses spread by average of {abs(spread_avg):.2f}")
    else:
        parts.append(f"Favorite covers spread by average of {spread_avg:.2f}")
    
    summary = "\n".join(parts)
    return summary
    

def get_Over_Under_Percentage(matches):
    total = len(matches)
    average_score = 0
    overs = 0
    unders = 0
    over_margins = []
    under_margins = []
    for game in matches:
        total_score = combine_record(game[5])
        target = float(game[9].split()[1])
        if game[9].startswith("O"):
            overs += 1
            over_margins.append(total_score-target)
        elif game[9].startswith("U"):
            unders += 1
            under_margins.append(target -total_score)
        average_score += total_score
    if len(over_margins) > 0:    
        average_o = sum(over_margins) / len(over_margins)
    else:
        average_o = 0
    if len(under_margins) > 0:
        average_u = sum(under_margins) / len(under_margins)
    else: average_u = 0
    average_score = average_score/len(matches) 
    
    parts = [] 
    parts.append(f"Over Margins Avg: {average_o}\nUnder Margins Avg: {average_u}")
    parts.append(f"Average Score: {average_score}")
    parts.append(f"Overs: {overs} Out of {total} games {((overs/total)*100):.2f}%")
    parts.append(f"Unders: {unders} Out of {total} games {((unders/total)*100):.2f}%")
    
    summary = "\n".join(parts)
    return summary
    
def get_Win_Percentage(matches):
    total = len(matches)
    Team_1 = matches[0][4]
    Team_2 = matches[0][8]
    T1_wins = 0
    T2_wins = 0
    for game in matches:
        winner = game[5].split()[0]
        if game[4] == Team_1:
            if winner == "L":
                T2_wins +=1
            else: 
                T1_wins +=1
        else:
            if winner == "W":
                T2_wins += 1
            else: 
                T1_wins +=1
    parts = []            
    parts.append(f"{Team_1} won {T1_wins} out of {total}: {((T1_wins/total)*100):.2f}%")
    parts.append(f"{Team_2} won {T2_wins} out of {total}: {((T2_wins/total)*100):.2f}%")
    summary = "\n".join(parts)
    return summary
    
        
matches = getLastMatchups(50, "Carolina Panthers", "New Orleans Saints")

print(get_Win_Percentage(matches))
print(get_Over_Under_Percentage(matches))
print(get_Spread_Info(matches))


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


        