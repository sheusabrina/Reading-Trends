#import libraries
from bs4 import BeautifulSoup
import re
import requests

#import classes

from parser_script import Parser
from parser_script import Review_Parser
from parser_script import Book_Parser

from scraper_script import Scraper

class Review_URL_ID_Data_Collector():

    def __init__(self, min_id, max_id, max_data_points, max_sleep_time, file_name, save_per_num):
        #basic definitions
        self.id_list = range(min_id, max_id)
        self.base_url = "https://www.goodreads.com/review/show/"

        #counters
        self.review_counter = 0
        self.unsaved_review_counter = 0
        self.save_per_num = save_per_num

        #creating scrapers
        self.scraper = Scraper()
        self.parser = Review_Parser()

        #creating log file
        self.datafile = open("file_name"+".csv", "a")

        #figure out how to add first line of csv as:
        #"ID,is_URL_valid,review_date_published"

    def generate_test_url(self):
        self.test_id = random.choices(self.id_list)
        self.test_url = self.base_url + str(test_id)

    def scrape_url(self):
        pass

    def parse_review(self, review):
        pass

    def log_data(self):
        ## Add data to csv
        ## Data should look like this:
            #"ID1,TRUE,11/28/2020"
            #"ID2,FALSE,""

        ##incremental counters

        self.review_counter += 1
        self.unsaved_review_counter +=1

        #maybe save?

        if unsaved_review_counter % self.save_per_num:
            #save file
            self.unsaved_review_counter = 0

    def data_collection_loop(self):
        pass
