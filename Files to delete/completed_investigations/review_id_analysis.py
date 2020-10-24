#NB: This script was used for a review analysis over the summer. We subsequently redid the analysis more rigorously in 10/2020, and captured the code and notes based on that analysis in a Jupyter notebook.
#DON'T REFER TO THIS SCRIPT. LOOK FOR THE NEW ANALYSIS!

#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

#df = pd.read_csv("review_id_sample_data.csv")
df = pd.read_csv("databases/review_id_data.csv")

#PROCESSING DF
df.rename(columns = {" is_URL_valid": "is_URL_valid", " review_publication_date": "review_publication_date"}, inplace = True)

df.review_publication_date = pd.to_datetime(df.review_publication_date, format = "%b %d %Y", errors = "coerce")

df.sort_values(by = "ID", inplace = True)
df.reset_index(inplace = True, drop = True)

## SUBDFS
valid_df = df[df.is_URL_valid == True].reset_index(drop = True)
invalid_df = df[df.is_URL_valid == False].reset_index(drop = True)

##FORMATING FUNCTIONS

def add_date_ordinal(df_to_modify, date_column_name):
    new_column_name = date_column_name+"_ordinal"
    new_df = df_to_modify.copy()
    new_df[new_column_name] = pd.to_datetime(df_to_modify[date_column_name]).apply(lambda date: date.toordinal())
    return new_df

def add_year(df_to_modify, date_column_name):
    new_column_name = date_column_name+"_year"
    new_df = df_to_modify.copy()
    new_df[new_column_name] = (pd.to_datetime(new_df[date_column_name]).apply(lambda date: date.year))
    new_df[new_column_name] = new_df[new_column_name].apply(lambda year: int(year) if pd.notna(year) else pd.NaT)
    return new_df

def add_is_sequential(df_to_modify):

    new_df = df_to_modify.copy()

    ## select starting point (minimum value in first five lines)
    #this will generally be the first row of the df, unless that is an unusually high date
    min_index = None
    min_date = None

    for index in range(0, 5):
        date = new_df.review_publication_date.iloc[index]

        if (not min_date) or (date < min_date):
            min_index, min_date = index, date

    #Initial Data for Reviewing Sequentials
    last_sequential_index = min_index
    last_sequential_date = min_date
    new_df.at[last_sequential_index, "is_sequential"] = True

    #Review Sequential Loop
    for index in range(min_index + 1, len(new_df) - 1):

        date = new_df.review_publication_date.iloc[index]
        next_date = new_df.review_publication_date.iloc[index + 1]

        if (date >= last_sequential_date) and (next_date >= date):
            new_df.at[index, "is_sequential"] = True
            last_sequential_index = index
            last_sequential_date = date

        else:
            new_df.at[index, "is_sequential"] = False

    #Review Sequential, Last Row
    index = len(new_df) - 1
    date = new_df.review_publication_date.iloc[index]

    if date >= last_sequential_date:
        new_df.at[index, "is_sequential"] = True

    #Review Sequential, First Rows
    if min_index != 0:
        new_df.fillna(value = False, )

    ##return

    return new_df

def select_by_year(df_to_modify, min_year, max_year):

    new_df = df_to_modify.copy()
    new_df = add_year(new_df, "review_publication_date")

    new_df = new_df[(new_df.review_publication_date_year >= min_year) & (new_df.review_publication_date_year <= max_year)].reset_index(drop = True)

    return new_df

#cut_df = select_by_year(valid_df, 2007, 2008)
#print(cut_df)

##DATA SUMMARY FUNCTIONS

def print_data_summary():

    #Values & Calculations
    num_ids_tested = len(df)
    num_ids_valid = len(valid_df)
    num_ids_invalid = len(invalid_df)

    perc_ids_valid = round(100 * num_ids_valid / num_ids_tested , 1)
    perc_ids_invalid = round(100 * num_ids_invalid / num_ids_tested, 1)

    #Print Summary

    print("""
    IDs Tested: {}
    Valid IDs: {} ({}%)
    Invalid IDs: {} ({}%)
    """.format(str(num_ids_tested), str(num_ids_valid), str(perc_ids_valid), str(num_ids_invalid), str(perc_ids_invalid)))

