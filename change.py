from urllib import parse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import csv


PATH = "C:\Program Files (x86)\chromedriver.exe"
BASE_URL = 'https://www.change.org/petitions/'
TAGS = ["victories" , "recent","popular_weekly"]
driver = webdriver.Chrome(PATH)
class Scrape:
    def __init__(self,tag) -> None:
        self.titles =[]
        self.goals = []
        self.signed =[]
        self.more_info = []
        self.url = ""
        self.set_url(tag)
        self.tag = tag
        self.count = 2
        self.saved_values = dict()

    def set_url(self,tag):
        self.url =BASE_URL+'?selected=' + tag


    def parse_values(self):
        self.titles  = driver.find_elements_by_css_selector('h4.mtn')
        self.signed =  driver.find_elements_by_css_selector('#page > div.bg-default > div > div > div > a > div > div.col-xs-12.col-sm-8 > div > p > span > strong')
        self.goals = driver.find_elements_by_css_selector('#page > div.bg-default > div > div > div > a > div > div.col-xs-12.col-sm-8 > div > p > span > span')
        self.more_info = driver.find_elements_by_css_selector('#page > div.bg-default > div > div > div > a > div > div.col-xs-12.col-sm-8 > div > div.hide-overflow > div > p > span > span')

    def save_value(self,title,goal ,signed):
        self.saved_values[title.text] = True
        filename =self.tag+'.csv'
        with open(filename, mode='w') as tfile:
            twriter = csv.writer(tfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

            twriter.writerow([title.text, goal.text, signed.text])
        print(title.text)

    def begin(self):
        driver.get(self.url)
        sleep(8)
        #handle accept cookies
        if len(driver.find_elements_by_xpath('//*[@id="app"]/div[2]/div/div/div/div/div[2]/button')) > 1 :
            driver.find_element_by_xpath('//*[@id="app"]/div[2]/div/div/div/div/div[2]/button').click()
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div[2]/div/div/div/div/div[2]/button')))
        driver.find_element_by_xpath('//*[@id="app"]/div[2]/div/div/div/div/div[2]/button').click()

        
        actions = ActionChains(driver)
        self.parse_values()
        total_values = len(self.titles)

        #initail scan since values are not rendered till they are in view
        for i in range(total_values):
            if self.titles[i] == ' ':
                continue
            self.save_value(self.titles[i],self.goals[i],self.signed[i])
        #renders null values
        while(self.count < len(self.titles)):
            actions.move_to_element(self.titles[self.count]).perform()
            self.parse_values()
            for counter , title in enumerate(self.titles):
                if title.text == '' or title.text in self.saved_values :
                    continue
                self.save_value(title,self.goals[counter], self.signed[counter])
            self.count += 2
        #handle load more
        while len(driver.find_elements_by_class_name("btn")) > 0:
            load_more_button = driver.find_element_by_css_selector("#page > div.bg-default > div > div > div > button")
            actions.move_to_element(load_more_button).perform()
            load_more_button.click()
            sleep(4)

            self.titles =  self.titles + driver.find_elements_by_css_selector('h4.mtn')
            self.signed=   self.signed + driver.find_elements_by_css_selector('#page > div.bg-default > div > div > div > a > div > div.col-xs-12.col-sm-8 > div > p > span > strong')
            self.goals =  self.goals + driver.find_elements_by_css_selector('#page > div.bg-default > div > div > div > a > div > div.col-xs-12.col-sm-8 > div > p > span > span')
            self.more_info = self.more_info +  driver.find_elements_by_css_selector('#page > div.bg-default > div > div > div > a > div > div.col-xs-12.col-sm-8 > div > div.hide-overflow > div > p > span > span')
     
            while(self.count < len(self.titles)):
                actions.move_to_element(self.titles[self.count]).perform()
                self.parse_values()
                for counter , title in enumerate(self.titles):
                    if title.text == '' or title.text in self.saved_values :
                        continue
                    self.save_value(title,self.goals[counter], self.signed[counter])
                self.count += 2





if  __name__ == '__main__':
    for tag in TAGS:
        scrape =  Scrape(tag)
    scrape.begin()