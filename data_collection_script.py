#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd

#import classes

from parser_script import Parser
from parser_script import Review_Parser
from parser_script import Book_Parser

from scraper_script import Scraper

#Data Generation Classes

class Data_Collector():

    def __init__(max_sleep_time, file_name):

        self.max_sleep_time = max_sleep_time

        self.data_points_counter = 0
        self.log_file_name = file_name + ".csv"
        self.scraper = Scraper()

    def is_csv(self):

        try:
            df = pd.read_csv(self.log_file_name)
            is_csv = True

        except (FileNotFoundError, pd.errors.EmptyDataError):
            is_csv = False

        return is_csv

class Review_Data_Collector(Data_Collector):

    def __init__(self, min_id, max_id, max_data_points, max_sleep_time, file_name):

        super().__init__(max_sleep_time, file_name)

        #Specifics for Review Data Collection
        self.id_list = range(min_id, max_id)
        self.base_url = "https://www.goodreads.com/review/show/"

        #counter
        self.max_data_points = max_data_points

        #Review Parser
        self.parser = Review_Parser()

    def open_log_file(self):

        self.datafile = open(self.log_file_name, "a")

    def add_headers_to_log_file(self):

        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def generate_current_url(self):
        self.current_id = random.choice(self.id_list)
        self.current_url = self.base_url + str(self.current_id)

    def scrape_url(self):

        self.current_scraped_string = self.scraper.url_to_string(self.current_url)

    def sleep(self):
        self.scraper.sleep(self.max_sleep_time)

    def print_progress(self):
        if self.data_points_counter % 5 == 0:
            percent_complete = round(100 * self.data_points_counter / self.max_data_points, 2)
            percent_complete_string = str(percent_complete)
            now = datetime.now()
            now_string = now.strftime("%d/%m/%Y %H:%M:%S")

            print("{} / {} Reviews Collected ({}% Complete) at {}". format(str(self.data_points_counter), str(self.max_data_points), percent_complete_string, now_string))

    def parse_review(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def log_data(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def data_collection_loop(self):

        if self.is_csv():
            self.open_log_file()

        else:

            self.open_log_file()
            self.add_headers_to_log_file()

        print("Beginning Data Collection...")
        while self.data_points_counter < self.max_data_points:
            self.generate_current_url()
            self.scrape_url()
            self.parse_review()
            self.log_data()
            self.print_progress()
            self.sleep()

        print("Data Collection Complete")
        self.datafile.close()

class Review_URL_ID_Data_Collector(Review_Data_Collector):

    def add_headers_to_log_file(self):
        self.datafile.write("ID,is_URL_valid,review_publication_date")

    def parse_review(self):

        self.current_soup = self.parser.html_to_soup(self.current_scraped_string)
        self.is_current_valid = self.parser.review_soup_is_valid(self.current_soup)

        if self.is_current_valid:
            self.current_date = self.parser.review_soup_to_date(self.current_soup)
        else:
            self.current_date = None

    def log_data(self):
        self.datafile.write("\n{},{},{}".format(str(self.current_id), self.is_current_valid, self.current_date))

        self.data_points_counter += 1

class Review_Detail_Data_Collector(Review_Data_Collector):

    def add_headers_to_log_file(self):

        self.datafile.write("ID,is_URL_valid,review_publication_date,book_title,book_id,rating,reviewer_href,started_reading_date,finished_reading_date,shelved_date")

    def parse_review(self):

        self.current_soup = self.parser.html_to_soup(self.current_scraped_string)
        self.is_current_valid = self.parser.review_soup_is_valid(self.current_soup)

        if self.is_current_valid:
            self.current_date = self.parser.review_soup_to_date(self.current_soup)
            self.current_book_title = self.parser.review_soup_to_book_title(self.current_soup)
            self.current_book_id = self.parser.review_soup_to_book_id(self.current_soup)
            self.current_rating = self.parser.review_soup_to_rating(self.current_soup)
            self.current_reviewer_href = self.parser.review_soup_to_reviewer_href(self.current_soup)

            self.current_progress_dict = self.parser.review_soup_to_progress_dict(self.current_soup)
            self.current_start_date = self.parser.progress_dict_to_start_date(self.current_progress_dict)
            self.current_finished_date = self.parser.progress_dict_to_finish_date(self.current_progress_dict)
            self.current_shelved_date = self.parser.progress_dict_to_shelved_date(self.current_progress_dict)

        else:
            self.current_date = None
            self.current_book_title = None
            self.current_book_id = None
            self.current_rating = None
            self.current_reviewer_href = None
            self.current_start_date = None
            self.current_finished_date = None
            self.current_shelved_date = None

    def log_data(self):

        self.datafile.write("\n{},{},{},{},{},{},{},{},{},{}".format(str(self.current_id), self.is_current_valid, self.current_date, self.current_book_title, self.current_book_id, self.current_rating, self.current_reviewer_href, self.current_start_date, self.current_finished_date, self.current_shelved_date))

        self.data_points_counter += 1

class Book_Data_Collector(Data_Collector):

    def __init__(self, book_id_list, max_sleep_time, file_name):

        super().__init__(max_sleep_time, file_name)


#keeping this low until I am fully confident that this is working as expected.
num_reviews_to_collect = 5 * 10 **6
estimated_num_reviews = int(3.5 * 10 **9)
num_wait_seconds = 1

min_2017_ID = 1484362322 #I want to actually analyze data from 2018-2020, but I'm pulling 2017 data too just because the ID generation isn't quite linear.
max_2020_ID = 3455207761 #I'm not sure if i should use this, since reviews are going to continue to roll in...

#Uncomment to run the URL generation data collector
#review_id_collector = Review_URL_ID_Data_Collector(0, estimated_num_reviews, num_reviews_to_collect, num_wait_seconds, "test_scrape")
#review_id_collector.data_collection_loop()

#Uncomment to run the Review Detail collector
review_collector = Review_Detail_Data_Collector(min_2017_ID, max_2020_ID, num_reviews_to_collect, num_wait_seconds, "review_data")
review_collector.data_collection_loop()
