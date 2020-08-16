#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd
import math

#import classes

from parser_script import Review_Parser

from scraper_script import Scraper
from data_collection_script import Review_Detail_Data_Collector

class Review():

    def __init__(id, date, book_title, book_id, rating, reviewer_href, start_date, finished_date, shelved_date):
        self.id = review_id
        self.date = date
        self.book_title = book_title
        self.book_id = book_id
        self.rating = rating
        self.reviewer_href = reviewer_href
        self.start_date = start_date
        self.finished_date = finished_date
        self.shelved_date = shelved_date

class Book():
    pass

class Boss():

    def __init__(self, boss_type, assignment_size, file_name):

        if boss_type == "book":
            id_column_name = "book_id"

        elif boss_type == "review":
            id_column_name = "ID"

        else:
            return "Error: Invalid Boss Type"

        self.assignment_size = assignment_size
        self.log_file_name = "databases/"+ file_name + ".csv"

    def is_csv(self):
        pass

    def input_scrape_request(self):
        "This method will be overwritten"

    def prepare_scope(self):

        if self.is_csv():

            data_logged_at_start = pd.read_csv(self.log_file_name)
            already_scraped = self.data_logged_at_start[id_column_name].unique()
            already_scraped = [str(id) for id in self.already_scraped]

            self.to_be_scraped = []

            for id in self.requested:

                if id not in already_scraped:
                    self.to_be_scraped.append(id)

            random.shuffle(self.to_be_scraped)

    def generate_assignments(self):

        num_to_be_scraped = len(self.to_be_scraped)
        num_assignments = math.ceil(num_to_be_scraped/assignment_size)

        self.assignment_list = [num for num in range(0, num_assignments - 1)]
        self.assignment_dict = {}

        for assignment in self.assignment_list:
            assignment_ids = self.assignment_list[assignment: assignment + assignment_size]
            self.assignment_dict[assignment] = assignment_ids  

    def give_assignment(self):

        if self.assignment_list:
            assignment = assignment_list[0]
            self.assignment_list = assignment_list[1:]
            self.assignment_list.append(assignment)

        else:
            assignment = None

        if assignment:
            assignment_ids = assignment_dict.get(assignment)
        else:
            assignment_ids = None

        return assignment, assignment_ids

    def complete_assignment(self, assignment):

        try:
            self.assignment_list.remove(assignment)

        except ValueError:
            pass

    def log_data(self):
        pass

class Review_Boss(Boss):

    def input_scrape_request(self, min_id, max_id):
        self.requested = range(min_id, max_id)

class Book_Boss(Boss):

    def input_scrape_request(self, book_list):
        self.requested = book_id_list

class Minion():

    def request_assignment(self):
        pass
