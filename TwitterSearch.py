'''Advanced Twitter Search'''

from bs4 import BeautifulSoup
import time
from csv import DictWriter
import pprint
import datetime
from datetime import date, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def init_driver(driver_type):
    if driver_type==1:
        driver=webdriver.Chrome()
    elif driver_type==2:
        driver=webdriver.Firefox()
    elif driver_type==3:
        driver=webdriver.Ie()
    elif driver_type==4:
        driver=webdriver.Opera()
    elif driver_type==5:
        driver=webdriver.PhantomJS()

    driver.wait=WebDriverWait(driver,5)
    return driver

def scroll(driver,start_date,end_date,words,max_time=4):
    url="https://twitter.com/search?l=en&q="
    for w in words[:-1]:
        url+="{}%2C%20OR%20".format(w)
    url+="{}%20".format(words[-1])
    url+="since%3A{}%20until%3A{}&src=typd".format(start_date,end_date)

    print(url)
    driver.get(url)

    '''To bound infinite scrolling to max time'''
    start_time=time.time()
    while(time.time()-start_time)<max_time:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    return driver

def scrape_tweets(driver):
    try:

        tweet_divs=driver.page_source
        obj=BeautifulSoup(tweet_divs,"html.parser")
        content=obj.find_all("div",class_="content")
        dates=[]
        names=[]
        tweet_texts=[]
        for i in content:
            
            date=(i.find_all("span",class_="_timestamp")[0].string).strip()
            
            try:
                name=(i.find_all("strong",class_="fullname")[0].string).strip()
            except AttributeError:
                name="Anonymous"

            tweet=i.find("p",class_="tweet-text").strings
            tweets="".join(tweet)

            dates.append(date)
            names.append(name)
            tweet_texts.append(tweets)

            #print("{}				{}					{}".format(name, date, tweets))

        data={"date":dates,"name":names,"tweet":tweet_texts}
        #print(data)
        make_csv(data)

    except Exception:
        
        print("Something went wrong!")
        driver.quit()

def make_csv(data):
    
    l=len(data['date'])
    print('Count:%d'%l)

    with open("twitterData.csv","a+") as file:
        #print("Opened File")
        fieldnames=['Date','Name','Tweets']
        writer=DictWriter(file,fieldnames=fieldnames)
        writer.writeheader()
        for i in range(l):
            #print(data['date'][i],data['name'][i],data['tweet'][i])
            writer.writerow({'Date': data['date'][i],'Name': data['name'][i],'Tweets': data['tweet'][i]})
    #print('Written to file')

def get_all_dates(start,end):
    dates=[]
    start=datetime.datetime.strptime(start,"%Y-%m-%d")
    end=datetime.datetime.strptime(end,"%Y-%m-%d")
    step=timedelta(days=1)
    while start<=end:
        dates.append(str(start.date()))
        start+=step
    return dates

def main():
    print("Welcome to Twitter Search")
    print("Availabe Drivers:-\n1. Chrome\n2. Firefox\n3. IE\n4. Opera\n5. PhantomJS")
    drivertype=int(input('Choose any browser: '))
    wordsToSearch=input('Enter words to be searched: ').split()
    print(wordsToSearch)

    start_date = input("Enter the start date in (Y-M-D): ")
    end_date = input("Enter the end date in (Y-M-D): ")
    all_dates = get_all_dates(start_date, end_date)
    print(all_dates)

    for i in range(len(all_dates)-1):
        driver=init_driver(drivertype)
        scroll(driver,str(all_dates[i]),str(all_dates[i+1]),wordsToSearch)
        scrape_tweets(driver)
        time.sleep(5)
        print("The tweets for {} are scraped!".format(all_dates[i]))
        driver.quit()
    
    
if __name__=="__main__":
    main()
    
