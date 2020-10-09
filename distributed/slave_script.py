#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd
import math
import sys
import time

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

    def transmit_data(self):

        pass

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

    def log_data(self): #MINION KEEPS DATA AS A LIST OF NODES
        self.collected_data_nodes_list.append(self.current_data_node)

    def sleep(self):

        self.scraper.sleep(self.max_sleep_time)

    def parse(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def generate_data_node(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

class Slave(Slave_Methods):

    def collect_data_chunk(self):

        for id in self.chunk_items:
            self.current_id = id
            self.generate_current_url()
            self.scrape_url()
            self.generate_soup()
            self.parse()
            self.log_data()
            self.sleep()

    def data_collection_loop(self):
        self.request_chunk()

        while self.chunk_key_list():
            self.collect_data_chunk()
            self.transmit_data()
            self.request_chunk()

        sys.exit() #WHEN MASTER STOPS DISTRIBUTING CHUNKS, TERMINATE