##ID VALIDITY FUNCTIONS

def visualize_validity_kde():

    valid_ids= valid_df.ID.values.tolist()
    invalid_ids = invalid_df.ID.values.tolist()

    with sns.axes_style("white"):
        sns.kdeplot(valid_ids, shade=True, label = "Valid IDs")
        sns.kdeplot(invalid_ids, shade=True, label = "Invalid IDs")

        plt.legend()

    plt.show()

def visualize_validity_strip():

    with sns.axes_style("white"):
        sns.stripplot(x="is_URL_valid", y="ID", data=df, jitter = 0.5)

    plt.title("Review URL IDs")

    plt.show()

## DATE SEQUENTIAL FUNCTIONS

def print_is_dates_sequential():
    df_by_id = valid_df.sort_values(by = "ID").reset_index(drop = True)
    df_by_date = valid_df.sort_values(by = "review_publication_date").reset_index(drop = True)

    list_by_id = df_by_id.values.tolist()
    list_by_date = df_by_date.values.tolist()
    is_sequential = list_by_id == list_by_date

    print("""
    Dates Sequential: {}
    """.format(is_sequential))

def visualize_dates(df_to_show = valid_df):

    ordinal_df = add_date_ordinal(df_to_show, "review_publication_date")

    with sns.axes_style("white"):
        ax = sns.regplot(x = "review_publication_date_ordinal", y = "ID",  data = ordinal_df, ci = None, marker = ".", scatter_kws= {"alpha": 0.5}, line_kws = {"color": "gray"})

        ax.set_ylim(ordinal_df["ID"].min(), ordinal_df["ID"].max())

        ax.set_xlabel("review_publication_date")
        new_xlabels = [date.fromordinal(int(x_val)) for x_val in ax.get_xticks() ]
        ax.set_xticklabels(new_xlabels)
        plt.xticks(rotation = 90)

        plt.title("Review URL IDs by Date")

    plt.tight_layout()
    plt.show()

def visualize_sequential_strip(df_to_show = valid_df):

    new_df = add_is_sequential(df_to_show)

    with sns.axes_style("white"):
        sns.stripplot(x="is_sequential", y="review_publication_date", data=new_df, jitter = 0.5)

        plt.title("Review URL Publication Dates")

    plt.show()

def visualize_sequential_strip_by_year():

    new_df = add_is_sequential(valid_df)
    new_df = add_year(new_df, "review_publication_date")

    with sns.axes_style("white"):
        sns.stripplot(x="review_publication_date_year", y="review_publication_date", hue = "is_sequential", data=new_df, jitter = 0.5)

        plt.title("Review URL Publication Dates")

    plt.show()

## DATE CUTOFF FUNCTIONS

def generate_year_cutoff(sequential_only = True):

    #Generate new_df (sequential or not)

    if sequential_only:
        new_df = add_is_sequential(valid_df)
        new_df = new_df[new_df.is_sequential == True].reset_index(drop = True)

    else:
        new_df = valid_df.copy()

    new_df = add_year(new_df, "review_publication_date")
    year_cutoff_dict = {}

    #identify years

    years_list = new_df.review_publication_date_year.unique().tolist()

    #identify ID cutoffs

    for year in years_list:
        year_df = new_df[new_df.review_publication_date_year == year]

        id_min, id_max = year_df["ID"].min(), year_df["ID"].max()
        year_cutoff_dict[year] = (id_min, id_max)

    return year_cutoff_dict

## ANALYSIS & FINDINGS

#print_data_summary()
#visualize_validity_strip()

#print_is_dates_sequential()
#visualize_dates()
#visualize_sequential_strip()

#print(generate_year_cutoff())

#What happened in 2016?

#visualize_sequential_strip_by_year()
#valid_df_2015_2017 = select_by_year(valid_df, 2015, 2017)
#visualize_dates(valid_df_2015_2017)

#What happened in 2017 - 2020?

valid_df_2017_2020 = select_by_year(valid_df, 2017, 2020)
visualize_dates(valid_df_2017_2020)
