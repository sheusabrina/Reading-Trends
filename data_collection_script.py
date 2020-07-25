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

class Review_Data_Collector:

    def __init__(self, min_id, max_id, max_data_points, max_sleep_time, file_name):
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
        self.datafile = open(file_name+".csv", "a")

    def generate_test_url(self):
        self.test_id = random.choice(self.id_list)
        self.test_url = self.base_url + str(self.test_id)

    def scrape_url(self):
        self.test_scraped_string = self.scraper.url_to_string(self.test_url)

    def sleep(self):
        self.scraper.sleep(self.max_sleep_time)

    def print_progress(self):
        if self.review_counter % 5 == 0:
            percent_complete = round(100 * self.review_counter / self.max_data_points, 2)
            percent_complete_string = str(percent_complete)
            now = datetime.now()
            now_string = now.strftime("%d/%m/%Y %H:%M:%S")

            print("{} / {} Reviews Collected ({}% Complete) at {}". format(str(self.review_counter), str(self.max_data_points), percent_complete_string, now_string))

    def parse_review(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def log_data(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def data_collection_loop(self):
        print("Beginning Data Collection...")
        while self.review_counter < self.max_data_points:
            self.generate_test_url()
            self.scrape_url()
            self.parse_review()
            self.log_data()
            self.print_progress()
            self.sleep()

        print("Data Collection Complete")
        self.datafile.close()

class Review_URL_ID_Data_Collector(Review_Data_Collector):

    def __init__(self, min_id, max_id, max_data_points, max_sleep_time, file_name):

        super().__init__(min_id, max_id, max_data_points, max_sleep_time, file_name)

        self.datafile.write("ID,is_URL_valid,review_publication_date")

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

class Review_Detail_Data_Collector(Review_Data_Collector):

    def __init__(self, min_id, max_id, max_data_points, max_sleep_time, file_name):

        super().__init__(min_id, max_id, max_data_points, max_sleep_time, file_name)

        self.datafile.write("ID,is_URL_valid,review_publication_date,book_title,book_id,rating,reviewer_href")

    def parse_review(self):

        self.test_soup = self.parser.html_to_soup(self.test_scraped_string)
        self.is_test_valid = self.parser.review_soup_is_valid(self.test_soup)

        if self.is_test_valid:
            self.test_date = self.parser.review_soup_to_date(self.test_soup)
            self.test_title = self.parser.review_soup_to_book_title(self.test_soup)
            self.test_book_id = self.parser.review_soup_to_book_id(self.test_soup)
            self.test_rating = self.parser.review_soup_to_rating(self.test_soup)
            self.test_reviewer_href = self.parser.review_soup_to_reviewer_href(self.test_soup)

        else:
            self.test_date = None
            self.test_title = None
            self.test_book_id = None
            self.test_rating = None
            self.test_reviewer_href = None

    def log_data(self):

        self.datafile.write("\n{},{},{},{},{},{},{}".format(str(self.test_id), self.is_test_valid, self.test_date, self.test_book_title, self.test_book_id, self.test_rating, self.test_reviewer_href))

        self.review_counter += 1

#keeping this low until I am fully confident that this is working as expected.
num_reviews_to_collect = 10
estimated_num_reviews = int(3.5 * 10 **9)

#Uncomment to run the data collector
#review_id_collector = Review_URL_ID_Data_Collector(0, estimated_num_reviews, num_reviews_to_collect, 5, "test_scrape")
#review_id_collector.data_collection_loop()
