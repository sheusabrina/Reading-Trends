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

    def url_to_bytes_content(self, url):
        self.select_header()

        self.webpage_response = requests.get(url, headers = self.header)
        self.webpage = self.webpage_response.content

        return self.webpage

    def url_to_string_content(self, url):

        self.url_to_bytes_content(url)

        self.webpage_string = str(self.webpage)

        return self.webpage_string

    def webpage_bytes_content_to_file(self, file_name):
        open(file_name+".html", "wb").write(self.webpage)

    def sleep(self, max_sleep_time):
        time_list = range(0, max_sleep_time*100, 1)
        sleep_time = random.choice(time_list)/100
        time.sleep(sleep_time)

## CREATING TEST FILES

scraper = Scraper()

#meditations book
#scraper.url_to_bytes_content("https://www.goodreads.com/book/show/30659")
#scraper.webpage_bytes_content_to_file("test_book_meditations")

#angels & demons book
#scraper.url_to_bytes_content("https://www.goodreads.com/book/show/960.Angels_Demons")
#scraper.webpage_bytes_content_to_file("test_book_angels_demons")

#HP1 book
#scraper.url_to_bytes_content("https://www.goodreads.com/book/show/3")
#scraper.webpage_bytes_content_to_file("test_book_hp1")

#review (meditations)
#scraper.url_to_bytes_content("https://www.goodreads.com/review/show/2668957860")
#scraper.webpage_bytes_content_to_file("test_review")

#review, error page
#scraper.url_to_bytes_content("https://www.goodreads.com/review/show/166895786")
#scraper.webpage_bytes_content_to_file("test_review_error")

#review, grounded (since it crashed the parser)

#print(type(scraper.url_to_bytes_content("https://www.goodreads.com/review/show/2572722180")))


#scraper.webpage_bytes_content_to_file("test_review_grounded")
