#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd

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

class Boss(Review_Detail_Data_Collector):

    def __init__(self):
        pass

    def prepare_scope(self):
        pass

    def generate_assignments(self):
        self.assignment_list = []

    def give_assignment(self):

        if self.assignment_list:
            assignment = assignment_list[0]
            self.assignment_list = assignment_list[1:]
            self.assignment_list.append(assignment)

        else:
            assignment = None

        return assignment

    def log_data(self):
        pass

class Minion(Review_Detail_Data_Collector):

    def request_assignment(self):
        pass
