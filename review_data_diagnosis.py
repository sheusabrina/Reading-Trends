#In my work yesterday, I introduced some issues into the data_collection classes.
    #I parsed webpages, converting to strings only some of the time.
    #I believe that process may have introduced bad data into my review database.
#I want to fully understand the potential impact on data, so that I can potentially clean out any bad data.
#This script compares the output of each data conversion process.
    #If they are identical, my data is fine.
    #If they have differences, those can be used to identify bad data in the log.

#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd
import time

#import classes

from parser_script import Parser
from parser_script import Review_Parser
from parser_script import Book_Parser

from scraper_script import Scraper

rev_url_med = "https://www.goodreads.com/review/show/2668957860"
rev_url_twilight = "https://www.goodreads.com/review/show/153608751"
rev_url_gatsby = "https://www.goodreads.com/review/show/1115578730"
rev_url_error = "https://www.goodreads.com/review/show/166895786"
rev_url_grounded = "https://www.goodreads.com/review/show/2572722180"

reviews_list = [rev_url_med, rev_url_twilight, rev_url_gatsby, rev_url_error, rev_url_grounded]

review_input_format = ["string_format", "bytes_format"]
review_parser_methods = ["review_soup_is_valid", "review_soup_to_date", "review_soup_to_book_title", "review_soup_to_book_id", "review_soup_to_rating", "review_soup_to_reviewer_href", "progress_dict_to_start_date", "progress_dict_to_finish_date", "progress_dict_to_shelved_date"]

scraper = Scraper()
parser = Review_Parser()

def run_data_test():

    log_file = open("review_data_diagnosis_log.csv", "a")
    log_file.write("rev_name,input_format,parser_method,parse_output,parse_output_type")

    for review_url in reviews_list:

        print("Analyzing: {}".format(review_url))

        for format in review_input_format:

            ##CONVERT URL TO HTML, DEPENDING ON THE FORMAT

            if format == "string_format":
                html = scraper.url_to_content(review_url)
            if format == "bytes_format":
                html = scraper.url_to_string(review_url)

            ## CREATE SOUP

            soup = parser.html_to_soup(html)

            #SLEEP A LITTLE

            time_list = range(0, 100, 1)
            sleep_time = random.choice(time_list)/100
            time.sleep(sleep_time)

            for parser_method in review_parser_methods:

                ##FOR INVALID REVIEWS, OUTPUT IS ALWAYS NONE

                if parser.review_soup_is_valid(soup) == False:

                    parser_output = None
                    parser_output_type = None

                ##FOR THE PROGRESS METHODS, GENERATE A DICTIONARY FIRST

                elif parser_method in ["progress_dict_to_start_date", "progress_dict_to_finish_date", "progress_dict_to_shelved_date"]:

                    dict = parser.review_soup_to_progress_dict(soup)

                    if parser_method == "progress_dict_to_start_date":
                        parser_output = parser.progress_dict_to_start_date(dict)
                    if parser_method == "progress_dict_to_finish_date":
                        parser_output = parser.progress_dict_to_finish_date(dict)
                    if parser_method == "progress_dict_to_shelved_date":
                        parser_output = parser.progress_dict_to_shelved_date(dict)

                    parser_output_type = type(parser_output)

                ##OTHERWISE, JUST RUN THE METHOD

                else:

                    if parser_method == "review_soup_is_valid":
                        parser_output = parser.review_soup_is_valid(soup)
                    if parser_method == "review_soup_to_date":
                        parser_output = parser.review_soup_to_date(soup)
                    if parser_method == "review_soup_to_book_title":
                        parser_output = parser.review_soup_to_book_title(soup)
                    if parser_method == "review_soup_to_book_id":
                        parser_output = parser.review_soup_to_book_id(soup)
                    if parser_method == "review_soup_to_rating":
                        parser_output = parser.review_soup_to_rating(soup)
                    if parser_method == "review_soup_to_reviewer_href":
                        parser_output = parser.review_soup_to_reviewer_href(soup)

                    parser_output_type = type(parser_output)

                ## LOG FINDINGS

                log_file.write("\n{},{},{},{},{}".format(review_url, format, parser_method, parser_output, parser_output_type))

    log_file.close()

#run_data_test()

#RESULTS:
    #This test shows that reading progress dates come back as none when run on bytes. They come back correctly when run on strings.
    #An Excel review of the review_data.csv file does not show a block of data in which reading progress dates were not populated.
        #The largest number of consecutive data points for which the shelved_date = None is four.
    #This corresponds with my review of commits, which suggests that review_parsing was consistently run with strings rather than content.
    #THE REVIEW DATA IS FINE! 
