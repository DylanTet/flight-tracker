from time import sleep, strftime
from random import randint
import pandas as pd
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import smtplib
from email.mime.multipart import MIMEMultipart
import locale
import os

#Setting up the initital driver along with kayak url then going to the Kayak website
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 
driver = wb.Firefox(executable_path="/Users/dylantettemer/Downloads/geckodriver.exe")
sleep(2)

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
        
    a_hours = hours_list[::2]
    a_carrier = carrier_list[::2]
    b_hours = hours_list[1::2]
    b_carrier = carrier_list[1::2]
    
    ### Creating the names of the columns for the dataframe storing all of the flights ###
    cols = (['Out Day', 'Out Time', 'Out Weekday', 'Out Airline', 'Out Cities', 'Out Duration', 'Out Stops', 'Out Stop Cities',
            'Return Day', 'Return Time', 'Return Weekday', 'Return Airline', 'Return Cities', 'Return Duration', 'Return Stops', 'Return Stop Cities',
            'Price'])
    
    flights_df = pd.DataFrame({'Out Day': a_day,
                               'Out Weekday': a_weekday,
                               'Out Duration': a_duration,
                               'Out Cities': a_section_names,
                               'Return Day': b_day,
                               'Return Weekday': b_weekday,
                               'Return Duration': b_duration,
                               'Return Cities': b_section_names,
                               'Out Stops': a_stop_list,
                               'Out Stop Cities': a_stops_list,
                               'Return Stops': b_stop_list,
                               'Return Stop Cities': b_stop_list,
                               'Out Time': a_hours,
                               'Out Airline': a_carrier,
                               'Return Time': b_hours,
                               'Return Airline': b_carrier,                           
                               'Price': prices_list})[cols]
    
    flights_df['timestamp'] = strftime("%Y%m%d-%H%M")
    return flights_df

def start_kayak(city_from, city_to, date_start, date_end):
   
    kayak = ('https://www.kayak.com/flights/' + city_from + '-' + city_to +
             '/' + date_start + '-flexible-3days/' + date_end + '-flexible-3days?sort=bestflight_a')
    driver.get(kayak)
    sleep(randint(60, 95))
    
    try: 
        popup_close = driver.find_element(By.XPATH, '//div[@class="B5la-button"]').click()
    
    except Exception as e:
        pass
    
    print("Loading more...")
    
    load_more()

    try: 
        popup_close = driver.find_element(By.XPATH, '//div[@class="B5la-button"]').click()
    
    except Exception as e:
        pass
    
    print("Starting first scrape...")
    
    df_flights_best = page_scrape()
    df_flights_best['sort'] = 'best'
    sleep(randint(60, 80))
    
    matrix = driver.find_elements(By.XPATH, '//*[contains(@id, "FlexMatrix")]')
    matrix_prices = [price.text.replace('$', '') for price in matrix]
    matrix_prices = list(map(locale.atoi, matrix_prices))
    matrix_min = min(matrix_prices)
    matrix_avg = sum(matrix_prices)/len(matrix_prices)
    
    print('switching to cheapest results...')
    cheap_results = '//a[@data-code = "price"]'
    driver.find_element(By.XPATH, cheap_results).click()
    sleep(randint(60,90))
    print('Loading more....')
    
    load_more()
    
    print('Starting second scrape...')
    df_flights_cheap = page_scrape()
    df_flights_cheap['sort'] = 'cheap'
    sleep(randint(60,80))
    
    print("Switching to quickest results...")
    quick_results = '//a[@data-code = "duration"]'
    driver.find_element(By.XPATH, quick_results).click()  
    sleep(randint(60,90))
    print('loading more.....')
    
    load_more()
    
    print('Starting third scrape...')
    df_flights_fast = page_scrape()
    df_flights_fast['sort'] = 'fast'
    sleep(randint(60,80))
    
    # saving a new dataframe as an excel file. the name is custom made to your cities and dates
    flight_directory = './search_backups'
    if not os.path.exists(flight_directory):
        os.mkdir(flight_directory)
        
    final_df = df_flights_cheap.append(df_flights_best).append(df_flights_fast)
    final_df.to_excel('search_backups//{}_flights_{}-{}_from_{}_to_{}.xlsx'.format(strftime("%Y%m%d-%H%M"),
                                                                                   city_from, city_to, 
                                                                                   date_start, date_end), index=False)
    print('saved df.....')
    
    # We can keep track of what they predict and how it actually turns out!
    xp_loading = '//div[contains(@id,"advice")]'
    loading = driver.find_element(By.XPATH, xp_loading).text
    xp_prediction = '//span[@class="info-text"]'
    prediction = driver.find_element(By.XPATH, xp_prediction).text
    print(loading+'\n'+prediction)
    
    weird = '¯\\_(ツ)_/¯'
    if loading == weird:
        loading = 'Not sure'
    
    username = 'tettemerd@gmail.com'
    password = 'zzpvctquockwknlq'
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)
    msg = ('Subject: Flight Scraper\n\n\
            Cheapest Flight: {}\nAverage Price: {}\n\nRecommendation: {}\n\nEnd of message'.format(matrix_min, matrix_avg, (loading+'\n'+prediction)))
    message = MIMEMultipart()
    message['From'] = 'tettemerd@gmail.com'
    message['to'] = 'tettemerd@gmail.com'
    server.sendmail('tettemerd@gmail.com', 'tettemerd@gmail.com', msg)
    print('sent email.....')

if __name__ == "__main__":
    
    city_from = input("Where are you traveling from? Please input IATA Code:  ")
    city_to = input("Where to? IATA code please:  ")
    date_start = input("Around which departure date? Please input in format YYYY-MM-DD:  ")
    date_end = input("Return when? Format YYYY-MM-DD:  ")
    
    for n in range(0,5):
        start_kayak(city_from, city_to, date_start, date_end)
        
        print('iteration {} was complete @ {}'.format(n, strftime("%Y%m%d-%H%M")))
        
        sleep(60*60*4)
        print("sleep finished...")


    
    
    


