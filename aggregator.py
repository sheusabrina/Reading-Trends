import pandas as pd
import datetime
import numpy as np

class Aggregator():

    def __init__(self, review_file, book_file, start_date, end_date, grain):

        self.start_date = start_date
        self.end_date = end_date
        self.grain = grain

        self.check_grain()

        self.review_df = pd.read_csv(review_file, usecols=["review_id","is_URL_valid", "review_publication_date", "book_id"], na_values="None")
        self.book_df = pd.read_csv(book_file, usecols=["book_id" "book_language", "num_reviews", "num_ratings", "avg_rating" ,"isbn13", "book_publication_date", "book_first_publication_date", "series"], na_values="None")

    def check_grain():

        if self.grain not in ["day", "week", "month", "quarter"]:

            print("Invalid Grain. Aggregator will not run correctly")

    def drop_invalid_rows(self, input_df):

        input_df.dropna(inplace = True)
        input_df.drop_duplicates(inplace = True)

    def drop_invalid_reviews(self):

        self.review_df = self.review_df[self.review_df.is_URL_valid == True]

    def datetime_conversion(self, input_df):

        date_columns = ["review_publication_date", "reviewer_started_reading_date", "reviewer_finished_reading_date", "reviwer_shelved_date", "data_log_time", "book_publication_date", "book_first_publication_date"]

        for col in input_df.columns:
            if col in date_columns:
                input_df[col] = pd.to_datetime(input_df[col], errors = "coerce")

    def drop_out_of_time_reviews(self):

        self.reviews_df = self.reviews_df[(self.reviews_df.review_publication_date >= self.start_date) and (self.reviews_df.review_publication_date <= self.end_date)]

    def clean_data(self):

        df_list = [self.review_df, self.book_df]

        for df in df_list:
            self.drop_invalid_rows(df)
            self.date_time_conversion()

        self.drop_invalid_reviews()
        self.drop_out_of_time_reviews()

        for df in df_list:
            df.reset_index(inplace = True, drop = True)

    def resample_reviews(self): ##ASK SOMEONE TO DOUBLE CHECK THIS!

        if self.grain == "day":
            pass

        elif self.grain == "week":
            self.reviews_df["review_publication_date"] = self.reviews_df["review_publication_date"].dt.strftime('%Y-%W')

        else: #GRAIN IS MONTH OR QUARTER

            #FOR MONTH, USE BUILT IN
            self.reviews_df["review_publication_date"] = self.reviews_df["review_publication_date"].dt.strftime('%Y-%m')

            #FOR QUARTER, ADD ADDITIONAL PROCESSING

            if self.grain = "quarter":
                self.reviews_df["review_publication_date"] = self.reviews_df["review_publication_date"].apply(lambda month_year: "{}-{}".format(month_year.year, (month_year.month -1)//3 +1 )


data_file_name_book = ""
data_file_name_review = ""
start_date = datetime.datetime(2018, 1, 1)
end_date = datetime.datetime(2020, 2, 29)
