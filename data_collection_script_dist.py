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

#SYNTAX EXAMPLE

    #@route('/hello')
    #def hello():
        #return "Hello World!"

class Master():
    #STEP 1: INIT MASTER
    #STEP 2: INPUT SCRAPING REQUEST
    #STEP 3: Master PREPERATION (ie, log file, chunking, etc)
        #THREAD 1: HANDLE ASSIGNMENT REQUESTS
        #THREAD 2: HANDLE INCOMING DATA
        #THREAD 3: ADD RECIEVED DATA TO LOG

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
