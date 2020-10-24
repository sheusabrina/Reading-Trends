#import libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime as dt

#IMPORTING CURRENT REVIEW DATA
review_df = pd.read_csv("databases/review_data.csv", low_memory = False)
review_df.dropna(inplace = True)
review_df.drop_duplicates(inplace = True)

#BOOK COUNTS
review_count_by_book_df = review_df.copy()
review_count_by_book_df = review_count_by_book_df[review_count_by_book_df.book_title != "None"]
review_count_by_book_df = review_count_by_book_df[sample_df.rating != "None"]
review_count_by_book_df = review_count_by_book_df.book_title.value_counts().sort_values(ascending = False)
