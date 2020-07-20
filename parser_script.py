from bs4 import BeautifulSoup
import re

#TO DO LIST:
#PARSER 2: GIVEN A BOOK PAGE, CYCLES THROUGH PAGES (AJAX)
#PARSER 3: GIVEN REVIEW URLS, GENERATES A REVIEWS DATABASE

class Parser():

    def __init__(self):
        pass

    def html_to_soup(self, html):
        soup = BeautifulSoup(html, "html.parser")

    #this method gets from the soup of a book page to urls for the top 30 reviews
    def book_soup_to_review_urls(self, book_soup):
        link_list = []

        review_list = book_soup.find_all(attrs = {"href": re.compile("^https://www.goodreads.com/review")})
        for review in review_list:
            link = review.get("href")
            link_list.append(link)

        return link_list

    def review_soup_is_valid(self, review_soup):
        pass

    def review_soup_to_data(self, review_soup):
        pass
