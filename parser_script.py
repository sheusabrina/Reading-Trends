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
        return soup

    def book_soup_to_review_urls(self, book_soup):
        #this method gets from the soup of a book page to urls for the top 30 reviews
        link_list = []

        review_list = book_soup.find_all(attrs = {"href": re.compile("^https://www.goodreads.com/review")})
        for review in review_list:
            link = review.get("href")
            link_list.append(link)

        return link_list

    def review_soup_is_valid(self, review_soup):
        title = review_soup.find('title').get_text()
        if title == "Page not found":
            is_valid = False
        else:
            is_valid = True
        return is_valid

    def review_soup_to_data(self, review_soup):
        review_date = review_soup.find_all(attrs = {"class": "right dtreviewed greyText smallText"})
        #review_date = review_soup.find_all(attrs = {"itemprop": "datePublished"})
        print(review_date)

##TESTING REVIEW PAGES

parser_for_testing = Parser()

test_review = open("test_review.html")
test_review_error = open("test_review_error.html")

test_review_soup = parser_for_testing.html_to_soup(test_review)
#test_review_error_soup = parser_for_testing.html_to_soup(test_review_error)

#print(parser_for_testing.review_soup_is_valid(test_review_soup))
#print(parser_for_testing.review_soup_is_valid(test_review_error_soup))

parser_for_testing.review_soup_to_data(test_review_soup)
