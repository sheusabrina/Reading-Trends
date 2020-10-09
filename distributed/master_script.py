#HOW TO USE MASTER:
    #INIT WITH HOST AND PORT OF OWN COMPUTER
    #INPUT SCRAPING SCOPE
    #CALL KICKOFF METHOD
    #MASTER IS READY FOR SLAVES

#import libraries
from bottle import route, run, template, post, get
from datetime import datetime
import math
import queue
import random
import system
import time
import threading

#import classes
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

        #IDENTIFYING ITEMS TO SCRAPE

        if not self.is_csv(): #IF NO CSV, ALL DATA NEEDS TO BE SCRAPED
            self.items_to_scrape_list = [x for x in self.items_requested_list]

        else: #IF CSV, SCRAPE ITEMS NOT ALREADY IN CSV

            log_file_data = pd.read_csv(self.log_file_name)
            ids_in_data_log = log_file_data[data_log_id_column_name].unique()
            ids_in_data_log = [str(id) for id in ids_in_data_log]

            for id in self.items_requested_list: #IDS NOT IN CSV DATA ADDED TO TO_BE_SCRAPED LIST

                if id not in ids_in_data_log:
                    self.items_to_scrape_list.append(id)

        #TERMINATE IF NO ITEMS TO SCRAPE
        if not self.items_to_scrape_list:
            print("Data request contains no unknown data. Terminating.")
            sys.exit()

        self.num_items_total = len(self.items_to_scrape_list)
        random.shuffle(self.items_to_scrape_list)

    def generate_chunks(self):

        #EACH CHUNK HAS A KEY, WHICH CORRESPONDS TO A LIST OF ITEMS
        self.num_chunks_total = math.ceil(self.num_items_total/self.num_items_per_chunk)
        chunks_key_list = [num for num in range(0, self.num_chunks_total - 1)]
        self.chunks_outstanding_queue = queue.Queue(maxsize=0)
        self.items_recieved_queue = queue.Queue(maxsize=0)

        self.num_chunks_recieved = 0

        #EACH CHUNK HAS A KEY, WHICH CORRESPONDS TO A LIST OF ITEMS

        self.chunk_dict = {}

        for chunk_key in chunks_key_list:
            chunk_items = [self.items_to_scrape_list[i] for i in range(chunk_key), len(chunks_key_list), chunk_key]
            self.chunk_dict[chunk_key] = chunk_items

    def write_data_point_to_csv(self, data_node):
        data = data_node.get_data()
        self.generate_datetime()
        self.datafile.write("\n{},{}".format(data, self.now_string))

        self.datafile.close()

    def generate_datetime(self):

        now = datetime.now()
        self.now_string = now.strftime("%m/%d/%Y %H:%M:%S")

    def print_progress(self):
        self.generate_datetime()
        print("{:,} / {:,} data chunks collected ({:.2%} complete) at {}".format(self.num_chunks_recieved, self.num_chunks_total, self.num_chunks_recieved/self.num_chunks_total, self.now_string)

    @get('/assignment_request')
    def assignment_request(self):

        if not self.chunks_outstanding_queue.empty():
            chunk_key = self.chunks_outstanding_queue.get()
            self.chunks_outstanding_queue.task_done()

            chunk_items = self.chunk_dict.get(chunk_key)

        else:

            chunk_key, chunk_items = None, None

        return assignment_key, assignment_ids

    @post('/input_data')
    def input_data(self, chunk_key, data_node_list):

        for data_node in data_node_list:
            self.items_recieved_queue.put(data_node)

        self.num_chunks_recieved += 1

    def input_scraping_scope(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

    def add_headers_to_log_file(self):
        print("This method should be overwritten in each inherited class. If this is printed, something is not working correctly.")

class Master(Master_Methods):

    def kickoff(self):
        self.prepare()

        thread_assignment_requests = threading.Thread(target = self.assignment_requests()).start()
        thread_data_delivery = threading.Thread(target = self.incoming_data()).start()
        thread_log_data = threading.Thread(target = self.log_data()).start()
        thread_print_progress_inter = threading.Thread(target = self.print_progress_inter()).start

    def prepare(self):
        self.prepare_scope()
        self.generate_chunks()
        self.prepare_log_file()

    def assignment_requests(self):
        pass

    def incoming_data(self):
        pass

    def log_data(self):

        if not self.items_recieved_queue.empty():
            data_node = self.items_recieved_queue.get()
            self.write_data_point_to_csv(data_node)
            self.items_recieved_queue.task_done()

        self.log_data()

    def print_progress_inter(self):
        self.print_progress()
        time.sleep(5*60)

class Review_Master(Master):

    def input_scraping_scope(self, min_id, max_id):
        self.items_requested_list = range(min_id, max_id)
