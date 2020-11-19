import pandas as pd
import datetime
import numpy as np

#NOTES:
    #WE SHOULD EXPERIMENT WITH ADDING BOOK PUBLICATION DATE, BOOK FIRST PUBLICATION DATE, AND AUTHOR FEATURES

class Aggregator():

    def __init__(self, review_file, book_file, start_date, end_date, grain):

        self.start_date = start_date
        self.end_date = end_date
        self.grain = grain

        self.check_grain()

        self.review_df = pd.read_csv(review_file, usecols=["review_id","is_URL_valid", "review_publication_date", "book_id"], na_values="None")
        self.book_df = pd.read_csv(book_file, usecols=["book_id", "book_language", "num_reviews", "num_ratings", "avg_rating" ,"isbn13", "series"], na_values="None")

    def check_grain(self):

        if self.grain not in ["day", "week", "month", "quarter"]:

            print("Invalid Grain. Aggregator will not run correctly")

    def drop_invalid_rows(self, input_df):

        input_df.dropna(inplace = True)
        input_df.drop_duplicates(inplace = True)

    def drop_invalid_reviews(self):

        self.review_df = self.review_df[self.review_df.is_URL_valid == True]
        self.review_df.drop(columns = "is_URL_valid", inplace = True)

    def datetime_conversion(self, input_df):

        date_columns = ["review_publication_date", "reviewer_started_reading_date", "reviewer_finished_reading_date", "reviwer_shelved_date", "data_log_time", "book_publication_date", "book_first_publication_date"]

        for col in input_df.columns:
            if col in date_columns:
                input_df[col] = pd.to_datetime(input_df[col], errors = "coerce")

    def drop_out_of_time_reviews(self):

        self.review_df = self.review_df[self.review_df.review_publication_date >= self.start_date]
        self.review_df = self.review_df[self.review_df.review_publication_date <= self.end_date]

        #self.review_df = self.review_df[(self.review_df.review_publication_date >= self.start_date) and (self.review_df.review_publication_date <= self.end_date)]

    def drop_reviews_for_unknown_books(self):

        known_book_ids = self.book_df.book_id.unique()
        self.review_df = self.review_df[self.review_df["book_id"].isin(known_book_ids)]

    def clean_data(self):

        df_list = [self.review_df, self.book_df]

        for df in df_list:
            self.drop_invalid_rows(df)
            self.datetime_conversion(df)

        self.drop_invalid_reviews()
        self.drop_out_of_time_reviews()
        self.drop_reviews_for_unknown_books()

        for df in df_list:
            df.reset_index(inplace = True, drop = True)

    def resample_reviews(self): ##ASK SOMEONE TO DOUBLE CHECK THIS!

        if self.grain == "day":
            pass

        elif self.grain == "week":
            self.review_df["review_publication_date"] = self.review_df["review_publication_date"].dt.strftime('%Y-%W')

        else: #GRAIN IS MONTH OR QUARTER

            #FOR MONTH, USE BUILT IN
            self.review_df["review_publication_date"] = self.review_df["review_publication_date"].dt.strftime('%Y-%m')

            #FOR QUARTER, ADD ADDITIONAL PROCESSING

            if self.grain == "quarter":
                self.review_df["review_publication_date"] = self.review_df["review_publication_date"].apply(lambda month_year: "{}-{}".format(month_year.year, (month_year.month -1)//3 +1 ))

    def transform_text_column(self, input_df, col):

        input_df["{}_none".format(col)] = np.where(input_df[col].isnull(), 1, 0)

        col_values = input_df[[col]]
        valid_values = col_values.dropna()
        valid_values = valid_values[col].unique()

        for val in valid_values:
            input_df["{}_{}".format(col, val)] = np.where(input_df[col] == val, 1, 0)

        input_df.drop(columns = col, inplace = True)

    def transform_given_text_columns(self):

        for col in ["series", "book_language"]: #WE MAY WANT TO TEST ADDING AUTHOR
            self.transform_text_column(self.book_df, col)

    def process_scraper_output(self):
        self.clean_data()
        self.resample_reviews()
        self.transform_given_text_columns()

    def reshape_data_by_book(self):

        review_df_copy = self.review_df.copy()
        review_df_copy["review_count"] = 1

        self.aggregated_df = pd.pivot_table(review_df_copy, index=["book_id"], columns = "review_publication_date", values=["review_count"], aggfunc=np.sum)
        self.aggregated_df.columns = [' '.join(col).strip() for col in self.aggregated_df.columns.values]
        self.aggregated_df.reset_index(inplace = True, drop = False)
        self.aggregated_df.fillna(0, inplace = True)

    def reshape_data_by_date(self):

        review_df_copy = self.review_df.copy()
        review_df_copy["review_count"] = 1

        self.aggregated_df = pd.pivot_table(review_df_copy, index=["book_id", "review_publication_date"], values=["review_count"], aggfunc=np.sum)
        self.aggregated_df = self.aggregated_df.reindex(pd.MultiIndex.from_product(self.aggregated_df.index.levels, names=self.aggregated_df.index.names))
        self.aggregated_df.reset_index(inplace = True, drop = False)
        self.aggregated_df.fillna(0, inplace = True)

        time_period_id_dict = {}
        time_period_list = self.review_df.review_publication_date.unique()
        time_period_list.sort()

        for i in range(0, len(time_period_list)):
            time_period_val = time_period_list[i]
            time_period_id = i + 1
            time_period_id_dict[time_period_val] = time_period_id

        self.aggregated_df["time_id"] = self.aggregated_df["review_publication_date"].apply(lambda date: time_period_id_dict.get(date))

    def merge_book_data_to_aggregated(self):

        self.book_df["book_id"] = self.book_df["book_id"].apply(lambda id: int(id))
        self.aggregated_df["book_id"] = self.aggregated_df["book_id"].apply(lambda id: int(id))
        self.aggregated_df = self.aggregated_df.merge(self.book_df, on = "book_id")

    def aggregate(self, aggregation_type):
        self.process_scraper_output()

        if aggregate_type == "by_book":
            self.reshape_data_by_book()
        elif aggregation_type == "by_date":
            self.reshape_data_by_date()

        self.merge_book_data_to_aggregated()

        return self.aggregated_df

data_file_name_review = "distributed_data_collection/databases/review_data_sample.csv"
data_file_name_book = "distributed_data_collection/databases/book_data_exc_corruption.csv"
start_date = datetime.datetime(2018, 1, 1)
end_date = datetime.datetime(2020, 2, 29)

test_aggregator = Aggregator(data_file_name_review, data_file_name_book, start_date, end_date, "month")
data_by_book = test_aggregator.aggregate("by_book")
data_by_date = test_aggregator.aggregate("by_date")
