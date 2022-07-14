# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 13:41:50 2022

@author: DE001E02544
"""
from msedge.selenium_tools import Edge
from msedge.selenium_tools import EdgeOptions
import pandas as pd
import logging
import time
import _pickle as cPickle
import traceback
class hopsital_scraper():
    
    def __init__(self):
        pass
    
    def get_hospital_list(self):
        self.logger.info("Get Data List.")
        edge_options = EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_argument('disable-gpu')
        driver = Edge(executable_path="..\webdriver\msedgedriver.exe",options=edge_options)
        driver.maximize_window()
        loop = True
        driver.get("https://www.deutsches-krankenhaus-verzeichnis.de/app/suche")
        driver.find_element_by_id("search_send").click()
        time.sleep(2)
        driver.find_element_by_id("js_search").click()
        link_list = []
        
        while loop ==True:
           link_list_current_page = driver.find_element_by_id("dkv_result_table_row").find_elements_by_tag_name("tr")
           for link in link_list_current_page:
               link = link.find_elements_by_tag_name("td")[0].find_element_by_tag_name("a").get_attribute("href")
               link_list.append(link)
           try:
                button = driver.find_element_by_xpath("//*[@id='pagination']/ul/li/a[contains(text(),'Weiter')]")
                driver.execute_script("arguments[0].click();", button)
                time.sleep(2)
           except Exception as e:
                loop = False
        driver.quit()
        return link_list
    def get_data(self):
        result_dataset = []
        
        #link_list = self.get_hospital_list()
        with open("list.pickle",'rb') as fp:
            link_list= cPickle.load(fp)
        edge_options = EdgeOptions()
        edge_options.use_chromium = True
        edge_options.add_argument('disable-gpu')
        edge_options.add_argument("headless")
        driver = Edge(executable_path="..\webdriver\msedgedriver.exe",options=edge_options)
        driver.maximize_window()
        i = 0
        logger = logging.Logger('Hospital')
        fh = logging.FileHandler("../log/hospital.log")
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
        for link in link_list:
            i += 1
            logger.info("Get Object " + str(i) + " of " + str(len(link_list)))
            print("Get Object " + str(i) + " of " + str(len(link_list)))
            try:
                driver.get(link)
                time.sleep(2)
                name = driver.find_element_by_tag_name("h1").get_attribute("innerHTML").lower()
                street = driver.find_element_by_class_name("col-sm-8").find_elements_by_tag_name("p")[0].get_attribute("innerHTML").lower().split("<br>")[0].rstrip().lstrip()
                zip_code = driver.find_element_by_class_name("col-sm-8").find_elements_by_tag_name("p")[0].get_attribute("innerHTML").lower().split("<br>")[1].split(" ")[0].rstrip().lstrip()
                city = driver.find_element_by_class_name("col-sm-8").find_elements_by_tag_name("p")[0].get_attribute("innerHTML").lower().split("<br>")[1].split(" ")[1].rstrip().lstrip()
                result_dataset.append({'name':name,'street':street,'zip_code':zip_code,'city':city})
                result_frame = pd.DataFrame(result_dataset)
                result_frame.to_csv(path_or_buf='../result/hospital_list.csv',index=False,encoding='utf-8')
            except Exception as e:
                logger.error("Error getting data from " + link)
                logger.error(traceback.format_exc())
        driver.quit()
h_s = hopsital_scraper()
h_s.get_data()