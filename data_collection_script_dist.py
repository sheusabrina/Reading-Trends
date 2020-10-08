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

class Master_Methods():

    def __init__(self, file_name, master_type, host, port): #INHERITED CLASSES WILL SET Master_TYPE

        #DIFFERENTIATED NAMES

        if Master_type == "book":
            self.data_type_name = "Books"
            data_log_id_column_name = "book_id"

        elif Master_type == "review":
            self.data_type_name = "Reviews"
            data_log_id_column_name = "ID"

        #SHARED FIELDS

        self.num_items_per_chunk = 200
        self.log_file_name = "databases/"+ file_name + ".csv"
        self.host = host
        self.port = port

    def is_csv(self):

        try:
            df = pd.read_csv(self.log_file_name, low_memory=False)
            is_csv = True

        except (FileNotFoundError, pd.errors.EmptyDataError):
            is_csv = False

        return is_csv

    def prepare_log_file(self):

        if self.is_csv():
            pass

        else:

            self.open_log_file()
            self.add_headers_to_log_file()
            self.datafile.close()

    def open_log_file(self):

        self.datafile = open(self.log_file_name, "a")

    def prepare_scope(self):

        if not self.is_csv():
            self.items_to_scrape_list = [x for x in self.items_requested_list]

        else:

            log_file_data = pd.read_csv(self.log_file_name)
            ids_in_data_log = log_file_data[data_log_id_column_name].unique()
            ids_in_data_log = [str(id) for id in ids_in_data_log]

            for id in self.items_requested_list: #IDS NOT IN CSV DATA ADDED TO TO_BE_SCRAPED LIST

                if id not in ids_in_data_log:
                    self.items_to_scrape_list.append(id)

        self.num_items_total = len(self.items_to_scrape_list)
        random.shuffle(self.items_to_scrape_list)

    def generate_chunks(self):

        num_chunks = math.ceil(self.num_items_total/self.num_items_per_chunk)
        self.chunks_outstanding_list = [num for num in range(0, num_chunks - 1)]
        self.items_recieved_list = []

        #EACH CHUNK HAS A KEY, WHICH CORRESPONDS TO A LIST OF ITEMS

        self.chunk_dict = {}

        for chunk_key in self.chunks_outstanding_list:
            chunk_items = [self.items_to_scrape_list[i] for i in range(chunk_key), len(self.chunks_oustanding_list), chunk_key]
            self.chunk_dict[chunk_key] = chunk_items

    @get('/assignment_request')
    def assignment_request(self):

        if self.chunks_oustanding_list:
            chunk_key = self.chunks_outstanding_list[0] #SELECT FIRST CHUNK KEY IN QUEUE
            self.chunks_oustanding_list = self.chunks_outstanding_list[1:0] #REMOVE CHUNK KEY FROM FRONT OF QUEUE
            self.chunks_outstanding_list.append(chunk_key) #RE-ADD IT TO END OF QUEUE

            chunk_items = self.chunk_dict.get(chunk_key)

        else:

            chunk_key, chunk_items = None, None

        return assignment_key, assignment_ids

    @post('/input_data')
    def input_data(self, chunk_key, data_node_list):

        self.chunks_outstanding_list.remove(chunk_key)

        for data_node in data_node_list:
            self.collected_data_nodes_list.append(data_node)

    def input_scraping_scope(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def add_headers_to_log_file(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    #STEP 1: INIT MASTER
    #STEP 2: INPUT SCRAPING REQUEST & CALL KICKOFF

    #STEP 3: Master PREPERATION (ie, log file, chunking, start-up rest API, etc)
        #THREAD 1: HANDLE ASSIGNMENT REQUESTS
        #THREAD 2: HANDLE INCOMING DATA
        #THREAD 3: ADD RECIEVED DATA TO LOG

class Master(Master_Methods):

    def kickoff(self):
        self.prepare()

        thread_assignment_requests = threading.Thread(target = self.assignment_requests())
        thread_incoming_data_requests = threading.Thread(target = self.incoming_data())
        thread_log_recieved_data = threading.Thread(target = self.log_data())

        thread_assignment_requests.start()
        thread_incoming_data_requests.start()
        thread_log_recieved_data.start()

    def prepare(self):
        self.prepare_scope()
        self.generate_chunks()
        self.prepare_log_file()

    def assignment_requests(self):
        pass

    def incoming_data(self):
        pass

    def log_data(self):
        pass

class Review_Master(Master):

    def input_scraping_scope(self, min_id, max_id):
        self.items_requested_list = range(min_id, max_id)
