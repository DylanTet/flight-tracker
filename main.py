from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart
import locale

#Setting up the initital driver along with kayak url then going to the Kayak website
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 
driver = wb.Firefox(executable_path="/Users/dylantettemer/Downloads/geckodriver.exe")
kayak = "https://www.kayak.com/flights/LAS-PMO/2023-02-06-flexible-3days/2023-02-15-flexible-3days?sort=bestflight_a"
driver.get(kayak)
sleep(2)

# Click on the cheapest price button on the site
cheap_results = '//a[@data-code = "price"]'
driver.find_element(By.XPATH, cheap_results).click()
sleep(30)

# Function to load more flight options on the site
def load_more():
    try:
        more_results = 'a//[@class="moreButton"]'
        driver.find_element(By.XPATH, more_results).click()
        print("Sleeping...")
        sleep(randint(45,60))
    except:
        pass
    

def page_scrape():
    
    xp_sections = '//*[@class="section duration allow-multi-modal-icons"]'
    
    sections = driver.find_elements(By.XPATH, xp_sections)
    sections_list =[value.text for value in sections]
    section_a_list = sections_list[::2]
    section_b_list = sections_list[1::2]
    
    if section_a_list == []:
        print("Exiting...")
        raise SystemExit
    
    # Letter A is for outbound flight and B is for inbound flights
    a_duration = []
    a_section_names = []
    
    for n in section_a_list:
        a_section_names.append(''.join(n.split()[2:5]))
        a_duration.append(''.join(n.split()[0:2]))
        
    
    b_duration = []
    b_section_names = []
    
    for n in section_b_list:
        b_section_names.append(''.join(n.split()[2:5]))
        b_duration.append(''.join(n.split()[0:2]))
        
    xp_dates = '//div[@class="section date"]'
    dates = driver.find_elements(By.XPATH, xp_dates)
    dates_list = [value.text for value in dates]
    a_dates_list = dates_list[::2]
    b_dates_list = dates_list[1::2]
    
    ### Seperating the returned day/number into a standalone date and day of the week
    a_day = [value.split()[0] for value in a_dates_list]
    a_weekday = [value.split()[1] for value in a_dates_list]
    
    b_day = [value.split()[0] for value in b_dates_list]
    b_weekday = [value.split()[1] for value in b_dates_list]
    
    ### Getting the prices for each flight ###
    xp_prices = '//span[@class="price option-text"]'
    prices = driver.find_elements(By.XPATH, xp_prices)
    prices_list = [price.text.replace('$', '') for price in prices if price.text != '']
    prices_list = list(map(locale.atoi, prices_list))

    
    ### The stops are a big list with one leg on the even index and second leg on the odd index
    xp_stops = '//div[@class="section stops"]/div[1]'
    stops = driver.find_elements(By.XPATH, xp_stops)
    stops_list = [stop.text[0].replace('n', '0') for stop in stops]
    a_stops_list = stops_list[::2]
    b_stops_list = stops_list[1::2]
        
    ### Put all of the stop cities into a list ###
    xp_stop_cities = '//div[@class="section stops"]/div[2]'
    stops_cities = driver.find_elements(By.XPATH, xp_stop_cities)
    stops_list = [stop.text for stop in stops_cities]
    a_stop_list = stops_list[::2]
    b_stop_list = stops_list[1::2]
    
    ### Gets all of the airline companies with departure and arrival times for both legs ###
    xp_schedule = '//div[@class="section times"]'
    schedules = driver.find_elements(By.XPATH, xp_schedule)
    hours_list = []
    carrier_list = []
    
    for schedule in schedules:
        hours_list.append(schedule.text.split('\n')[0])
        carrier_list.append(schedule.text.split('\n')[1])
        
    print(carrier_list)
    
page_scrape()




    
    
    


