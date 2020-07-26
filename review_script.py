#import libraries
import pandas as pd

#Classes

class Review_Database():

    def __init__(self, file_name):

        self.file_name = file_name + ".csv"
        self.df = pd.read_csv(self.file_name)

        self.df = self.df[self.df.is_URL_valid == True]

        self.df.dropna(inplace = True)
        self.df.drop_duplicates(inplace = True)

        self.df.sort_values(by = "ID", inplace = True)
        self.df.reset_index(inplace = True, drop = True)

    def drop_unrated(self):

        self.df = self.df[self.df.rating != "None"]
        self.df.reset_index(inplace = True, drop = True)

    def limit_dates(self, min_year, max_year):

        self.df["year"] = (pd.to_datetime(self.df["review_publication_date"]).apply(lambda date: date.year))
        self.df = self.df[(self.df.year >= min_year) & (self.df.year <= max_year)]
        self.df.drop(columns = ["year"], inplace = True)
        self.df.reset_index(inplace = True, drop = True)

    def generate_review_count_by_book(self):

        self.df_by_book = self.df.groupby(["book_id", "book_title"]).ID.count().reset_index()
        self.df_by_book.rename(columns = {"ID": "review_count"}, inplace = True)
        self.df_by_book.sort_values(by = "review_count", ascending=False, inplace = True)
        self.df_by_book.reset_index(inplace = True, drop = True)

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

## TESTING

review_database = Review_Database("review_data_sample")
review_database.drop_unrated()
review_database.limit_dates(2017, 2020)
review_database.generate_review_count_by_book()

print(review_database.df_by_book)
