#HOW TO USE MASTER:
    #INIT WITH HOST AND PORT OF OWN COMPUTER
    #INPUT SCRAPING SCOPE
    #CALL KICKOFF METHOD
    #MASTER IS READY FOR SLAVES

#TO-DO LIST:
    #FIX BUG WITH DATA LOG READING
    #FIX INTERMITTENT ALERT THREAD
    #ADD EMAIL ALERTS
    #ADD TERMINATION
    #USE DAEMON THREADS

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

class Master_Methods():

    def __init__(self, file_name, host, port, num_ids_per_chunk):

        self.num_ids_per_chunk = num_ids_per_chunk
        self.num_ids_recieved = 0
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

        #IDENTIFYING ITEMS TO SCRAPE

        if not self.is_csv(): #IF NO CSV, ALL DATA NEEDS TO BE SCRAPED
            self.ids_to_scrape_list = [x for x in self.ids_requested_list]

        else: #IF CSV, SCRAPE ITEMS NOT ALREADY IN CSV
            self.ids_to_scrape_list = []

            log_file_data = pd.read_csv(self.log_file_name)
            ids_in_data_log = log_file_data[self.data_log_id_column_name].unique()
            ids_in_data_log = [str(id) for id in ids_in_data_log]

            for id in self.ids_requested_list: #IDS NOT IN CSV DATA ADDED TO TO_BE_SCRAPED LIST

                if id not in ids_in_data_log:
                    self.ids_to_scrape_list.append(id)

        #TERMINATE IF NO ITEMS TO SCRAPE
        if not self.ids_to_scrape_list:
            print("Data request contains no unknown data. Terminating.")
            sys.exit()

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
        print("{:,} / {:,} data points collected ({:.2%} complete) at {}".format(self.num_ids_recieved, self.num_ids_total, self.num_ids_recieved/self.num_ids_total, self.now_string))

    def print_progress_inter(self):
        self.print_progress()
        time.sleep(5*60)

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

        self.num_ids_recieved += 1

        return "Data Recieved"

    def run_rest_api(self):
        bottle.route("/api")(self.transmit_chunk_ids)
        bottle.route("/api", method = "POST")(self.recieve_data)

        run(host=self.host, port=self.port, debug=True)

    def log_data_loop(self):

        while True: #INFINITE LOOP

            if not self.data_strings_queue.empty():
                data_string = self.data_strings_queue.get()

                self.open_log_file()
                self.generate_datetime()
                self.datafile.write("\n{},{}".format(data_string, self.now_string))
                self.datafile.close()

                self.data_strings_queue.task_done()

    def termination_monitoring_loop(self):
        print("entering termination monitoring")

        terminate = False

        while terminate == False:

            if (self.num_ids_total == self.num_ids_recieved) and self.data_strings_queue.empty():
                terminate = True

            elif self.chunks_oustanding_queue.empty() and self.soup_tuple_queue.empty():

                print("Data collection is nearing completion or stuck. Check slave functionality") #THIS WILL BE MORE USEFUL ONCE SCRAPER CAN EMAIL ME!
                time.sleep(60*60) #HOUR

            else:
                pass

        sys.exit()

    def input_scraping_scope(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def add_headers_to_log_file(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

class Master(Master_Methods):

    def prepare(self):
        self.prepare_scope()
        self.generate_chunks()
        self.prepare_log_file()

    def kickoff(self):
        self.prepare()

        thread_api = threading.Thread(target = self.run_rest_api).start()
        thread_log_data = threading.Thread(target = self.log_data_loop).start()
        thread_print_progress_inter = threading.Thread(target = self.print_progress_inter).start()

class Review_Master(Master):

    def __init__(self, file_name, host, port, num_ids_per_chunk):
        super().__init__(file_name, host, port, num_ids_per_chunk)
        self.data_log_id_column_name = "review_id"

    def input_scraping_scope(self, min_id, max_id):
        self.ids_requested_list = range(min_id, max_id)

    def add_headers_to_log_file(self):
        self.datafile.write("review_id,is_URL_valid,review_publication_date,book_title,book_id,rating,reviewer_href,reviewer_started_reading_date,reviewer_finished_reading_date,reviwer_shelved_date,data_log_time")

class Book_Master(Master):

    def __init__(self, file_name, host, port, num_ids_per_chunk):
        super().__init__(file_name, host, port, num_ids_per_chunk)
        self.data_log_id_column_name = "book_id"

    def add_headers_to_log_file(self):
        self.datafile.write("book_id,book_author,book_language,num_reviews,num_ratings,avg_rating,isbn13,editions_url,book_publication_date,book_first_publication_date,series,data_log_time")

#TESTING
host, port = "localhost", 8080

test_review_master = Review_Master("test_database", host, port, 3)
test_review_master.input_scraping_scope(120, 130)
test_review_master.kickoff()
