#import libraries
from bs4 import BeautifulSoup
import re
import requests

#import classes

from parser_script import Parser
from parser_script import Review_Parser
from parser_script import Book_Parser

from scraper_script import Scraper

#Data Generation Classes

class Review_URL_ID_Data_Collector():

    def __init__(self, min_id, max_id, max_data_points, max_sleep_time, file_name
        self.max_sleep_time = max_sleep_time
        self.id_list = range(min_id, max_id)
        self.base_url = "https://www.goodreads.com/review/show/"

        #counters
        self.review_counter = 0
        self.max_data_points = max_data_points

        #creating scrapers
        self.scraper = Scraper()
        self.parser = Review_Parser()

        #creating log file
        self.datafile = open("file_name"+".csv", "a")
        self.datafile.write("ID, is_URL_valid, review_publication_date")

    def generate_test_url(self):
        self.test_id = random.choices(self.id_list)
        self.test_url = self.base_url + str(test_id)

    def scrape_url(self):
        self.test_scraped_string = self.scraper.url_to_string(self.test_url)

    def sleep(self:)
        self.scraper.sleep(self.max_sleep_time)

    def parse_review(self, review):
        self.test_soup = self.parser.html_to_soup(self.test_scraped_string)
        self.is_test_valid = self.parser.review_soup_is_valid(self.test_soup)

        if self.is_test_valid:
            self.test_date = self.parser.review_soup_to_date(self.test_soup)
        else:
            self.test_date = None

    def log_data(self):
        self.datafile.write("{},{},{}".format(str(self.test_id), self.is_test_valid, self.test_date)

        self.review_counter += 1

    def data_collection_loop(self):
        while self.review_counter < self.max_data_points:
            self.generate_test_url()
            self.scrape_url()
            self.parse_review()
            self.log_data()
            self.sleep()

        self.datafile.close()
        print("Data Collection Complete")
