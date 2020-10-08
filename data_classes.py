class Review():

    def __init__(self, id, is_valid, date, book_title, book_id, rating, reviewer_href, start_date, finished_date, shelved_date):
        self.id = review_id
        self.is_valid = is_valid
        self.date = date
        self.book_title = book_title
        self.book_id = book_id
        self.rating = rating
        self.reviewer_href = reviewer_href
        self.start_date = start_date
        self.finished_date = finished_date
        self.shelved_date = shelved_date

    def get_data(self):
        data = "{},{},{},{},{},{},{},{},{},{}".format(str(self.id), self.is_valid, self.current_date, self.book_title, self.book_id, self.rating, self.reviewer_href, self.start_date, self.finished_date, self.shelved_date)
        return data

class Book():

    def __init__(self, book_id, author, language, num_reviews, num_ratings, avg_rating, isbn13, editions_url,publication_date,first_publication_date,series,log_time):
        self.id = book_id
        self.author = author
        self.language = language
        self.num_reviews = num_reviews
        self.num_ratings = num_ratings
        self.avg_rating = avg_rating
        self.isbn13 = isbn13
        self.editions_url = editions_url
        self.publication_date = publication_date
        self.first_publication_date = first_publication_date
        self.series = series

    def get_data(self):
        data = "{},{},{},{},{},{},{},{},{},{},{}".format(self.id, self.author, self.language, self.num_reviews, self.num_ratings, self.avg_rating, self.isbn13, self.editions_url, self.publication_date, self.first_publication_date, self.series)
        return data
