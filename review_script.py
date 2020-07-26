class Review():

    def __init__(self, review_ID):
        self.review_ID = review_ID
        self.review_URL = None
        self.is_URL_valid = None
        self.review_publication_date = None
        self.book_title = None
        self.book_ID = None
        self.rating = None
        self.reviewer_href = None
        self.started_reading_date = None
        self.finished_reading_date = None
        self.shelved_date = None

        self.is_review_populated = None
        self.review_best_date = None
