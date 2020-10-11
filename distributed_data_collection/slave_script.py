data_transmission_loop#HOW TO USE SLAVE:
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
        self.data_strings_queue = queue.Queue(maxsize=0)

        self.host = host
        self.port = port

        self.is_data_needed = True

    def request_chunk(self):

        chunk_response = requests.get("http://{}:{}/api".format(self.host, self.port))
        self.chunk_id_list = self.convert_chunk(chunk_response)

    def convert_chunk(self, chunk_response):

        old_chunk = chunk_response.content.decode()
        old_chunk = old_chunk.split(",")

        chars_to_remove = [",", "[", "]", " "]
        new_chunk = []

        for item in old_chunk:
            for char in chars_to_remove:
                item = item.replace(char,"")

            item = int(item)
            new_chunk.append(item)

        return new_chunk

    def data_transmission_loop(self):

        if not self.data_strings_queue.empty():
            data_string = self.data_strings_queue.get()
            requests.post("http://{}/{}/api", data = {"data_string": data_string}).format(self.host, self.port)
            self.data_strings_queue.task_done()

        self.data_transmission_loop()

    def generate_url(self):
        self.url = self.base_url + str(self.id)

    def scrape_url(self):

        self.webpage_as_string = self.scraper.url_to_string_content(self.url)

    def generate_soup(self):

        self.soup = self.parser.html_to_soup(self.webpage_as_string)

        if self.parser.is_soup_populated(self.soup): #IF THE SOUP IS POPULATED, WE'RE ALL SET
            return

        #IF THE SOUP ISN'T POPULATED, RETRY WITH INCREASING WAITTIMES
        num_invalid_responses_recieved = 0

        while self.parser.is_soup_populated(self.soup) == False:

            pausetime = max(self.max_sleep_time, num_invalid_responses_recieved*60) #IF IT'S THE FIRST ERROR, REGULAR SLEEPTIME. FOR SUBSEQUENT ERRORS, INCREASINGLY LARGE WAIT TIMES.
            time.sleep(pausetime)
            num_invalid_responses_recieved += 1

            self.soup = self.parser.html_to_soup(self.webpage_as_string)

    def log_data(self):
        self.data_strings_queue.put(self.data_string)

    def sleep(self):

        self.scraper.sleep(self.max_sleep_time)

    def termination_monitoring_loop(self):

        if (not self.is_data_needed) and self.data_strings_queue.empty():
            sys.exit()

        else:
            time.sleep(10*60) #I DON'T WANT TO BE RUNNING THIS CONSTANTLY

        self.termination_monitoring_loop()

    def parse(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def generate_data_string(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

class Slave(Slave_Methods):

    def data_collection_loop(self):
        self.request_chunk()

        while self.chunk_id_list is not None:

            for id in self.chunk_id_list:
                self.id = id
                self.generate_url()
                self.scrape_url()
                self.generate_soup()
                self.parse()
                self.generate_data_string()
                self.log_data()
                self.sleep()

            self.request_chunk()

        self.is_data_needed = False

    def kickoff(self):

        thread_data_collection = threading.Thread(target = self.data_collection_loop()).start()
        thread_data_transmission = threading.Thread(target = self.transmit_data()).start()
        thread_termination_monitoring = threading.Thread(target = self.transmit_data()).start()

class Review_Slave(Slave):

    def __init__(self, max_sleep_time, host, port):
        super().__init__(max_sleep_time, host, port)

        self.base_url = "https://www.goodreads.com/review/show/"
        self.parser = Review_Parser()

    def parse(self):

        self.is_review_valid = self.parser.review_soup_is_review_valid(self.soup)

        if self.is_review_valid:
            self.date = self.parser.review_soup_to_date(self.soup)
            self.book_title = self.parser.review_soup_to_book_title(self.soup)
            self.book_id = self.parser.review_soup_to_book_id(self.soup)
            self.rating = self.parser.review_soup_to_rating(self.soup)
            self.reviewer_href = self.parser.review_soup_to_reviewer_href(self.soup)

            self.progress_dict = self.parser.review_soup_to_progress_dict(self.soup)
            self.start_date = self.parser.progress_dict_to_start_date(self.progress_dict)
            self.finished_date = self.parser.progress_dict_to_finish_date(self.progress_dict)
            self.shelved_date = self.parser.progress_dict_to_shelved_date(self.progress_dict)

        else:
            self.date = None
            self.book_title = None
            self.book_id = None
            self.rating = None
            self.reviewer_href = None
            self.start_date = None
            self.finished_date = None
            self.shelved_date = None

    def generate_data_string(self):

        self.data_string = "{},{},{},{},{},{},{},{},{},{}".format(self.id, self.is_review_valid, self.date, self.book_title, self.book_id, self.rating, self.reviewer_href, self.start_date, self.finished_date, self.shelved_date)

class Book_Slave(Slave):

    def __init__(self, max_sleep_time, host, port):
        super().__init__(max_sleep_time, host, port)

        self.base_url = "https://www.goodreads.com/review/show/"
        self.parser = Review_Parser()

#TESTING
host, port = "localhost", 8080

test_slave = Review_Slave(1, host, port)
test_slave.kickoff()
