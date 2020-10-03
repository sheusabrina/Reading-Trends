#WE PROBABLY DON'T NEED THIS SCRIPT. I WAS BORED WHILE THE DATA SCRAPED... 

#import libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime as dt

#import classes

from database_script import Book_Database
from database_script import Review_Database
from database_script import Merged_Database

#import objects
from database_script import merged_database

#DATE FILLER
#BAR CHART MAKER

class Visualizer():

    def __init__(self, database):
        self.database = database

    def show_ratings_by_day(self, chart_title = None):

        rating_df = self.database.generate_review_count_by_day()

        dates = rating_df.review_publication_date.dt.date.values.tolist()

        rating_1_counts = rating_df["1"].values.tolist()
        rating_2_counts = rating_df["2"].values.tolist()
        rating_3_counts = rating_df["3"].values.tolist()
        rating_4_counts = rating_df["4"].values.tolist()
        rating_5_counts = rating_df["5"].values.tolist()

        rating_2_bottom = rating_1_counts
        rating_3_bottom = [rating_2_counts[i] + rating_2_bottom[i] for i in list(range(len(dates)))]
        rating_4_bottom = [rating_3_counts[i] + rating_3_bottom[i] for i in list(range(len(dates)))]
        rating_5_bottom = [rating_4_counts[i] + rating_4_bottom[i] for i in list(range(len(dates)))]

        #VISUALIZE

        width_value = 20

        ax = plt.subplot()
        plt.bar(dates, rating_1_counts, label = "1 Star", width = width_value)
        plt.bar(dates, rating_2_counts, label = "2 Stars", bottom = rating_2_bottom, width = width_value)
        plt.bar(dates, rating_3_counts, label = "3 Stars", bottom = rating_3_bottom, width = width_value)
        plt.bar(dates, rating_4_counts, label = "4 Stars", bottom = rating_4_bottom, width = width_value)
        plt.bar(dates, rating_5_counts, label = "5 Stars", bottom = rating_5_bottom, width = width_value)

        #Labels

        if chart_title:
            plt.title(chart_title)

        plt.ylabel("Ratings")
        plt.xlabel("Days")

        plt.xticks(rotation = 45)
        plt.legend()

        plt.show()
        plt.close("all")

test_visualizer = Visualizer(merged_database)
test_visualizer.show_ratings_by_day("Harry Potter & The Sorcerers' Stone Daily Ratings")
