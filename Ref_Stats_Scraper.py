import requests
from lxml import html



def scrapePage(week):
    url = 'https://www.nflpenalties.com/week/{week}?year=2023'
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        xpath = '/html/body/div[2]/div[4]/div/table/tbody/tr'
        table = tree.xpath(xpath)
        print(table)


scrapePage(1)