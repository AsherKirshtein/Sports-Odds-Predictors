import psycopg2

# Database connection setup
DB_CONFIG = {
    "dbname": "nfl_db",
    "user": "postgres",
    "password": "your_password",
    "host": "localhost"
}

def get_last_away_game_scores(team_name, amount):
    """Fetch the last 10 home game outcomes with team and opponent scores."""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    location = team_name.split(" ", 3)[:-1]
    if len(location) > 1:
        location = location[0] + location[1]
    else:
        location = location[0]
    print(location)
    # Fetch last 10 home games (team is the favorite)
    cur.execute("""
        SELECT 
            game_date, 
            underdog AS opponent,  -- Since team is home, opponent is always the underdog
            score
        FROM nfl_games
        WHERE location != %s  -- Team must be playing at home
        ORDER BY game_date DESC
        LIMIT %s;
    """, (location, amount,))

    games = cur.fetchall()
    
    cur.close()
    conn.close()

    # Process score to extract team and opponent scores
    formatted_games = []
    for game in games:
        game_date, opponent, score = game
        print(game)
        score = score.lstrip("W")
        score = score.lstrip("L")
        score = score.lstrip("T")

        # Extract team and opponent scores from the "score" field
        try:
            team_score, opponent_score = map(int, score.split('-'))  
        except ValueError:
            team_score, opponent_score = None, None  # Handle cases where the score isn't in "XX-XX" format
        
        formatted_games.append({
            "date": game_date,
            "opponent": opponent,
            "team_score": team_score,
            "opponent_score": opponent_score
        })

    return formatted_games

def get_last_home_game_scores(team_name, amount):
    """Fetch the last 10 home game outcomes with team and opponent scores."""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    location = team_name.split(" ", 3)[:-1]
    if len(location) > 1:
        location = location[0] + location[1]
    else:
        location = location[0]
    print(location)
    cur.execute("""
        SELECT 
            game_date, 
            CASE 
                WHEN favorite = %s THEN underdog 
                ELSE favorite 
            END AS opponent, 
            score
        FROM nfl_games
        WHERE location = %s  -- Team must be playing at home
        ORDER BY game_date DESC
        LIMIT %s;
    """, (team_name, team_name, amount))

    games = cur.fetchall()
    
    cur.close()
    conn.close()

    # Process score to extract team and opponent scores
    formatted_games = []
    for game in games:
        game_date, opponent, score = game
        score = score.lstrip("W")
        score = score.lstrip("L")
        score = score.lstrip("T")

        # Extract team and opponent scores from the "score" field
        try:
            team_score, opponent_score = map(int, score.split('-'))  
        except ValueError:
            team_score, opponent_score = None, None  # Handle cases where the score isn't in "XX-XX" format
        
        formatted_games.append({
            "date": game_date,
            "opponent": opponent,
            "team_score": team_score,
            "opponent_score": opponent_score
        })

    return formatted_games

def get_last_game_scores(team_name, amount):
    """Fetch the last 10 game outcomes with team and opponent scores."""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Fetch the last 10 games, extracting scores correctly
    cur.execute("""
        SELECT 
            game_date, 
            CASE 
                WHEN favorite = %s THEN underdog 
                ELSE favorite 
            END AS opponent, 
            score
        FROM nfl_games
        WHERE favorite = %s OR underdog = %s
        ORDER BY game_date DESC
        LIMIT %s;
    """, (team_name, team_name, team_name, amount,))

    games = cur.fetchall()
    
    cur.close()
    conn.close()

    # Process score to extract team and opponent scores
    formatted_games = []
    for game in games:
        game_date, opponent, score = game
        score = score.lstrip("W")
        score = score.lstrip("L")
        score = score.lstrip("T")
        # Extract team and opponent scores from the "score" field
        try:
            team_score, opponent_score = map(int, score.split('-'))  
        except ValueError:
            team_score, opponent_score = None, None  # Handle cases where the score isn't in "XX-XX" format
        
        formatted_games.append({
            "date": game_date,
            "opponent": opponent,
            "team_score": team_score,
            "opponent_score": opponent_score
        })

    return formatted_games


# Example Usage:
team = "San Francisco 49ers"
last_10_scores = get_last_away_game_scores(team, 8)

print(last_10_scores)


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


    