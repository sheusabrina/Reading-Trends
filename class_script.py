class Book():

    def __init__(self, title, ISBN, author, pub_year):
        self.title = title
        self.author = author
        self.ISBN = ISBN
        self.pub_year = pub_year
        self.reviews = []
        self.genres = []

class Review():

    def __init__(self, headline, rating, date, reviewer, text = None):
        self.headline = headline
        self.rating = rating
        self.date = date
        self.reviewer = reviewer
        if text:
            self.text = text

class Classification():

    def __init__(name):
        self.name =name
        self.automated_book_list = []
        self.manual_book_list = []

    def add_book(book, list_type):
        if list_type = "automated":
            self.automated_book_list.append(book)
        elif: list_type = "manual":
            self.automated_book_list.append(book)
        else:
            return "Error: Invalid List Type"
