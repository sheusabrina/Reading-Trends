from bs4 import BeautifulSoup
import re

#PARSER 1: GIVEN BOOK PAGE, GENERATES LIST OF REVIEW URLS
    #Note, when this is working right, test_book will generate 5,915 URLS

test_book = open("test_book.html")
book_soup = BeautifulSoup(test_book, "html.parser")

review_list = book_soup.find_all(attrs = {"href": re.compile("^https://www.goodreads.com/review")})
link_list = []
for review in review_list:
    link = review.get("href")
    link_list.append(link)

#print(review_list)

print(link_list[0])




#PARSER 2: GIVEN REVIEW URLS, GENERATES A DATABASE
