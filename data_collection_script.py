#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random

#import classes

from parser_script import Parser
from parser_script import Review_Parser
from parser_script import Book_Parser

from scraper_script import Scraper

#Data Generation Classes

class Review_URL_ID_Data_Collector():

    def __init__(self, min_id, max_id, max_data_points, max_sleep_time, file_name):
        self.max_sleep_time = max_sleep_time
        self.id_list = range(min_id, max_id)
        self.base_url = "https://www.goodreads.com/review/show/"

        #counters
        self.review_counter = 0
        self.max_data_points = max_data_points
        self.progress_percent_next_benchmark = 10

        #creating scrapers
        self.scraper = Scraper()
        self.parser = Review_Parser()

        #creating log file
        self.datafile = open(file_name+".csv", "a")
        self.datafile.write("ID, is_URL_valid, review_publication_date")

    def generate_test_url(self):
        self.test_id = random.choice(self.id_list)
        self.test_url = self.base_url + str(self.test_id)

    def scrape_url(self):
        self.test_scraped_string = self.scraper.url_to_string(self.test_url)

    def sleep(self):
        self.scraper.sleep(self.max_sleep_time)

    def parse_review(self):

        self.test_soup = self.parser.html_to_soup(self.test_scraped_string)
        self.is_test_valid = self.parser.review_soup_is_valid(self.test_soup)

        if self.is_test_valid:
            self.test_date = self.parser.review_soup_to_date(self.test_soup)
        else:
            self.test_date = None

    def log_data(self):
        self.datafile.write("\n{},{},{}".format(str(self.test_id), self.is_test_valid, self.test_date))

        self.review_counter += 1

    def print_progress(self):
        self.percent_complete = 100 * self.review_counter // self.max_data_points
        if self.percent_complete >= self.progress_percent_next_benchmark:
            now = datetime.now()
            now_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("Data Collection {}% Complete at {}".format(str(self.percent_complete), now_string))

            self.progress_percent_next_benchmark +=10

    def data_collection_loop(self):
        print("Beginning Data Collection...")
        while self.review_counter < self.max_data_points:
            self.generate_test_url()
            self.scrape_url()
            self.parse_review()
            self.log_data()
            self.print_progress()
            self.sleep()

        self.datafile.close()

#REVIEW ID COLLECTOR
    #Purpose: collect data to test the assumption that there are roughly 3.5B reviews (seems too high?!) with IDs arranged sequentially by date from 0 upwards.
    #Analytic Plan:
        #Part 1: For valid review IDs, confirm that IDs and publication dates are sequential. Additionally, identify ID cutoffs in order to limit eventual scraping to certain time periods.
        #Part 2: Assess invalid review IDs for patterns in order to better estimate the number of reviews and optimize eventual scraping.

#keeping this low until I am fully confident that this is working as expected.
num_reviews_to_collect = 100000
estimated_num_reviews = int(3.5 * 10 **9)

#Uncomment to run the data collector
review_id_collector = Review_URL_ID_Data_Collector(0, estimated_num_reviews, num_reviews_to_collect, 5, "review_id_data")
review_id_collector.data_collection_loop()
