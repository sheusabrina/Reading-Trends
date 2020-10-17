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

    def is_soup_populated(self, soup):

        text = soup.findAll(text = True)

        if not text:
            is_soup_populated = False

        #elif (len(text) == 1) and "This is a random-length HTML comment" in text[0]:
            #is_soup_populated = False

        elif "This is a random-length HTML comment" in text[1]:
            is_soup_populated = False

        else:
            is_soup_populated = True

        return is_soup_populated

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

        author = book_soup.find(attrs = {"id": re.compile("bookAuthors")})
        author = author.find(attrs = {"itemprop": re.compile("author")})
        author = author.get_text()

        author.replace("(Goodreads Author)","")
        author = string_cleaner(author)

        return author

    def book_soup_to_language(self, book_soup):

        language = book_soup.find(attrs = {"itemprop": re.compile("inLanguage")})

        if language: #SOME BOOKS DON'T HAVE LANGUAGE
            language = language.get_text()

        return language

    def book_soup_to_num_reviews(self, book_soup):

        num_reviews = book_soup.find(attrs = {"itemprop": re.compile("reviewCount")}).get_text()

        num_reviews = num_reviews.replace("reviews","")
        num_reviews = num_reviews.replace("review","")
        num_reviews = string_cleaner(num_reviews)
        num_reviews = int(num_reviews)

        return num_reviews

    def book_soup_to_num_ratings(self, book_soup):

        num_ratings = book_soup.find(attrs = {"itemprop": re.compile("ratingCount")}).get_text()

        num_ratings = num_ratings.replace("ratings","")
        num_ratings = num_ratings.replace("rating", "")
        num_ratings = string_cleaner(num_ratings)
        num_ratings = int(num_ratings)

        return num_ratings

    def book_soup_to_avg_rating(self, book_soup):

        avg_rating = book_soup.find(attrs = {"itemprop": re.compile("ratingValue")}).get_text()

        avg_rating = string_cleaner(avg_rating)
        avg_rating = float(avg_rating)

        return avg_rating

    def book_soup_to_isbn13(self, book_soup):

        isbn = book_soup.find(attrs = {"itemprop": re.compile("isbn")})

        if isbn: #SOME BOOK PAGES DON'T HAVE ISBN
            isbn = isbn.get_text()

        return isbn

    def book_soup_to_editions_href(self, book_soup):

        editions = book_soup.find(attrs = {"class": re.compile("otherEditionsLink")})

        if editions: #SOME BOOKS DO NOT HAVE EDITIONS
            editions = editions.find(href = True)
            editions_url = editions.get("href")

        else:
            editions_url = None

        return editions_url

    def book_soup_to_publication_date(self, book_soup):

        publication_details = book_soup.find(text = re.compile("Published"))

        if "by" in publication_details: #REMOVE PUBLISHER IF LISTED
            publication_date = publication_details[:publication_details.index("by")]
        else:
            publication_date = publication_details

        publication_date = publication_date.replace("Published","")
        publication_date = string_cleaner(publication_date)
        publication_date = date_suffix_cleaner(publication_date)

        return publication_date

    def book_soup_to_first_publication_date(self, book_soup):

        publication_date = book_soup.find(text = re.compile("first published"))

        if publication_date: ## SOME BOOKS DON'T HAVE ONE

            if "![CDATA[" in publication_date:
                publication_date = None

            else:
                publication_date = publication_date.replace("(first published ","")
                publication_date = publication_date.replace(")","")
                publication_date = string_cleaner(publication_date)
                publication_date = date_suffix_cleaner(publication_date)

        return publication_date

    def book_soup_to_series(self, book_soup):

        series = book_soup.find(attrs = {"href": re.compile("series")})

        if series: ##SOME BOOKS DON'T HAVE ONE
            series = series.get_text()

            #REMOVE FIRST PAREN
            if len(series) > 0:
                if series[0] == "(":
                    series = series[1:]

            #REMOVE NUMBER IF THERE IS ONE
            if "#" in series:
                series = series[:series.index("#")]

        #NOTE: IF # IS PART OF AN ACTUAL SERIES NAME, THAT SERIES NAME IS GETTING TRUNCATED. OH WELL.

            series = string_cleaner(series)

        return series

test_parser = Book_Parser()
