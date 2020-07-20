from bs4 import BeautifulSoup
import re

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


#PARSER 2: GIVEN A BOOK PAGE, CYCLES THROUGH PAGES (AJAX)


#PARSER 3: GIVEN REVIEW URLS, GENERATES A REVIEWS DATABASE
