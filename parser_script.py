from bs4 import BeautifulSoup

#PARSER 1: GIVEN BOOK PAGE, GENERATES LIST OF REVIEW URLS

test_book = open("test_book.html")
book_soup = BeautifulSoup(test_book, "html.parser")

#PARSER 2: GIVEN REVIEW URLS, GENERATES A DATABASE
