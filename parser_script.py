from bs4 import BeautifulSoup
import re

def string_cleaner(input_string):
    output_string = input_string.replace(",","")
    output_string = output_string.replace("\\n", "")
    output_string = output_string.strip()

    return output_string

def date_suffix_cleaner(input_string):

    date_suffix = re.search("\d(st|rd|nd|th)", input_string)

    if date_suffix:
        date_suffix = date_suffix.group(0)
        date = re.search("\d", date_suffix).group(0)
        output_string = input_string.replace(date_suffix, date)

    else:
        output_string = input_string

    return output_string

class Parser():

    def __init__(self):
        pass

    def html_to_soup(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup

    def is_populated(self, soup):

        text = soup.findAll(text = True)

        if text:
            is_populated = True
        else:
            is_populated = False

        return is_populated


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
        #Note: If there are multiple authors, this identifies the first one only.

        author = book_soup.find(attrs = {"class": "authorName"}) ## THIS SHOULD USUALLY WORK
        if not author: #TRY REGEX IF IT DOESN'T
            author = book_soup.find(attrs = {"class": re.compile("authorName")})

        author = author.get_text()
        author = string_cleaner(author)

        return author

    def book_soup_to_language(self, book_soup):

        details = self.book_soup_to_details_soup(book_soup) # REDUCING AMOUNT OF PAGE TO RUN REGEX ON
        language = details.find(attrs = {"itemprop": re.compile("inLanguage")}) #DOESN'T WORK WITHOUT THE REGEX. DON'T TRY.

        if language: #SOME BOOKS DON'T HAVE LANGUAGE
            language = language.get_text()

        return language

    def book_soup_to_num_reviews(self, book_soup):

        num_reviews = book_soup.find(attrs = {"itemprop": "reviewCount"}).get_text()
        num_reviews = num_reviews.replace("reviews","")
        num_reviews = num_reviews.replace("review","")
        num_reviews = string_cleaner(num_reviews)
        num_reviews = int(num_reviews)

        return num_reviews

    def book_soup_to_num_ratings(self, book_soup):

        num_ratings = book_soup.find(attrs = {"itemprop": "ratingCount"}).get_text()
        num_ratings = num_ratings.replace("ratings","")
        num_ratings = num_ratings.replace("rating", "")
        num_ratings = string_cleaner(num_ratings)
        num_ratings = int(num_ratings)

        return num_ratings

    def book_soup_to_avg_rating(self, book_soup):

        avg_rating = book_soup.find(attrs = {"itemprop": "ratingValue"}).get_text()
        avg_rating = string_cleaner(avg_rating)
        avg_rating = float(avg_rating)

        return avg_rating

    def book_soup_to_isbn13(self, book_soup):

        details = self.book_soup_to_details_soup(book_soup) # REDUCING AMOUNT OF PAGE TO RUN REGEX ON
        isbn = details.find(attrs = {"itemprop": re.compile("isbn")}) #DOESN'T WORK WITHOUT THE REGEX. DON'T TRY.

        if isbn: #SOME BOOK PAGES DON'T HAVE ISBN

            isbn = isbn.get_text()

        return isbn

    def book_soup_to_editions_href(self, book_soup):

        details = self.book_soup_to_details_soup(book_soup) # REDUCING AMOUNT OF PAGE TO RUN REGEX ON
        editions = details.find(attrs = {"class": re.compile("otherEditionsLink")}) #DOESN'T WORK WITHOUT THE REGEX. DON'T TRY.

        if editions: #SOME BOOKS DO NOT HAVE EDITIONS

            editions = editions.find(href = True)
            editions_url = editions.get("href")

        else:

            editions_url = None

        return editions_url

    def book_soup_to_details_soup(self, book_soup):

        details = book_soup.find(attrs = {"id": "details"})
        return details

    def book_soup_to_publication_date(self, book_soup):

        details = self.book_soup_to_details_soup(book_soup)
        publication_details = details.find(text = re.compile("Published"))

        if "by" in publication_details: #REMOVE PUBLISHER IF LISTED
            publication_date = publication_details[:publication_details.index("by")]
        else:
            publication_date = publication_details

        publication_date = publication_date.replace("Published","")
        publication_date = string_cleaner(publication_date)
        publication_date = date_suffix_cleaner(publication_date)

        return publication_date

    def book_soup_to_first_publication_date(self, book_soup):

        details = self.book_soup_to_details_soup(book_soup)
        publication_date = details.find(text = re.compile("first published"))

        if publication_date: ## SOME BOOKS DON'T HAVE ONE
            publication_date = publication_date.replace("(first published ","")
            publication_date = publication_date.replace(")","")
            publication_date = string_cleaner(publication_date)
            publication_date = date_suffix_cleaner(publication_date)

        return publication_date

    def book_soup_to_series(self, book_soup):

        #NOTE: If series name has a "#" in it, it will get cut off. I can live with that.

        details = self.book_soup_to_details_soup(book_soup)
        series = details.find(attrs = {"href": re.compile("series")})

        if series: ##SOME BOOKS DON'T HAVE ONE
            series = series.get_text()
            if "#" in series: #REMOVE NUMBER IF THERE IS ONE
                series = series[:series.index("#")]

            series = string_cleaner(series)

        return series

test_parser = Book_Parser()

#html_hp1_regular = open("html_files/test_book_hp1_regular.html")
#html_angels_demons = open("html_files/test_book_angels_demons.html")
html_meditations = open("html_files/test_book_meditations.html")
#html_deep_fathom = open("html_files/test_book_deep_fathom.html")

#book_soup_angels_demons = test_parser.html_to_soup(html_angels_demons)
book_soup_meditations = test_parser.html_to_soup(html_meditations)
#book_soup_deep_fathom = test_parser.html_to_soup(html_deep_fathom)

#book_soup_hp1_regular = test_parser.html_to_soup(html_hp1_regular)

print("Test soups ready...")

#author_angels_demons = test_parser.book_soup_to_author(book_soup_angels_demons)
#author_meditations = test_parser.book_soup_to_author(book_soup_meditations)
#author_hp1 = test_parser.book_soup_to_author(book_soup_hp1)
#author_deep_fathom = test_parser.book_soup_to_author(book_soup_deep_fathom)

first_element_meditations = test_parser.is_populated(book_soup_meditations)
print(first_element_meditations)

#author_hp1_regular = test_parser.book_soup_to_author(book_soup_hp1_regular)

#print(author_angels_demons)
#print(author_meditations)
#print(author_hp1_regular)
#print(author_deep_fathom)

#language_angels_demons = test_parser.book_soup_to_language(book_soup_angels_demons)
#language_meditations = test_parser.book_soup_to_language(book_soup_meditations)
#language_hp1 = test_parser.book_soup_to_language(book_soup_hp1)

#language_hp1_regular = test_parser.book_soup_to_language(book_soup_hp1_regular)

#print(language_angels_demons)
#print(language_meditations)
#print(language_hp1_regular)
#print(language_hp1)

#num_reviews_angels_demons = test_parser.book_soup_to_num_reviews(book_soup_angels_demons)
#num_reviews_meditations = test_parser.book_soup_to_num_reviews(book_soup_meditations)
#num_reviews_hp1 = test_parser.book_soup_to_num_reviews(book_soup_hp1)

#num_reviews_hp1_regular = test_parser.book_soup_to_num_reviews(book_soup_hp1_regular)

#print(num_reviews_hp1_regular)

#print(num_reviews_angels_demons)
#print(num_reviews_meditations)
#print(num_reviews_hp1)

#avg_rating_angels_demons = test_parser.book_soup_to_avg_rating(book_soup_angels_demons)
#avg_rating_meditations = test_parser.book_soup_to_avg_rating(book_soup_meditations)
#avg_rating_hp1 = test_parser.book_soup_to_avg_rating(book_soup_hp1)

#avg_rating_hp1_regular = test_parser.book_soup_to_avg_rating(book_soup_hp1_regular)

#print(avg_rating_meditations)
#print(avg_rating_angels_demons)
#print(avg_rating_hp1)

#print(avg_rating_hp1_regular)

#num_ratings_angels_demons = test_parser.book_soup_to_num_ratings(book_soup_angels_demons)
#num_ratings_meditations = test_parser.book_soup_to_num_ratings(book_soup_meditations)
#num_ratings_hp1 = test_parser.book_soup_to_num_ratings(book_soup_hp1)

#num_ratings_hp1_regular = test_parser.book_soup_to_num_ratings(book_soup_hp1_regular)

#print(num_ratings_meditations)
#print(num_ratings_angels_demons)
#print(num_ratings_hp1)

#print(num_ratings_hp1_regular)

#isbn_meditations = test_parser.book_soup_to_isbn13(book_soup_meditations)
#isbn_angels_demons = test_parser.book_soup_to_isbn13(book_soup_angels_demons)

#isbn13_hp1_regular = test_parser.book_soup_to_isbn13(book_soup_hp1_regular)

#print(isbn13_hp1_regular)

#print(isbn_meditations)
#print(isbn_angels_demons)

#editions_meditations = test_parser.book_soup_to_editions_href(book_soup_meditations)
#editions_angels_demons = test_parser.book_soup_to_editions_href(book_soup_angels_demons)
#editions_hp1_regular = test_parser.book_soup_to_editions_href(book_soup_hp1_regular)

#print(editions_meditations)
#print(editions_angels_demons)
#print(editions_hp1_regular)

#details_hp1_regular = test_parser.book_soup_to_details_soup(book_soup_hp1_regular)

#print(details_hp1_regular)

#publication_date_meditations = test_parser.book_soup_to_publication_date(book_soup_meditations)
#publication_date_angels_demons = test_parser.book_soup_to_publication_date(book_soup_angels_demons)

#publication_date_hp1_regular = test_parser.book_soup_to_publication_date(book_soup_hp1_regular)

#print(publication_date_hp1_regular)

#print(publication_date_meditations)
#print(publication_date_angels_demons)

#first_publication_date_meditations = test_parser.book_soup_to_first_publication_date(book_soup_meditations)
#first_publication_date_angels_demons = test_parser.book_soup_to_first_publication_date(book_soup_angels_demons)

#first_publication_date_hp1_regular = test_parser.book_soup_to_first_publication_date(book_soup_hp1_regular)

#print(first_publication_date_meditations)
#print(first_publication_date_angels_demons)

#print(first_publication_date_hp1_regular)

#series_angels_demons = test_parser.book_soup_to_series(book_soup_angels_demons)
#series_meditations = test_parser.book_soup_to_series(book_soup_meditations)

#series_hp1_regular = test_parser.book_soup_to_series(book_soup_hp1_regular)

#print(series_hp1_regular)

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
