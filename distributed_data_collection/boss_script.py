#HOW TO USE BOSS:
    #INIT WITH HOST AND PORT OF OWN COMPUTER
    #INPUT SCRAPING SCOPE
    #CALL KICKOFF METHOD
    #YOU HAVE TO CLICK CTRL-C TWICE TO TERMINATE.

#TO-DO LIST:
    #FIX BUG WITH DATA LOG READING
    #ADD EMAIL ALERTS

#import libraries
import bottle
from bottle import route, run, template, post, get, request
from datetime import datetime
import math
import pandas as pd
import queue
import random
import sys
import time
import threading

class Boss():

    def __init__(self, file_name, host, port, num_ids_per_chunk):

        self.num_ids_per_chunk = num_ids_per_chunk
        self.num_ids_logged = 0
        self.log_file_name = "databases/"+ file_name + ".csv"
        self.host = host
        self.port = port
        self.active = True
        self.n = None

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

        #IDENTIFYING ITEMS TO SCRAPE

        if not self.is_csv(): #IF NO CSV, ALL DATA NEEDS TO BE SCRAPED
            self.ids_to_scrape_list = [x for x in self.ids_requested_list]

        else: #IF CSV, SCRAPE ITEMS NOT ALREADY IN CSV
            self.ids_to_scrape_list = []

            log_file_data = pd.read_csv(self.log_file_name, usecols=[self.data_log_id_column_name])
            log_file_data.dropna(inplace = True)
            ids_in_data_log = log_file_data[self.data_log_id_column_name].unique()
            ids_in_data_log = [int(id) for id in ids_in_data_log]

            for id in self.ids_requested_list: #IDS NOT IN CSV DATA ADDED TO TO_BE_SCRAPED LIST

                if id not in ids_in_data_log:
                    self.ids_to_scrape_list.append(id)

        #TERMINATE IF NO ITEMS TO SCRAPE
        if not self.ids_to_scrape_list:
            print("Data request contains no unknown {} data.".format(self.data_type))

        else:
            self.num_ids_total = len(self.ids_to_scrape_list)
            random.shuffle(self.ids_to_scrape_list)

    def generate_chunks(self):

        #QUEUES & COUNTERS
        self.chunks_outstanding_queue = queue.Queue(maxsize=0)
        self.data_strings_queue = queue.Queue(maxsize=0)

        num_chunks_total = math.ceil(self.num_ids_total/self.num_ids_per_chunk)

        for i in range(0, num_chunks_total):
            chunk_ids = self.ids_to_scrape_list[i::num_chunks_total]

            self.chunks_outstanding_queue.put(chunk_ids)

    def generate_datetime(self):

        now = datetime.now()
        self.now_string = now.strftime("%m/%d/%Y %H:%M:%S")

    def print_progress(self):
        self.generate_datetime()
        print("{:,} / {:,} {} data points collected ({:.2%} complete) at {}".format(self.num_ids_logged, self.num_ids_total, self.data_type, self.num_ids_logged/self.num_ids_total, self.now_string))

    def print_progress_inter(self):

        while self.active:
            self.print_progress()
            time.sleep(60)

    def transmit_chunk_ids(self):

        if not self.chunks_outstanding_queue.empty():
            chunk = self.chunks_outstanding_queue.get()
            chunk = str(chunk)
            self.chunks_outstanding_queue.task_done()

        else:

            chunk = None

        return chunk

    def recieve_data(self):

        data_string = request.forms.get("data_string")
        self.data_strings_queue.put(data_string)

        return "Data Recieved"

    def run_rest_api(self):
        bottle.route(self.api_path)(self.transmit_chunk_ids)
        bottle.route(self.api_path, method = "POST")(self.recieve_data)

        run(host=self.host, port=self.port, debug=True)

    def log_data_loop(self):

        while self.active or (not self.data_strings_queue.empty()):

            data_string = self.data_strings_queue.get()

            self.open_log_file()
            self.generate_datetime()
            self.datafile.write("\n{},{}".format(data_string, self.now_string))
            self.datafile.close()

            self.data_strings_queue.task_done()

            self.num_ids_logged += 1

    def input_scraping_scope(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def add_headers_to_log_file(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")


    def prepare(self):
        self.prepare_scope()
        self.generate_chunks()
        self.prepare_log_file()

    def kickoff(self):
        self.prepare()

        for method in [self.log_data_loop, self.print_progress_inter, self.run_rest_api]:
                thread = threading.Thread(target = method, daemon = True)
                thread.start()

        #BLOCKING
        while self.num_ids_total != self.num_ids_logged:
            time.sleep(1)

        self.active = False

        print("{} data collected.".format(self.data_type))

class Review_Boss(Boss):

    def __init__(self, file_name, host, port, num_ids_per_chunk):
        super().__init__(file_name, host, port, num_ids_per_chunk)
        self.data_log_id_column_name = "review_id"
        self.api_path = "/api_review"
        self.data_type = "review"

    def input_scraping_scope(self, min_id, max_id, n = None):

        num_ids_in_range = max_id - min_id

        if n and (n< num_ids_in_range):
            self.ids_requested_list = random.sample(range(min_id, max_id), n)

        else:
            self.ids_requested_list = range(min_id, max_id)

    def add_headers_to_log_file(self):
        self.datafile.write("review_id,is_URL_valid,review_publication_date,book_title,book_id,rating,reviewer_href,reviewer_started_reading_date,reviewer_finished_reading_date,reviwer_shelved_date,data_log_time")

class Book_Boss(Boss):

    def __init__(self, file_name, host, port, num_ids_per_chunk, min_num_reviews = None):
        super().__init__(file_name, host, port, num_ids_per_chunk)
        self.data_log_id_column_name = "book_id"
        self.api_path = "/api_book"
        self.data_type = "book"
        self.min_num_reviews = min_num_reviews


    def input_scraping_scope(self, review_database_file):
        review_database_file = "databases/" + review_database_file + ".csv"
        review_df = pd.read_csv(review_database_file, usecols=["book_id"])
        review_df.dropna(inplace = True)
        review_df = review_df[review_df.book_id != "None"]
        review_df.reset_index(inplace = True, drop = True)

        if self.min_num_reviews:
            review_df["num_reviews"] = 1
            review_df = review_df.groupby("book_id").count()[["num_reviews"]]
            review_df.reset_index(inplace = True)
            review_df = review_df[review_df.num_reviews >= self.min_num_reviews]
            review_df.sort_values(by = "num_reviews", ascending = False, inplace = True)

        self.ids_requested_list = review_df.book_id.unique()
        self.ids_requested_list = [int(x) for x in self.ids_requested_list if x != "None"]

    def add_headers_to_log_file(self):
        self.datafile.write("book_id,book_author,book_language,num_reviews,num_ratings,avg_rating,isbn13,editions_url,book_publication_date,book_first_publication_date,series,data_log_time")

class Dual_Boss():

    def __init__(self, review_file_name, book_file_name, num_ids_per_chunk):

        self.num_ids_per_chunk = num_ids_per_chunk
        self.review_file_name = review_file_name
        self.book_file_name = book_file_name
        self.active = True

    def input_review_configuration(self, host, port, min_id, max_id, n = None):

        self.review_boss = Review_Boss(self.review_file_name, host, port, self.num_ids_per_chunk)
        self.review_boss.input_scraping_scope(min_id, max_id, n)
        self.is_review_configured = True

    def input_book_configuration(self, host, port, min_num_reviews = None):

        self.book_boss = Book_Boss(self.book_file_name, host, port, self.num_ids_per_chunk, min_num_reviews)
        self.book_boss.input_scraping_scope(self.review_file_name)
        self.is_book_configured = True

    def kickoff_book_boss(self):
        self.book_boss.kickoff()

    def kickoff_review_boss(self):
        self.review_boss.kickoff()

    def is_active_loop(self):

        while self.active:

            if len(self.active_threads) == 0:
                self.active = False

            else:

                for thread in self.active_threads:
                    if not thread.is_alive():
                        self.active_threads.remove(thread)

            time.sleep(60*5)

    def kickoff(self):

        if (not self.is_book_configured) or (not self.is_review_configured):
            return "Configurations Must Be Inputted Prior to Kickoff"

        self.active_threads = []

        for method in [self.kickoff_book_boss, self.kickoff_review_boss, self.is_active_loop]:
            thread = threading.Thread(target = method, daemon = True)
            self.active_threads.append(thread)
            thread.start()

        while self.active:
            time.sleep(1)

        print("All data collected. terminating")
        sys.exit()

#TESTING

host = "localhost" # "0.0.0.0"
review_port, book_port = 8080, 80

min_id = 2235559808
max_id = 3607950182
review_n = (3 * 10**4)
ids_per_chunk = 100
book_cutoff = 10

test_dual_boss = Dual_Boss("review_data", "book_data", ids_per_chunk)
test_dual_boss.input_review_configuration(host, review_port, min_id, max_id, review_n)
test_dual_boss.input_book_configuration(host, book_port, book_cutoff)
test_dual_boss.kickoff()
