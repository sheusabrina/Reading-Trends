#HOW TO USE SLAVE:
    #MAKE SURE THAT MASTER SCRIPT IS ALREADY RUNNING
    #INIT SLAVE WITH REST API HOST & PORT (MASTER'S COMPUTER)
    #CALL KICKOFF

#import libraries
from bs4 import BeautifulSoup
import requests
import sys
import time

#import classes
from parser_script import Review_Parser, Book_Parser
from scraper_script import Scraper

class Slave_Methods():

    def __init__(self, max_sleep_time, host, port):

        self.scraper = Scraper()
        self.max_sleep_time = max_sleep_time

        self.host = host
        self.port = port

    def request_chunk(self):

        chunk_response = requests.get("http://{}:{}/api".format(self.host, self.port))
        self.chunk_id_list = self.convert_chunk(chunk_response)

    def convert_chunk(self, chunk_response):

        chunk = recieved_chunk.content.decode()
        chunk = chunk.split(",")

        chars_to_remove = [",", "[", "]", " "]
        new_chunk = []

        for item in old_chunk:
            for char in chars_to_remove:
                item = item.replace(char,"")

            item = int(item) #DOUBLE CHECK THAT IDS SHOULD BE INTEGERS?
            new_chunk.append(item)

    def transmit_data(self):

        requests.post("http://{}/{}/api", data = {"chunk_data_strings": self.chunk_data_strings_list}).format(self.host, self.port)

    def generate_current_url(self):
        self.current_url = self.base_url + str(self.current_id)

    def scrape_url(self):

        self.current_webpage_as_string = self.scraper.url_to_string_content(self.current_url)

    def generate_soup(self):

        self.current_soup = self.parser.html_to_soup(self.current_webpage_as_string)

        if self.parser.is_soup_populated(self.current_soup): #IF THE SOUP IS POPULATED, WE'RE ALL SET
            return

        #IF THE SOUP ISN'T POPULATED, RETRY WITH INCREASING WAITTIMES
        num_invalid_responses_recieved = 0

        while self.parser.is_soup_populated(self.current_soup) == False:

            pausetime = max(self.max_sleep_time, num_invalid_responses_recieved*60) #IF IT'S THE FIRST ERROR, REGULAR SLEEPTIME. FOR SUBSEQUENT ERRORS, INCREASINGLY LARGE WAIT TIMES.
            time.sleep(pausetime)
            num_invalid_responses_recieved += 1

            self.current_soup = self.parser.html_to_soup(self.current_webpage_as_string)

    def log_data(self): #MINION KEEPS DATA AS A LIST OF STRINGS
        self.chunk_data_strings_list.append(self.current_data_string)

    def sleep(self):

        self.scraper.sleep(self.max_sleep_time)

    def parse(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def generate_data_string(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

class Slave(Slave_Methods):

    def collect_data_chunk(self):

        for id in self.chunk_id_list:
            self.current_id = id
            self.generate_current_url()
            self.scrape_url()
            self.generate_soup()
            self.parse()
            self.log_data()
            self.sleep()

    def kickoff(self): #DATA COLLECTION LOOP
        self.request_chunk()

        while self.chunk_key_list():
            self.collect_data_chunk()
            self.transmit_data()
            self.request_chunk()

        sys.exit() #WHEN MASTER STOPS DISTRIBUTING CHUNKS, TERMINATE

class Review_Slave(Slave):

    def __init__(self, max_sleep_time, host, port):
        super().__init__(max_sleep_time, host, port)

        self.base_url = "https://www.goodreads.com/review/show/"
        self.parser = Review_Parser()

    def parse(self):

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

    def generate_data_string(self):

        self.current_data_string = data = "{},{},{},{},{},{},{},{},{},{}".format(self.current_id, self.is_currnet_valid, self.current_date, self.current_book_title, self.current_book_id, self.current_rating, self.current_reviewer_href, self.current_start_date, self.current_finished_date, self.current_shelved_date)

class Book_Slave(Slave):

    def __init__(self, max_sleep_time, host, port):
        super().__init__(max_sleep_time, host, port)

        self.base_url = "https://www.goodreads.com/review/show/"
        self.parser = Review_Parser()
