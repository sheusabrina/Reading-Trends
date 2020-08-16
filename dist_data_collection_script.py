#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd
import sys

#import classes

from parser_script import Parser
from parser_script import Review_Parser
from parser_script import Book_Parser

from scraper_script import Scraper

class Boss():
    pass
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

class Minion():
    pass 
