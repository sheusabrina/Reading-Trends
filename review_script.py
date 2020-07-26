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
print(review_database.df)
