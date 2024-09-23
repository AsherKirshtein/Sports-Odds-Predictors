import requests
from lxml import html
from bs4 import BeautifulSoup

url = "https://sportsbook.draftkings.com/leagues/football/nfl?referrer=singular_click_id%3Db048078d-4ce2-4b38-8f4f-239889141b0b"
    
def extract_team_lines_from_url(url):
    # Fetch the HTML content from the URL
    response = requests.get(url)
    response.raise_for_status()  # Ensure we notice bad responses
    html_content = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all team elements and outcome lines
    team_elements = soup.find_all('div', class_='event-cell')
    outcome_lines = soup.find_all('span', class_='sportsbook-outcome-cell__line')

    # Create a list to store the results
    results = []

    # Ensure there are enough outcome lines
    if len(outcome_lines) >= len(team_elements) * 2:
        for i in range(0, len(team_elements), 2):  # Assuming team elements are paired
            team1_element = team_elements[i]
            team2_element = team_elements[i+1]
            
            # Extract the team names
            team1_name = team1_element.find('div', class_='event-cell__name-text').get_text(strip=True)
            team2_name = team2_element.find('div', class_='event-cell__name-text').get_text(strip=True)
            
            # Extract the lines for spreads and totals
            team1_spread_line = outcome_lines[i*2].get_text(strip=True) if i*2 < len(outcome_lines) else 'N/A'
            Over_under = outcome_lines[i*2+1].get_text(strip=True) if i*2+1 < len(outcome_lines) else 'N/A'

            # Append the results
            results.append((team1_name, team1_spread_line, Over_under, team2_name))
            #results.append((team2_name, team2_spread_line, team2_total_line))
    return results

print(extract_team_lines_from_url(url))