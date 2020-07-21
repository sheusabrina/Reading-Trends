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
        self.select_header()

        webpage_response = requests.get(url, headers = self.header)
        webpage = webpage_response.content
        webpage_string = str(webpage)
        self.webpage_string = webpage_string

        return self.webpage_string

    def string_to_file(self, file_name):
        open(file_name+".html", "w").write(self.webpage_string)

    def sleep(self, max_sleep_time):
        time_list = range(0, max_sleep_time*100, 1)
        sleep_time = random.choice(time_list)/100
        time.sleep(sleep_time)

##TESTING

#example_url = "https://docs.python.org/3/howto/regex.html"

#testing_scraper = Scraper()
#testing_scraper.url_to_string(example_url)
#testing_scraper.string_to_file("test_scraper_output")
