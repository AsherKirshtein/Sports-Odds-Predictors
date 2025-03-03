import psycopg2
import matplotlib.pyplot as plt

# Database connection setup
DB_CONFIG = {
    "dbname": "nfl_db",
    "user": "postgres",
    "password": "password",
    "host": "localhost"
}

def get_windy_game_results():
    """Fetches the count of wins and losses in windy games (wind > 30 mph)."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Query for wins in windy games
    cur.execute("""
        SELECT COUNT(*) FROM nfl_games g
        JOIN weather_data w ON g.game_date = w.weather_date
        WHERE w.wind_speed > 30 AND g.spread_result = 'Win';
    """)
    wins = cur.fetchone()[0]

    # Query for losses in windy games
    cur.execute("""
        SELECT COUNT(*) FROM nfl_games g
        JOIN weather_data w ON g.game_date = w.weather_date
        WHERE w.wind_speed > 30 AND g.spread_result = 'Loss';
    """)
    losses = cur.fetchone()[0]

    cur.close()
    conn.close()

    return wins, losses

def get_windy_game_over_under():
    """Fetches the count of 'Over' and 'Under' results in windy games."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Query to get over/under results in windy games
    cur.execute("""
    SELECT g.over_under_result AS result, COUNT(*) AS total_games
    FROM nfl_games g
    JOIN (
        SELECT weather_date, AVG(wind_speed) AS avg_wind_speed
        FROM weather_data
        GROUP BY weather_date
    ) w ON g.game_date = w.weather_date
    WHERE w.avg_wind_speed > 10
    GROUP BY g.over_under_result;
    """)


    results = cur.fetchall()
    cur.close()
    conn.close()

    # Convert query results into a dictionary
    result_dict = {row[0]: row[1] for row in results}

    over_count = result_dict.get("Over", 0)
    under_count = result_dict.get("Under", 0)

    print(f"Over hit in windy games: {over_count}")
    print(f"Under hit in windy games: {under_count}")

    return over_count, under_count


def plot_windy_game_results(wins, losses):
    """Plots a bar chart comparing wins vs. losses in windy games."""
    categories = ["Wins", "Losses"]
    values = [wins, losses]

    plt.figure(figsize=(6, 4))
    plt.bar(categories, values, color=['green', 'red'])
    plt.xlabel("Spread Result")
    plt.ylabel("Number of Games")
    plt.title("Wins vs. Losses in Windy Games (Wind Speed > 30 mph)")
    plt.show()


get_windy_game_over_under()
