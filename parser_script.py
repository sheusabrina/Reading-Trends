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

    def book_soup_to_author(self, book_soup):

        author = book_soup.find(attrs = {"class": "authorName"})#.get_text()
        #Note: If there are multiple authors, this identifies the first one only.

        print(author)

        #return author

    def book_soup_to_language(self, book_soup):

        language = book_soup.find(attrs = {"itemprop": "inLanguage"}).get_text()

        return language

    def book_soup_to_num_reviews(self, book_soup):

        num_reviews = book_soup.find(attrs = {"itemprop": "reviewCount"}).get_text()
        num_reviews = num_reviews.replace("reviews","")
        num_reviews = num_reviews.replace(",","")
        num_reviews = num_reviews.strip()
        num_reviews = int(num_reviews)

        return num_reviews

    def book_soup_to_num_ratings(self, book_soup):

        num_ratings = book_soup.find(attrs = {"itemprop": "ratingCount"}).get_text()
        num_ratings = num_ratings.replace("ratings","")
        num_ratings = num_ratings.replace(",","")
        num_ratings = num_ratings.strip()
        num_ratings = int(num_ratings)

        return num_ratings

    def book_soup_to_avg_rating(self, book_soup):

        avg_rating = book_soup.find(attrs = {"itemprop": "ratingValue"}).get_text().strip()
        avg_rating = float(avg_rating)

        return avg_rating

    def book_soup_to_isbn13(self, book_soup):

        isbn = book_soup.find(attrs = {"itemprop": "isbn"}).get_text()

        return isbn

    def book_soup_to_editions_href(self, book_soup):

        editions = book_soup.find(attrs = {"class": "otherEditionsLink"})
        editions = editions.find("a")

        editions_url = editions.get("href")

        return editions_url

    def book_soup_to_details_soup(self, book_soup):

        details = book_soup.find(attrs = {"id": "details"})
        return details

    def book_soup_to_publication_date(self, book_soup):

        details = self.book_soup_to_details_soup(book_soup)
        publication_details = details.find(text = re.compile("Published")).strip()
        publication_details_list = publication_details.splitlines()
        publication_date = publication_details_list[1].strip()

        return publication_date

    def book_soup_to_first_publication_date(self, book_soup):

        details = self.book_soup_to_details_soup(book_soup)
        publication_date = details.find(text = re.compile("first published")).strip()
        publication_date = publication_date.replace("(first published ","")
        publication_date = publication_date.replace(")","")

        print(publication_date)

        return publication_date

    def book_soup_to_series(self, book_soup):

        #NOTE: If series name has a "#" in it, it will get cut off. I can live with that.

        details = self.book_soup_to_details_soup(book_soup)
        series = details.find(attrs = {"href": re.compile("series")})

        if series:

            series = series.get_text()
            series = series[:series.index("#")]

        print(series)

        return series

## WHY IS PARSING WORKING BETTER IN THE DATA COLLECTOR THAN IN THE PARSER TESTING?
    #SOMETHING BAD IS HAPPENING IN FILE CONVERSION

##BOOKS IN DATA COLLECTOR
# URL -> WEBPAGE RESPONSE -> WEBPAGE CONTENT (BYTES) -> STRING -> SOUP

##BOOKS IN PARSER TESTING
#URL -> WEBPAGE RESPONSE -> WEBPAGE CONTENT (BYTES) -> HTML FILE -> OPEN AS TEXTIOWRAPPER(NO RB) OR BUFFERED READER (RB) -> STRING -> SOUP

#HYPOTHESIS: SOMETHING IS HAPPENING TO THE FILE IN THE TRANSITION FROM BYTES TO HTML TO TEXTIO/BUFFERED THAT HAS SOME IMPACT AS IT IS CONVERTED BACK TO A STRING
#POTENTIAL SOLUTIONS:
    #CAN YOU OPEN AN HTML AS BYTES INSTEAD OF TEXTIOWRAPPER / BUFFERED READER?
    #IF YOU CONVERT FROM TEXTIOWRAPPER/BUFFERED READER TO BYTES, WILL THAT HELP?

