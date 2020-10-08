#THIS SCRIPT WILL BE DELETED

#THIS SCRIPT IS AN ATTEMPT TO BUILD A DISTRIBUTED SYSTEM, BUT IT NEEDS TO BE REWORKED TO USE AN HTTP SYSTEM
#I HAVEN'T DEBUGGED IT

#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd
import math
import sys

#import classes

from parser_script import Review_Parser
from parser_script import Book_Parser
from scraper_script import Scraper
from data_classes import Book, Review

##HOW TO USE IN DISTRIBUTED SYSTEM:
    #HAVE ONE SCRIPT WITH BOSS (INIT, INPUT DATA, PREPARE)
    #ALL OTHER SCRIPTS HAVE ONE MINION WHICH REFERENCES BOSS

#REVIEW & BOOK ARE DATA STORAGE NODES:
    #GLORIFIED DICTIONARY
    #MAKE STRING STATEMENTS THAT ALIGN WITH CSV NEEDS
class Boss():

    def __init__(self, num_ids_per_assignment, file_name, boss_type): #INHERITED CLASSES WILL SET BOSS_TYPE

        #DIFFERENTIATED NAMES

        if boss_type == "book":
            self.data_type_name = "Books"
            data_log_id_column_name = "book_id"

        elif boss_type == "review":
            self.data_type_name = "Reviews"
            data_log_id_column_name = "ID"

        #SHARED FIELDS

        self.num_ids_per_assignment = num_ids_per_assignment
        self.log_file_name = "databases/"+ file_name + ".csv"

        print("Boss Initiated & Awaiting Input Data Request")

