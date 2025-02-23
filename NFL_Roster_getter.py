from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import os
import csv
from datetime import datetime
import re

def get_all_links(url):
    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in headless mode
    
    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the URL
    driver.get(url)

    try:
        # Find ALL matching div containers dynamically
        containers = driver.find_elements(By.XPATH, '//main/div[8]/div[1]/div')  # More general XPath

        all_links = []

        # Loop through each container and extract links
        for container in containers:
            links = container.find_elements(By.TAG_NAME, "a")  # Find all <a> tags inside
            for link in links:
                href = link.get_attribute("href")
                if href:
                    all_links.append(href)

        # Print all extracted links
        print("Extracted Links:")
        for link in all_links:
            print(link)

    except Exception as e:
        print(f"Error fetching links: {e}")

    # Close the browser
    driver.quit()

# Example Usage
url = "https://www.ourlads.com/nfldepthcharts/"
get_all_links(url)
