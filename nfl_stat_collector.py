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

def get_All_Player_data():
    for letter in range(97, 123):  # ASCII values of 'a' to 'z'
        url_letter = chr(letter)
        url = f'https://www.profootballarchives.com/nflplayers-{url_letter}.html' 
        print(url) 
        
get_All_Player_data()