#HOW TO USE SLAVE:
    #MAKE SURE THAT MASTER SCRIPT IS ALREADY RUNNING
    #INIT SLAVE WITH REST API HOST & PORT (MASTER'S COMPUTER)
    #CALL KICKOFF

#import libraries
from bs4 import BeautifulSoup
import requests
import queue
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

    def request_chunk(self):

        chunk_response = requests.get(self.api_url)

        if self.is_chunk_none(chunk_response):
            self.active = False

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

        while self.active or (not self.data_strings_queue.empty()):

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

    def data_scraping_loop(self):

        while self.active:

            if not self.id_queue.empty():
                id = self.id_queue.get()
                self.id_to_soup_tuple(id)
                self.id_queue.task_done()

            else:
                self.request_chunk()

    def data_parsing_loop(self):

        while self.active or (not self.soup_tuple_queue.empty()):
            self.parse()

    def kickoff(self):

        #GIVE SERVER TIME TO START UP
        print("Slave Sleeping...")
        time.sleep(40)
        print("Slave Kicking Off...")

        #BACKGROUND THREADS
        self.active = True
        active_threads = []

        for method in [self.data_scraping_loop, self.data_parsing_loop, self.data_transmission_loop]:
            thread = threading.Thread(target = method, daemon = True)
            active_threads.append(thread)
            thread.start()

        #BLOCK IN MAIN THREAD

        while self.active:
            time.sleep(1)

        for thread in active_threads:
            thread.join()

        print("Data Collected. Terminating.")

class Review_Slave(Slave):

    def __init__(self, max_sleep_time, host, port):
        super().__init__(max_sleep_time, host, port)

        self.api_url = "http://{}:{}/api_review".format(self.host, self.port)
        self.base_url = "https://www.goodreads.com/review/show/"
        self.parser = Review_Parser()

    def parse(self):

        if not self.soup_tuple_queue.empty():

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

        self.api_url = "http://{}:{}/api_book".format(self.host, self.port)
        self.base_url = "https://www.goodreads.com/book/show/"
        self.parser = Book_Parser()

    def parse(self):

        if not self.soup_tuple_queue.empty():

            soup_tuple = self.soup_tuple_queue.get()
            id, soup = soup_tuple[0], soup_tuple[1]

            author = self.parser.book_soup_to_author(soup)
            language = self.parser.book_soup_to_language(soup)
            num_reviews = self.parser.book_soup_to_num_reviews(soup)
            num_ratings = self.parser.book_soup_to_num_ratings(soup)
            avg_rating = self.parser.book_soup_to_avg_rating(soup)
            isbn13 = self.parser.book_soup_to_isbn13(soup)
            editions_href = self.parser.book_soup_to_editions_href(soup)
            publication_date = self.parser.book_soup_to_publication_date(soup)
            first_publication_date = self.parser.book_soup_to_first_publication_date(soup)
            series = self.parser.book_soup_to_series(soup)

            data_string = "{},{},{},{},{},{},{},{},{},{},{}".format(id, author, num_reviews, num_ratings, avg_rating, isbn13, editions_href, publication_date, first_publication_date, series)

            self.data_strings_queue.put(data_string)
            self.soup_tuple_queue.task_done()
            
#TESTING
#host, port = "localhost", 8080

#test_slave = Review_Slave(1, host, port)
#test_slave.kickoff()
