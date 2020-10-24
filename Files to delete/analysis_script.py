#import libraries
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import datetime as dt



sample_df = pd.read_csv("databases/review_data.csv", low_memory = False)
sample_df.dropna(inplace = True)
sample_df.drop_duplicates(inplace = True)
sample_df = sample_df[sample_df.book_title != "None"]
sample_df = sample_df[sample_df.rating != "None"]
review_counts = sample_df.book_title.value_counts().sort_values(ascending = False)
