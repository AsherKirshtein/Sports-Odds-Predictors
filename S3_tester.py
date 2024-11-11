import requests

# API Gateway URL
url = "https://qp0wc17832.execute-api.us-east-2.amazonaws.com/default/sports_Predictor"

# Parameters to be passed in the query string
params = {
    "team1": "Pittsburgh Steelers",
    "team2": "Washington Commanders"
}

# Make a GET request
response = requests.get(url, params=params)

# Check if the response is successful
if response.status_code == 200:
    print("Success! Here's the response data:")
    print(response.json())  # Parse and print JSON response
else:
    print(f"Failed with status code {response.status_code}")
    print(response.text)  # Print error message