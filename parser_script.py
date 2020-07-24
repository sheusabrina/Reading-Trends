from bs4 import BeautifulSoup
import re

class Parser():

    def __init__(self):
        pass

    def html_to_soup(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup

class Review_Parser(Parser):

    def review_soup_is_valid(self, review_soup):
        title = review_soup.find('title').get_text()
        if title == "Page not found":
            is_valid = False
        else:
            is_valid = True
        return is_valid

    def review_soup_to_date(self, review_soup):
        review_date = review_soup.find(attrs = {"class": "right dtreviewed greyText smallText"}).get_text()
        review_date = review_date.replace("\\n" , "").strip().replace(",", "")

        return review_date

    def review_soup_to_book_title(self, review_soup):
        book_title = review_soup.find(attrs = {"class": "bookTitle"}).get_text()
        return book_title

    def review_soup_to_book_id(self, review_soup):
        book = review_soup.find(attrs = {"class": "bookTitle"})
        book_url = book.get("href")

        book_id = book_url.replace("/book/show/", "")
        book_id = book_id.split(".")[0]

        return book_id

class Book_Parser(Parser):

    def soup_to_review_urls(self, book_soup):
        #this method gets from the soup of a book page to urls for the top 30 reviews
        link_list = []

        review_list = book_soup.find_all(attrs = {"href": re.compile("^https://www.goodreads.com/review")})
        for review in review_list:
            link = review.get("href")
            link_list.append(link)

        return link_list

## TESTING

test_review = open("test_review.html")
test_parser = Review_Parser()

review_soup = test_parser.html_to_soup(test_review)
#review_book_title = test_parser.review_soup_to_book_title(review_soup)
book_id = test_parser.review_soup_to_book_id(review_soup)

#print(review_book_title)
print(book_id)
