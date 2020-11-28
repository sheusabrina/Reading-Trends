import pandas as pd
import datetime
import numpy as np

class Aggregator():

    def __init__(self, review_file, book_file, book_column_list, start_date, end_date, grain, print_updates = True, clean_authors = False, subject_file = None):

        self.start_date = start_date
        self.end_date = end_date
        self.grain = grain
        self.print_updates = print_updates
        self.book_file = book_file
        self.subject_file = subject_file
        self.clean_authors = clean_authors
        self.is_sparsity_filter = False

        self.check_grain()

        self.review_column_list = ["review_id","is_URL_valid", "review_publication_date", "book_id"]
        self.book_column_list = ["book_id", "isbn13"]

        for col in book_column_list:
            if col not in self.book_column_list:
                self.book_column_list.append(col)

        na_val_list = ["None", " ", ""]
        col_type_dict = {"review_id": np.float64, "review_publication_date": "str", "book_publication_date": "str", "data_log_time":"str", "is_URL_valid": "str", "book_id": np.float64, "book_language": "str", "num_reviews": np.float64, "num_ratings": np.float64, "avg_rating": np.float64, "isbn13": "str", "series": "str"}

        self.review_df = pd.read_csv(review_file, usecols = self.review_column_list, na_values= na_val_list, dtype = col_type_dict)
        self.book_df = pd.read_csv(book_file, usecols= self.book_column_list, na_values= na_val_list, dtype = col_type_dict)

        if self.subject_file:
            self.subject_df = pd.read_csv(subject_file, na_values= na_val_list, dtype = col_type_dict)

        if self.print_updates:
            print("Aggregator Initiated.")

    def check_grain(self):

        if self.grain not in ["day", "week", "month", "quarter"]:

            print("Invalid Grain. Aggregator will not run correctly")

    def drop_invalid_rows(self, input_df):

        input_df.dropna(inplace = True, how = "all")
        input_df.drop_duplicates(inplace = True)

    def drop_invalid_reviews(self):

        self.review_df = self.review_df[self.review_df.is_URL_valid != "FALSE"].copy()
        self.review_df = self.review_df[self.review_df.is_URL_valid != "False"].copy()
        self.review_df.drop(columns = "is_URL_valid", inplace = True)

    def datetime_conversion(self, input_df):

        date_columns = ["review_publication_date", "reviewer_started_reading_date", "reviewer_finished_reading_date", "reviwer_shelved_date", "data_log_time", "book_publication_date", "book_first_publication_date"]

        for col in input_df.columns:
            if col in date_columns:
                input_df[col] = pd.to_datetime(input_df[col], errors = "coerce")

    def drop_out_of_time_reviews(self):

        self.review_df = self.review_df[self.review_df.review_publication_date >= self.start_date].copy()
        self.review_df = self.review_df[self.review_df.review_publication_date <= self.end_date].copy()

    def drop_reviews_for_unknown_books(self):

        known_book_ids = self.book_df.book_id.unique()
        self.review_df = self.review_df[self.review_df["book_id"].isin(known_book_ids)]

    def drop_unreviewed_books(self):

        reviewed_book_ids = self.review_df.book_id.unique()
        self.book_df = self.book_df[self.book_df["book_id"].isin(reviewed_book_ids)].copy()

    def drop_long_series_names(self):

        if "series" in self.book_df.columns:

            max_characters = 60
            self.book_df["series"] = self.book_df["series"].apply(lambda series: series if ( (len(str(series)) < max_characters) ) else np.nan).copy()

    def rename_subject_columns(self):

        if self.subject_file:

            rename_dict = {}

            for col in self.subject_df.columns:

                if col == "isbn13":
                    pass

                else:
                    new_col_name = "subject_{}".format(col)
                    rename_dict[col] = new_col_name

            self.subject_df.rename(columns= rename_dict, inplace = True)

    def clean_author_values(self):

        if ("book_author" in self.book_column_list) and (self.clean_authors):

            if self.print_updates:
                print("Cleaning Author Data...")

                cleaner = Author_Cleaner(self.book_file)
                cleaner.train()

                self.book_df["book_author"] = self.book_df["book_author"].apply(lambda author: cleaner.get_clean_name(author))

            if self.print_updates:
                print("Author Data Cleaned.")

    def clean_scraped_data(self):

        df_list = [self.review_df, self.book_df]

        for df in df_list:
            self.drop_invalid_rows(df)
            self.datetime_conversion(df)

        self.drop_invalid_reviews()
        self.drop_out_of_time_reviews()
        self.drop_reviews_for_unknown_books()
        self.drop_unreviewed_books()
        self.drop_long_series_names()
        self.clean_author_values()

        for df in df_list:
            df.reset_index(inplace = True, drop = True)

    def clean_subject_data(self):

        if self.subject_file:

            if self.print_updates:
                    print("Cleaning Subject Data...")

            self.subject_df.drop(columns = "clean_subjects", inplace = True)
            self.drop_invalid_rows(self.subject_df)
            self.rename_subject_columns()

            self.subject_df.fillna(0, inplace = True)
            self.subject_df.reset_index(inplace = True, drop = True)

            if self.print_updates:
                    print("Subject Data Cleaned")

    def resample_reviews(self):

        if self.grain == "day":
            self.review_df["review_publication_date"] = self.review_df["review_publication_date"].dt.strftime('%Y-%m-%d')

        elif self.grain == "week":
            self.review_df["review_publication_date"] = self.review_df["review_publication_date"].dt.strftime('%Y-%W')

        elif self.grain == "month":
            self.review_df["review_publication_date"] = self.review_df["review_publication_date"].dt.strftime('%Y-%m')

        elif self.grain == "quarter":
            self.review_df["review_publication_date"] = self.review_df["review_publication_date"].dt.strftime('%Y-%m')
            self.review_df["review_publication_date"] = self.review_df["review_publication_date"].apply(lambda year_month: "{}-{}".format(year_month.split("-")[0], (int(year_month.split("-")[1]) -1)//3 +1) )

    def generate_time_columns(self):

        self.aggregated_df["review_publication_year"] = self.aggregated_df["review_publication_date"].apply(lambda year_grain: int(year_grain.split("-")[0]))
        self.aggregated_df["review_publication_{}".format(self.grain)] = self.aggregated_df["review_publication_date"].apply(lambda year_grain: int(year_grain.split("-")[-1]))

        if self.grain == "day":
            self.aggregated_df["review_publication_month"] = self.aggregated_df["review_publication_date"].apply(lambda year_grain: int(year_grain.split("-")[1]))

    def transform_text_column(self, input_df, col):

        if col in input_df.columns:

            input_df["{}_none".format(col)] = np.where(input_df[col].isnull(), 1, 0)

            col_values = input_df[[col]]
            valid_values = col_values.dropna()
            valid_values = valid_values[col].unique()

            for val in valid_values:
                input_df["{}_{}".format(col, val)] = np.where(input_df[col] == val, 1, 0)

            input_df.drop(columns = col, inplace = True)

    def transform_given_text_columns(self):

        for col in ["series", "book_language", "book_author"]:
            self.transform_text_column(self.book_df, col)

    def process_scraper_output(self):

        if self.print_updates:
            print("Processing Scraper Output...")

        self.clean_scraped_data()
        self.resample_reviews()
        self.transform_given_text_columns()

        if self.print_updates:
            print("Scraper Output Processed.")

    def aggregate_data_by_book(self):

        if self.print_updates:
            print("Aggregating Review Data...")

        review_df_copy = self.review_df.copy()
        review_df_copy["review_count"] = 1

        self.aggregated_df = pd.pivot_table(review_df_copy, index=["book_id"], columns = "review_publication_date", values=["review_count"], aggfunc=np.sum)
        self.aggregated_df.columns = [' '.join(col).strip() for col in self.aggregated_df.columns.values]
        self.aggregated_df.reset_index(inplace = True, drop = False)
        self.aggregated_df.fillna(0, inplace = True)

        if self.print_updates:
            print("Review Data Aggregated.")

    def aggregate_data_by_date(self):

        if self.print_updates:
            print("Aggregating Review Data...")

        review_df_copy = self.review_df.copy()
        review_df_copy["review_count"] = 1

        self.aggregated_df = pd.pivot_table(review_df_copy, index=["book_id", "review_publication_date"], values=["review_count"], aggfunc=np.sum)
        self.aggregated_df = self.aggregated_df.reindex(pd.MultiIndex.from_product(self.aggregated_df.index.levels, names=self.aggregated_df.index.names))
        self.aggregated_df.reset_index(inplace = True, drop = False)
        self.aggregated_df.fillna(0, inplace = True)

        self.generate_time_columns()

        if self.print_updates:
            print("Review Data Aggregated.")

    def merge_book_data_to_aggregated(self):

        if self.print_updates:
            print("Merging Book Data...")

        self.book_df["book_id"] = self.book_df["book_id"].apply(lambda id: int(id))
        self.aggregated_df["book_id"] = self.aggregated_df["book_id"].apply(lambda id: int(id))
        self.aggregated_df = self.aggregated_df.merge(self.book_df, on = "book_id") #SHOULD THIS REMAIN AN INNER MERGE?

        if self.print_updates:
            print("Book Data Merged.")

    def merge_subject_data_to_aggregated(self):

        if self.subject_file:

            if self.print_updates:
                print("Merging Subject Data...")

            self.aggregated_df = self.aggregated_df.merge(self.subject_df, how = "left", on = "isbn13")
            self.aggregated_df.fillna(0, inplace = True)

            if self.print_updates:
                print("Subject Data Merged.")

    def drop_non_features(self):

        non_feature_list = ["isbn13", "review_publication_date"]

        for col in non_feature_list:
            if col in self.aggregated_df.columns:
                self.aggregated_df.drop(columns = col, inplace = True)

    def aggregate(self, aggregation_type):

        self.process_scraper_output()
        self.clean_subject_data()

        if aggregation_type == "by_book":
            self.aggregate_data_by_book()
        elif aggregation_type == "by_date":
            self.aggregate_data_by_date()

        self.merge_book_data_to_aggregated()
        self.merge_subject_data_to_aggregated()
        self.drop_non_features()

        return self.aggregated_df

    def sparsity_filter(self, k):

        if self.print_updates:
            print("Applying Sparsity Filter...")

        cols_to_drop = []

        ##FINDING SPARSE COLUMNS

        for col in self.aggregated_df.columns:
            num_values = self.aggregated_df[col].nunique()

            if num_values == 1:
                cols_to_drop.append(col)

            elif num_values == 2:
                if self.aggregated_df[col].sum() <=2:
                    cols_to_drop.append(col)

        #GENERATING OUTPUT

        self.sparsity_filtered_df = self.aggregated_df.copy()

        for col in cols_to_drop:
            self.sparsity_filtered_df.drop(columns = col, inplace = True)

        #PRINT STATEMENT

        num_col_input = len(self.aggregated_df.columns)
        num_col_dropped = len(cols_to_drop)
        num_col_remaining = len(self.sparsity_filtered_df.columns)

        print("Dropped {:,}/{:,} columns. {:,} columns remaining.".format(num_col_dropped, num_col_input, num_col_remaining))

        self.is_sparsity_filter = True

        return self.sparsity_filtered_df

    def get_annual_time_periods(self, year):

        if self.is_sparsity_filter:
            col_list = self.sparsity_filtered_df.columns
        else:
            col_list = self.aggregated_df.columns

        time_periods = []

        for col in col_list:
            if "review_count" in col:
                if "2020" in col:
                    time_periods.append(col)

        return time_periods

    def get_train_test_split(self, perc_train):

        if self.is_sparsity_filter:
            data = self.sparsity_filtered_df.copy()
        else:
            data = self.aggregated_df.copy()

        data = data.iloc[np.random.permutation(data.index)].reset_index(drop=True)

        num_observations_total = len(data)
        num_observations_train = int(num_observations_total* perc_train)
        num_observations_test = num_observations_total - num_observations_train

        data_train = data.head(num_observations_train).reset_index(drop = True)
        data_test = data.tail(num_observations_test).reset_index(drop = True)

        return data_train, data_test

class Author_Cleaner():

    def __init__(self, book_file):

        na_val_list = ["None", " ", "", "Amazon", "amazon"]

        self.book_df = pd.read_csv(book_file, usecols= ["book_author"], na_values= na_val_list)
        self.book_df.dropna(inplace = True, how = "any")

        self.book_df["book_author_length"] = self.book_df["book_author"].apply(lambda author: len(author))
        self.book_df = self.book_df.sort_values(by = "book_author_length")

        self.author_input_list = list(self.book_df.book_author.unique())

        self.author_dict = {}

    def train(self):

        authors_to_check = [x for x in self.author_input_list]
        single_name_authors = ["Aristophanes", "Aristotle", "Banksy", "Epictetus", "Homer"]

        index = 0

        while index < len(authors_to_check):
            author_current = authors_to_check[index]

            if (" " in author_current) or (author_current in single_name_authors):

                author_duplicates = [author for author in authors_to_check if author_current in author]
                author_duplicates = author_duplicates[1:]

                if author_duplicates:
                    for duplicate in author_duplicates:
                        self.author_dict[duplicate] = author_current
                        authors_to_check.remove(duplicate)
            index +=1

    def get_clean_name(self, input_name):

        clean_name = self.author_dict.get(input_name)

        if not clean_name:
            clean_name = input_name

        return clean_name

##HOW TO USE AGGREGATOR:

#Initiation: Aggregator takes the csv files containing scraped data and transforms them into a format which can be used for modeling. It takes the following arguments:
    #review_file = file name for the csv file containing scraped review data
    #book_file = file name for the csv file containing scraped book data
    #book_column_list = a list of book data fields which should be included in the transformed data table. It can contain any of the following values:
        #book_column_list = ["book_language", "num_reviews", "num_ratings", "avg_rating", "series", "book_author"]
    #start date = all data from before this date will be removed (should be entered as a datetime)
    #end_date = all data from after this date will be removed (should be entered as a datetime)
    #grain = the level at which review dates should be aggregated. It will accept one of the following values:
        #acceptable_values = ["day", "week", "month", "quarter"]
    #subject_file = file name for the csv file containing the openlibrary subject data. Default = None
    #print_updates = Boolean for whether aggregator should print to terminal. Default = True
    #clean_authors = boolean for whether author names should be cleaned. Default = False
#Other Methods:
    #use .aggregate("by_book") or .aggregate("by_date") method to transform data into one of two forms. This method will return an aggregated dataframe.
    #use .sparsity_filter(k) to drop all binary columns which have k or fewer positive values. This method will return a dataframe.
    #use .get_train_test_split(perc_train) to return split dataframes. If this method is called multiple times on the same aggregator object, it will return a different split each time.
    #use .get_annual_time_periods(year) if you aggregated "by_book" and would like a list of all time periods in a given year.


##TESTING AGGREGATOR

data_file_name_review = "distributed_data_collection/databases/review_data_sample.csv"
#data_file_name_review = "distributed_data_collection/databases/review_data.csv"

data_file_name_book = "distributed_data_collection/databases/book_data_sample.csv"
#data_file_name_book = "distributed_data_collection/databases/book_data.csv"
data_file_name_subject = "subject_matching/data/sub_feat_all.csv"

book_column_list = ["num_reviews", "num_ratings", "avg_rating", "series"]

start_date = datetime.datetime(2018, 1, 1)
end_date = datetime.datetime(2020, 2, 29)

#test_aggregator = Aggregator(data_file_name_review, data_file_name_book, book_column_list, start_date, end_date, "month", subject_file = data_file_name_subject)
#test_aggregator = Aggregator(data_file_name_review, data_file_name_book, book_column_list, start_date, end_date, "month")
#test_aggregator = Aggregator(data_file_name_review, data_file_name_book, book_column_list, start_date, end_date, "month", clean_authors = True)

#test_data = test_aggregator.aggregate("by_book")
#print(test_data)

#sparsity_data = test_aggregator.sparsity_filter(2)

#print(sparsity_data)

#dup_value = "J.R.R. Tolkien Christopher Tolkien (Editor) Alan  Lee (artist) (Illustrator)"
#non_dup_value = "Leora Rosenberg"

#test_cleaner = Author_Cleaner(data_file_name_book)
#test_cleaner.train()
#test_cleaner.get_clean_name(dup_value)
#test_cleaner.get_clean_name(non_dup_value)
