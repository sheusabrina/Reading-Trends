#import libraries

import requests
import random
import time

#import data
from headers_data import ordered_headers_list

class Scraper():

    def __init__(self):
        self.headers_list = ordered_headers_list

    def select_header(self):
        self.header = random.choice(self.headers_list)

    def url_to_string(self, url):
        webpage_response = requests.get(url)
        webpage = webpage_response.content
        webpage_string = str(webpage)
        return webpage_string

    def string_to_file(self, file_name, string):
        open(file_name+".html", "w").write(string)

    def sleep(self, max_sleep_time):
        time_list = range(0, max_sleep_time*100, 1)
        sleep_time = random.choice(time_list)/100
        time.sleep(sleep_time)
