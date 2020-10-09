#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd
import math
import sys

from bottle import route, run, template, post, get
import threading
import queue

#import classes

from parser_script import Review_Parser, Book_Parser
from scraper_script import Scraper
from data_classes import Book, Review

class Slave_Methods():

    def __init__(self, max_sleep_time, minion_type, host, port):

        #DIFFERENTIATED NAMES & PARSERS

        if minion_type == "book":
            self.base_url = "https://www.goodreads.com/book/show/"
            self.parser = Book_Parser()

        if minion_type == "review":
            self.base_url = "https://www.goodreads.com/review/show/"
            self.parser = Review_Parser()

        #SHARED FIELDS

        self.scraper = Scraper()
        self.max_sleep_time = max_sleep_time

        self.host = host
        self.port = port

    def request_chunk(self):

        pass

        #self.chunk_key
        #self.chunk_items

class Slave(Slave_Methods):
    pass
