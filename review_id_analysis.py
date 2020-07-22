#import libraries
from bs4 import BeautifulSoup
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

#REVIEW ID COLLECTOR
    #Purpose: collect data to test the assumption that there are roughly 3.5B reviews (seems too high?!) with IDs arranged sequentially by date from 0 upwards.
    #Analytic Plan:
        #Part 1: For valid review IDs, confirm that IDs and publication dates are sequential. Additionally, identify ID cutoffs in order to limit eventual scraping to certain time periods.
        #Part 2: Assess invalid review IDs for patterns in order to better estimate the number of reviews and optimize eventual scraping.

#This CSV contains a partial dataset and should not be used for analysis. But it will be enough start writing the code.
df = pd.read_csv("review_id_sample_data.csv")

df = df.head(10)

#PROCESSING DF

df.rename(columns = {" is_URL_valid": "is_URL_valid", " review_publication_date": "review_publication_date"}, inplace = True)

df.review_publication_date = pd.to_datetime(df.review_publication_date, format = "%b %d %Y", errors = "coerce")
df.sort_values(by = "ID", inplace = True)

## SUBDFS
valid_df = df[df.is_URL_valid == True]
invalid_df = df[df.is_URL_valid == False]

##COUNTS & PERCENTAGES
num_ids_tested = len(df)
num_ids_valid = len(valid_df)
num_ids_invalid = len(invalid_df)

perc_ids_valid = round(100 * num_ids_valid / num_ids_tested , 1)
perc_ids_invalid = round(100 * num_ids_invalid / num_ids_tested, 1)

#PART I: DATA SUMMARY

def print_data_summary():

    print("""
    Data Summary:
    IDs Tested: {}
    Valid IDs: {} ({}%)
    Invalid IDs: {} ({}%)
    """.format(str(num_ids_tested), str(num_ids_valid), str(perc_ids_valid), str(num_ids_invalid), str(perc_ids_invalid)))

#print_data_summary()

##PART II: SEQUENTIAL DATES

def is_dates_sequential():
    df_by_id = valid_df.sort_values(by = "ID").reset_index(drop = True)
    df_by_date = valid_df.sort_values(by = "review_publication_date").reset_index(drop = True)

    list_by_id = df_by_id.values.tolist()
    list_by_date = df_by_date.values.tolist()
    is_sequential = list_by_id == list_by_date

    print("""
    Dates Sequential: {}
    """.format(is_sequential))

#is_dates_sequential()