#WHAT ARE THESE DATA TYPES ANYWAY?

test_parser = Book_Parser()

test_book_angels_demons = open("html_files/test_book_angels_demons.html", "rb")
test_book_meditations = open("html_files/test_book_meditations.html", "rb")
test_book_hp1 = open("html_files/test_book_hp1.html", "rb")

test_book_angels_demons_no_rb = open("html_files/test_book_angels_demons.html")
print("Parser pre-string format, without rb: {}".format(type(test_book_angels_demons_no_rb)))
print("Parser pre-string format: {}".format(type(test_book_angels_demons)))

print("Parser presoup format: {}".format(type(str(test_book_angels_demons))))

book_soup_angels_demons = test_parser.html_to_soup(str(test_book_angels_demons))
book_soup_meditations = test_parser.html_to_soup(str(test_book_meditations))
#book_soup_hp1 = test_parser.html_to_soup(str(test_book_hp1))

print("Parser soup format: {}".format(type(book_soup_angels_demons)))

#print("Test soups ready...")

author_angels_demons = test_parser.book_soup_to_author(book_soup_angels_demons)
author_meditations = test_parser.book_soup_to_author(book_soup_meditations)

#print(author_angels_demons)
#print(author_meditations)

#language_angels_demons = test_parser.book_soup_to_language(book_soup_angels_demons)
#language_meditations = test_parser.book_soup_to_language(book_soup_meditations)
#language_hp1 = test_parser.book_soup_to_language(book_soup_hp1)

#print(language_angels_demons)
#print(language_meditations)
#print(language_hp1)

#num_reviews_angels_demons = test_parser.book_soup_to_num_reviews(book_soup_angels_demons)
#num_reviews_meditations = test_parser.book_soup_to_num_reviews(book_soup_meditations)
#num_reviews_hp1 = test_parser.book_soup_to_num_reviews(book_soup_hp1)

#print(num_reviews_angels_demons)
#print(num_reviews_meditations)
#print(num_reviews_hp1)

#avg_rating_angels_demons = test_parser.book_soup_to_avg_rating(book_soup_angels_demons)
#avg_rating_meditations = test_parser.book_soup_to_avg_rating(book_soup_meditations)
#avg_rating_hp1 = test_parser.book_soup_to_avg_rating(book_soup_hp1)

#print(avg_rating_meditations)
#print(avg_rating_angels_demons)
#print(avg_rating_hp1)

#num_ratings_angels_demons = test_parser.book_soup_to_num_ratings(book_soup_angels_demons)
#num_ratings_meditations = test_parser.book_soup_to_num_ratings(book_soup_meditations)
#num_ratings_hp1 = test_parser.book_soup_to_num_ratings(book_soup_hp1)

#print(num_ratings_meditations)
#print(num_ratings_angels_demons)
#print(num_ratings_hp1)

#isbn_meditations = test_parser.book_soup_to_isbn13(book_soup_meditations)
#print(isbn_meditations)

#editions_meditations = test_parser.book_soup_to_editions_href(book_soup_meditations)
#print(editions_meditations)

#publication_date_meditations = test_parser.book_soup_to_publication_date(book_soup_meditations)
#publication_date_angels_demons = test_parser.book_soup_to_publication_date(book_soup_angels_demons)

#print(publication_date_meditations)
#print(publication_date_angels_demons)

#first_publication_date_meditations = test_parser.book_soup_to_first_publication_date(book_soup_meditations)
#first_publication_date_angels_demons = test_parser.book_soup_to_first_publication_date(book_soup_angels_demons)

#print(first_publication_date_meditations)
#print(first_publication_date_angels_demons)

#series_angels_demons = test_parser.book_soup_to_series(book_soup_angels_demons)
#series_meditations = test_parser.book_soup_to_series(book_soup_meditations)

#print(series_angels_demons)
#print(series_meditations)

## TESTING REVIEW PARSER

#test_review = open("test_review.html", "wb")
#test_unpopulated_review = open("test_review_unpopulated.html", "wb")
#test_grounded_review = open("test_review_grounded.html", "wb")

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
