#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd
import math
import sys

from bottle import route, run, template
import threading
import queue

#import classes

from parser_script import Review_Parser
from parser_script import Book_Parser
from scraper_script import Scraper

#DATA STORAGE NODES

class Review():

    def __init__(self, id, is_valid, date, book_title, book_id, rating, reviewer_href, start_date, finished_date, shelved_date):
        self.id = review_id
        self.is_valid = is_valid
        self.date = date
        self.book_title = book_title
        self.book_id = book_id
        self.rating = rating
        self.reviewer_href = reviewer_href
        self.start_date = start_date
        self.finished_date = finished_date
        self.shelved_date = shelved_date

    def get_data(self):
        data = "{},{},{},{},{},{},{},{},{},{}".format(str(self.id), self.is_valid, self.current_date, self.book_title, self.book_id, self.rating, self.reviewer_href, self.start_date, self.finished_date, self.shelved_date)
        return data

class Book():

    def __init__(self, book_id, author, language, num_reviews, num_ratings, avg_rating, isbn13, editions_url,publication_date,first_publication_date,series,log_time):
        self.id = book_id
        self.author = author
        self.language = language
        self.num_reviews = num_reviews
        self.num_ratings = num_ratings
        self.avg_rating = avg_rating
        self.isbn13 = isbn13
        self.editions_url = editions_url
        self.publication_date = publication_date
        self.first_publication_date = first_publication_date
        self.series = series

    def get_data(self):
        data = "{},{},{},{},{},{},{},{},{},{},{}".format(self.id, self.author, self.language, self.num_reviews, self.num_ratings, self.avg_rating, self.isbn13, self.editions_url, self.publication_date, self.first_publication_date, self.series)
        return data

#DISTRIBUTED SYSTEM

class DistComponent:

    def __init__(self, host, port):
        work_queue = queue.LifoQueue(maxsize=0)
        results_queue = queue.LifoQueue(maxsize=0)

class Master(DistComponent):
    pass

class Slave(DistComponent):
    pass

class Review_Master(Master):
    pass

class Book_Master(Master):
    pass

class Review_Slave(Slave):
    pass

class Book_Slave(Slave):
    pass
