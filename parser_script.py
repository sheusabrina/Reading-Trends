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
        book_title = book_title.replace(",", "")
        return book_title

    def review_soup_to_book_id(self, review_soup):
        book = review_soup.find(attrs = {"class": "bookTitle"})
        book_url = book.get("href")

        #remove front of URL
        book_id = book_url.replace("/book/show/", "")
        book_id = book_id.split(".")[0]

        #remove back of URL
        book_id = book_id.split("-")[0]

        return book_id

    def review_soup_to_rating(self, review_soup):
        rating_section = review_soup.find(attrs = {"itemprop": "reviewRating"})

        if rating_section:
            rating = rating_section.find(attrs = {"class": "value-title"}).get("title")

        else:
            rating = None

        return rating

    def review_soup_to_reviewer_href(self, review_soup):
        reviewer = review_soup.find(attrs = {"class": "reviewer"})
        reviewer = reviewer.find(attrs = {"class": "userReview"})
        reviewer_href = reviewer.get("href")

        return reviewer_href

    def review_soup_to_progress_dict(self, review_soup):

        progress = review_soup.find(attrs = {"class": "readingTimeline"}).get_text().replace("\\n" , " ").strip()
        progress_list = progress.split("       ")

        progress_dict = {}

        for item in progress_list:

            item = item.replace(",", "")

            if " – " in item:
                split_list = item.split(" – ")
                milestone = split_list[1].strip()
                date = split_list[0].strip()

            else:
                milestone = item
                date = None

            progress_dict[milestone] = date

        return progress_dict

    def progress_dict_to_start_date(self, dict):

        start_date = dict.get("Started Reading")
        return start_date

    def progress_dict_to_finish_date(self, dict):

        finish_date = dict.get("Finished Reading")
        return finish_date

    def progress_dict_to_shelved_date(self, dict):

        shelved_date = dict.get("Shelved")
        return shelved_date

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

#test_review = open("test_review.html")
#test_unpopulated_review = open("test_review_unpopulated.html")
#test_grounded_review = open("test_review_grounded.html")

#test_parser = Review_Parser()

#review_soup = test_parser.html_to_soup(test_grounded_review)
#review_soup = test_parser.html_to_soup(test_review)

#review_book_title = test_parser.review_soup_to_book_title(review_soup)
#book_id = test_parser.review_soup_to_book_id(review_soup)
#review_book_is_rating = test_parser.review_soup_is_rating(review_soup)
#book_rating = test_parser.review_soup_to_rating(review_soup)
#reviewer_href = test_parser.review_soup_to_reviewer_href(review_soup)
#reading_timeline = test_parser.review_soup_to_progress_dict(review_soup)

#start = test_parser.progress_dict_to_start_date(reading_timeline)
#finish = test_parser.progress_dict_to_finish_date(reading_timeline)
#shelved = test_parser.progress_dict_to_shelved_date(reading_timeline)

#print(review_book_title)
#print(book_id)
#print(book_rating)
#print(reviewer_href)
#print(review_book_is_rating)

#print(reading_timeline)
#print(start)
#print(finish)
#print(shelved)
