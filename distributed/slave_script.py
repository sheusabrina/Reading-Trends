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

    def parse(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def generate_data_node(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

class Slave(Slave_Methods):
    pass
