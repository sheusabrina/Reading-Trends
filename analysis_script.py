#import libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

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
        rating_df = rating_df.pivot(index = "review_publication_date", columns = "rating", values = "review_count")

        ## ADD MORE DATES (DO THIS LATER)

        #min_date = min(rating_df.review_publication_date)
        #max_date = max(rating_df.review_publication_date)
        #new_dates = pd.date_range(min_date, max_date)

        #rating_df.set_index("review_publication_date", inplace = True)
        #rating_df.reindex(new_dates)

        print(rating_df)

        #TURN DF INTO LISTS

        #RECOGNIZE EXISTING VALUES
        #rating_values = rating_df.rating.unique() #LIST OF RATINGS (ie, 3,5)
        #rating_values = [int(x) for x in rating_values]
        #rating_values.sort()
        #num_rating_values = len(rating_values)

        #rating_counts_dict = {}
        #for rating_val in rating_values:
            #rating_counts_dict[rating_val] = rating_df.review_count.values.tolist()

        #print(rating_counts_dict)

        #VISUALIZE

        #ax = plt.subplot()

        #for rating_val in rating_values:

            #pass

test_visualizer = Visualizer(merged_database)
test_visualizer.show_ratings_by_day()
