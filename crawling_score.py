import os
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def crawlingTeamScore():
    driver = webdriver.Chrome() 
    driver.get('https://www.koreabaseball.com/Default.aspx')
    time.sleep(3)

    away_team = []
    home_team = []
    away_score = []
    home_score = []
    for i in range(0,5):
        away_team = driver.find_element(By.XPATH, f'//*[@id="LiveRelay"]/div[1]/div[3]/div/div[1]/ul/li[{i}]/div/div[2]/div[2]/div[1]/div[1]/img').get_attribute("alt")
        home_team = driver.find_element(By.XPATH, f'//*[@id="LiveRelay"]/div[1]/div[3]/div/div[1]/ul/li[{i}]/div/div[2]/div[2]/div[3]/div[1]/img').get_attribute("alt")
        away_score = driver.find_element(By.XPATH, f'//*[@id="LiveRelay"]/div[1]/div[3]/div/div[1]/ul/li[{i}]/div/div[2]/div[2]/div[1]/div[2]').text
        home_score = driver.find_element(By.XPATH, f'//*[@id="LiveRelay"]/div[1]/div[3]/div/div[1]/ul/li[{i}]/div/div[2]/div[2]/div[3]/div[2]').text

    return away_team, home_team, away_score, home_score