#PREPARATION METHODS

    def is_csv(self):

        try:
            df = pd.read_csv(self.log_file_name, low_memory=False)
            is_csv = True

        except (FileNotFoundError, pd.errors.EmptyDataError):
            is_csv = False

        return is_csv

    def input_data_request(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def prepare_scope(self):

        if self.is_csv(): #IF WE HAVE A CSV, COMPARE REQUESTED DATA TO CSV DATA

            log_file_data = pd.read_csv(self.log_file_name)
            ids_in_data_log = log_file_data[data_log_id_column_name].unique()
            ids_in_data_log = [str(id) for id in ids_in_data_log]

            self.ids_to_be_scraped = []

            for id in self.ids_requested: #IDS NOT IN CSV DATA ADDED TO TO_BE_SCRAPED LIST

                if id not in ids_in_data_log:
                    self.ids_to_be_scraped.append(id)

        else: #IF WE DON'T HAVE A CSV, ALL REQUESTED DATA MUST BE SCRAPED

            self.ids_to_be_scraped = self.ids_requested
            requested_ids_found = 0

        if not self.ids_to_be_scraped: #IF WE ALREADY HAVE ALL THE DATA IN THE CSV
            print("All Requested Data Has Already Been Collected ")
            return

        random.shuffle(self.ids_to_be_scraped) #RANDOMIZE ORDER OF TO_BE_SCRAPED SO THAT REQUESTS TO WEBSITE ARE NOT SEQUENTIAL

        #COUNTERS
        self.num_ids_to_be_scraped = len(self.ids_to_be_scraped)
        self.num_ids_scraped = 0

        #VALUES FOR PRINT STATEMENT
        num_ids_requested = len(self.ids_requested)
        requested_ids_found = num_ids_requested - self.num_ids_to_be_scraped

        print("{found} of {requested} Requested {type} Found In Log. {outstanding} {type} Remaining".format(found = requested_ids_found, requested = num_ids_requested, type = self.data_type_name, outstanding = self.num_ids_to_be_scraped))

    def generate_assignments(self): #SPLITS DATA NEEDED INTO ASSIGNMENTS THAT CAN BE GIVEN TO MINIONS

        num_assignments = math.ceil(self.num_ids_to_be_scraped/self.num_ids_per_assignment)

        #OUTSTANDING ASSIGNMENT KEY LIST WILL HOLD THE NAMES OF ASSIGNMENTS (THESE ARE JUST SEQUENTIAL NUMBERS)
        #ASSIGNMENT DICT WILL HOLD THE LIST OF IDS ASSOCIATED WITH EACH ASSIGNMENT

        self.outstanding_assignment_key_list = [num for num in range(0, num_assignments - 1)]
        self.assignment_dict = {}

        for assignment_key in self.outstanding_assignment_key_list:
            assignment_ids = self.ids_to_be_scraped[self.num_ids_per_assignment * assignment_key : min(self.num_ids_per_assignment * assignment_key + assignment_key, len(self.ids_to_be_scraped))]
            self.assignment_dict[assignment_key] = assignment_ids

    def prepare_for_minions(self):

        if not self.ids_requested:
            print("Boss Requires Data Request Prior to Preparing for Minions")
            return

        self.prepare_scope()
        self.prepare_log_file()
        self.generate_assignments()

        print("Boss is Ready to Recieve Requests from Minions")

#PREPARING LOG FILE METHODS

    def add_headers_to_log_file(self):

        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def prepare_log_file(self):

        if self.is_csv():
            pass

        else:

            self.open_log_file()
            self.add_headers_to_log_file()
            self.datafile.close()

        print("Log File Ready")

    def open_log_file(self):

        self.datafile = open(self.log_file_name, "a")

#COMMUNICATE WITH MINIONS METHODS

    def give_assignment(self):

        #IF THERE ARE OUTSTANDING ASSIGNMENTS, SELECT THE FIRST ONE & MOVE IT TO THE END OF THE LIST

        if self.outstanding_assignment_key_list:
            assignment_key = assignment_key_list[0]
            self.outstanding_assignment_key_list = assignment_key_list[1:]
            self.outstanding_assignment_key_list.append(assignment_key)

        else: #IF THERE ARE NO OUTSTANDING ASSIGNMENTS, SELECT NONE (NONE TRIGGERS A SHUTDOWN FOR MINION)
            assignment_key = None

        #GET ID LIST FOR RELEVANT ASSIGNMENT
        if assignment_key:
            assignment_ids = assignment_dict.get(assignment)
        else:
            assignment_ids = None

        #GIVE KEY AND ASSIGNMENT ID TO MINION
        return assignment_key, assignment_ids

#LOG DATA METHODS

    def input_data(self, assignment_key, data_nodes):

        #LOG THE DATA

        self.open_log_file()
        self.generate_datetime()

        for node in data_nodes:
            write_data_point_to_csv(data_node)

        self.datafile.close()

        #MARK ASSIGNMENTS AS COMPLETE
        self.remove_assignment_from_list_of_outstanding(assignment_key)

        #UPDATE COUNTERS & PRINT PROGRESS

        self.num_ids_scraped += len(data_nodes)
        self.print_progress()

    def write_data_point_to_csv(self, data_node):
        data = data_node.get_data()

        self.datafile.write("\n{},{}".format(data, self.now_string))

    def remove_assignment_from_list_of_outstanding(self, assignment_key):

        try:
            self.outstanding_assignment_key_list.remove(assignment_key)

        except ValueError: #AT THE END OF THE PROCESS, MULTIPLE MINIONS MAY HAVE BEEN GIVEN THE SAME ASSIGNMENT
            pass

## PROGRESS METHODS

    def generate_datetime(self):

        now = datetime.now()
        self.now_string = now.strftime("%m/%d/%Y %H:%M:%S")

    def print_progress(self):
        self.generate_datetime()
        percent_complete = round(100 * self.num_ids_scraped / self.num_ids_to_be_scraped, 2)
        percent_complete_string = str(self.percent_complete)

        print("{} / {} {} Collected ({}% Complete) at {}".format(str(self.num_ids_scraped), str(self.num_ids_to_be_scraped), self.data_type_name, percent_complete_string, self.now_string))

class Review_Boss(Boss):

    def __init__(self, num_ids_per_assignment, file_name):
        super().__init__(num_ids_per_assignment, file_name, "review")

    def input_data_request(self, min_id, max_id):
        self.ids_requested = range(min_id, max_id)

        print("Boss Recieved Data Request & Ready to Prepare for Minions")

    def add_headers_to_log_file(self):

        self.datafile.write("ID,is_URL_valid,review_publication_date,book_title,book_id,rating,reviewer_href,started_reading_date,finished_reading_date,shelved_date,log_time")

class Book_Boss(Boss):

    def __init__(self, num_ids_per_assignment, file_name):
        super().__init__(num_ids_per_assignment, file_name, "book")

    def input_data_request(self, book_list):
        self.ids_requested = book_id_list

        print("Boss Recieved Data Request & Ready to Prepare for Minions")

    def add_headers_to_log_file(self):

        self.datafile.write("book_id,author,language,num_reviews,num_ratings,avg_rating,isbn13,editions_url,publication_date,first_publication_date,series,log_time")

#MINION WITH REVIEW_MINION AND BOOK_MINION INHERITING
#MINION HANDLES:
    #SCRAPING & PARSING
    #CREATING BOOK & REVIEW NODES
    #SLEEP BETWEEN REQUESTS & AFTER RECIEVING UNPOPULATED DATA

class Minion():

    def __init__(self, boss, max_sleep_time, minion_type): #INHERITED CLASSES WILL SET MINION TYPE

        #DIFFERENTIATED NAMES & PARSERS

        if minion_type == "book":
            self.base_url = "https://www.goodreads.com/book/show/"
            self.parser = Book_Parser()

        if minion_type == "review":
            self.base_url = "https://www.goodreads.com/review/show/"
            self.parser = Review_Parser()

        #SHARED FIELDS

        self.boss = boss
        self.scraper = Scraper()
        self.max_sleep_time = max_sleep_time
        self.collected_data_nodes_list = []

    def request_assignment(self):
        self.assignment_key, self.assignment_ids = self.boss.give_assignment()

    def generate_current_url(self):
        self.current_url = self.base_url + str(self.current_id)

    def parse(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def generate_data_node(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def scrape_url(self):

        self.current_webpage_as_string = self.scraper.url_to_string_content(self.current_url)

    def generate_soup(self):

        self.current_soup = self.parser.html_to_soup(self.current_webpage_as_string)

        if self.parser.is_soup_populated(self.current_soup): #IF THE SOUP IS POPULATED, WE'RE ALL SET
            return

        #IF THE SOUP ISN'T POPULATED, WAIT INCREASING PERIODS BETWEEN RETRIES

        num_invalid_responses_recieved = 0

        while self.parser.is_soup_populated(self.current_soup) == False:

            if num_invalid_responses_recieved < 10:
                #self.generate_datetime()
                #print("Recieved Invalid Response from Website. Pausing Data Collection at {}...".format(self.self.now_string))

                pause_time = max(self.max_sleep_time, num_invalid_responses_recieved*60) #IF IT'S THE FIRST ERROR, REGULAR SLEEPTIME. FOR SUBSEQUENT ERRORS, INCREASINGLY LARGE WAIT TIMES.
                self.sleep(pause_time)

                #self.generate_datetime()
                #print("Restarting Data Collection at {}...".format(self.now_string))
                self.current_soup = self.parser.html_to_soup(self.current_webpage_as_string)

                num_invalid_responses_recieved += 1

            else: #AT THE POINT WHERE IT'S TEN MINUTES BETWEEN REQUESTS, JUST TERMINATE

                #print("Too Many Invalid Requests Recieved. Terminating Data Collection.")
                sys.exit()

    def log_data(self): #MINION KEEPS DATA AS A LIST OF NODES
        self.collected_data_nodes_list.append(self.current_data_node)

    def sleep(self, max_sleep_time_overwrite = None): #SYNTAX IS A LITTLE AWKWARD: IT USES THE MAX_SLEEP_TIME OF THE CLASS BY DEFAULT, BUT THAT CAN BE OVERWRITTEN

        if max_sleep_time_overwrite:
            sleeptime = max_sleep_time_overwrite
        else:
            sleeptime = self.max_sleep_time

        self.scraper.sleep(sleeptime)

    def transmit_data_to_boss(self):

        self.boss.input_data(self.assignment_key, self.collected_data_nodes_list)
        self.collected_data_nodes_list = [] #ONCE DATA IS TRANSMITTED, CLEAR OUT LIST

    def collect_assigned_data(self): #COLLECTING DATA FOR A SINGLE ASSIGNMENT

        for id in self.assignment_ids:
            self.current_id = id
            self.generate_current_url()
            self.scrape_url()
            self.generate_soup()
            self.parse()
            self.log_data()
            self.sleep()

    def data_collection_loop(self): #REQUESTING NEW ASSIGNMENTS & TRANSMITTING DATA
        self.request_assigment()

        while self.assignment_key():
            self.collect_assigned_data()
            self.transmit_data_to_boss()
            self.request_assignment()

        sys.exit() #TERMINATE SCRIPT AFTER NEW ASSIGNMENTS STOP COMING IN

class Review_Minion(Minion):

    def __init__(self, boss, max_sleep_time):
        super().__init__(boss, max_sleep_time, "review")

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

    def generate_data_node(self):

        self.current_data_node = Review(self.current_id, self.is_current_valid, self.current_date, self.current_book_title, self.current_book_id, self.current_rating, self.current_reviewer_href, self.current_start_date, self.current_finished_date, self.current_shelved_date)

class Book_Minion(Minion):

    def __init__(self, boss, max_sleep_time):
        super().__init__(boss, max_sleep_time, "book")

    def parse(self):
        self.current_author = self.parser.book_soup_to_author(self.current_soup)
        self.current_language = self.parser.book_soup_to_language(self.current_soup)
        self.current_num_reviews = self.parser.book_soup_to_num_reviews(self.current_soup)
        self.current_num_ratings = self.parser.book_soup_to_num_ratings(self.current_soup)
        self.current_avg_rating = self.parser.book_soup_to_avg_rating(self.current_soup)
        self.current_isbn13 = self.parser.book_soup_to_isbn13(self.current_soup)
        self.current_editions_href = self.parser.book_soup_to_editions_href(self.current_soup)
        self.current_publication_date = self.parser.book_soup_to_publication_date(self.current_soup)
        self.current_first_publication_date = self.parser.book_soup_to_first_publication_date(self.current_soup)
        self.current_series = self.parser.book_soup_to_series(self.current_soup)

    def generate_data_node(self):

        self.current_data_node = Book(self.current_id, self.current_author, self.current_language, self.current_num_reviews, self.current_num_ratings, self.current_avg_rating, self.current_isbn13, self.current_editions_href, self.current_publication_date, self.current_first_publication_date, self.current_series)
