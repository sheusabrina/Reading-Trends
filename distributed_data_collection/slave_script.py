#HOW TO USE SLAVE:
    #MAKE SURE THAT MASTER SCRIPT IS ALREADY RUNNING
    #INIT SLAVE WITH REST API HOST & PORT (MASTER'S COMPUTER)
    #CALL KICKOFF

#import libraries
from bs4 import BeautifulSoup
import requests
import queue
import sys
import time
import threading

#import classes
from parser_script import Review_Parser, Book_Parser
from scraper_script import Scraper

class Slave_Methods():

    def __init__(self, max_sleep_time, host, port):

        self.scraper = Scraper()
        self.max_sleep_time = max_sleep_time
        self.id_queue = queue.Queue(maxsize=0)
        self.soup_tuple_queue = queue.Queue(maxsize=0)
        self.data_strings_queue = queue.Queue(maxsize=0)

        self.host = host
        self.port = port
        self.api_url = "http://{}:{}/api".format(self.host, self.port)

        self.is_data_needed = True

    def request_chunk(self):

        chunk_response = requests.get(self.api_url)

        if self.is_chunk_none(chunk_response):
            self.is_data_needed = False

        else:
            chunk_id_list = self.convert_chunk(chunk_response)
            for id in chunk_id_list:
                self.id_queue.put(id)

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

        while True: #INFINITE LOOP, BUT IT ENDS WHEN THE PROGRAM DOES

            if not self.data_strings_queue.empty():

                data_string = self.data_strings_queue.get()
                requests.post(self.api_url, data = {"data_string": data_string})
                self.data_strings_queue.task_done()

    def id_to_soup_tuple(self, id):
        url = self.base_url + str(id)
        webpage_as_string = self.scraper.url_to_string_content(url)
        soup = self.parser.html_to_soup(webpage_as_string)

        if not self.parser.is_soup_populated(soup): #IF RESPONSE IS INVALID
            num_invalid_responses_recieved = 0

            while self.parser.is_soup_populated(soup) == False:

                pausetime = max(self.max_sleep_time, num_invalid_responses_recieved*60) #IF IT'S THE FIRST ERROR, REGULAR SLEEPTIME. FOR SUBSEQUENT ERRORS, INCREASINGLY LARGE WAIT TIMES.
                time.sleep(pausetime)
                num_invalid_responses_recieved += 1

                soup = self.parser.html_to_soup(webpage_as_string)

        tuple = (id, soup)
        self.soup_tuple_queue.put(tuple)

    def sleep(self):

        self.scraper.sleep(self.max_sleep_time)

    def termination_monitoring_loop(self):

        terminate = False

        while terminate == False:

            if (not self.is_data_needed) and self.data_strings_queue.empty():
                terminate = True

            else:
                time.sleep(10*60)

        sys.exit()

    def is_chunk_none(self, chunk):

        chunk = chunk.content.decode()

        if chunk == "":
            return True
        else:
            return False

    def parse(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def generate_data_string(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

class Slave(Slave_Methods):

    def data_collection_loop(self):

        while self.is_data_needed:

            if self.id_queue.empty():
                self.request_chunk()

            else:
                id = self.id_queue.get()
                self.id_to_soup_tuple(id)
                self.id_queue.task_done()

    def data_parsing_loop(self):

        while True: #INFINITE LOOP, BUT IT ENDS WHEN THE PROGRAM DOES

            if not self.soup_tuple_queue.empty():
                self.parse()

    def kickoff(self):

        time.sleep(30) #SEE IF THE DELAY SOLVES THE ACTIVE REFUSAL ERROR

        thread_data_collection = threading.Thread(target = self.data_collection_loop).start()
        thread_data_parsing = threading.Thread(target = self.data_parsing_loop).start()
        thread_termination_monitoring = threading.Thread(target = self.termination_monitoring_loop).start()
        thread_data_transmission = threading.Thread(target = self.data_transmission_loop).start()

class Review_Slave(Slave):

    def __init__(self, max_sleep_time, host, port):
        super().__init__(max_sleep_time, host, port)

        self.base_url = "https://www.goodreads.com/review/show/"
        self.parser = Review_Parser()

    def parse(self):

        soup_tuple = self.soup_tuple_queue.get()
        id, soup = soup_tuple[0], soup_tuple[1]

        is_review_valid = self.parser.review_soup_is_valid(soup)

        if is_review_valid:
            date = self.parser.review_soup_to_date(soup)
            book_title = self.parser.review_soup_to_book_title(soup)
            book_id = self.parser.review_soup_to_book_id(soup)
            rating = self.parser.review_soup_to_rating(soup)
            reviewer_href = self.parser.review_soup_to_reviewer_href(soup)

            progress_dict = self.parser.review_soup_to_progress_dict(soup)
            start_date = self.parser.progress_dict_to_start_date(progress_dict)
            finished_date = self.parser.progress_dict_to_finish_date(progress_dict)
            shelved_date = self.parser.progress_dict_to_shelved_date(progress_dict)

        else:
            date = None
            book_title = None
            book_id = None
            rating = None
            reviewer_href = None
            start_date = None
            finished_date = None
            shelved_date = None

        data_string = "{},{},{},{},{},{},{},{},{},{}".format(id, is_review_valid, date, book_title, book_id, rating, reviewer_href, start_date, finished_date, shelved_date)
        self.data_strings_queue.put(data_string)

        self.soup_tuple_queue.task_done()

class Book_Slave(Slave):

    def __init__(self, max_sleep_time, host, port):
        super().__init__(max_sleep_time, host, port)

        self.base_url = "https://www.goodreads.com/review/show/"
        self.parser = Review_Parser()

#TESTING
host, port = "localhost", 8080

test_slave = Review_Slave(1, host, port)
test_slave.kickoff()
