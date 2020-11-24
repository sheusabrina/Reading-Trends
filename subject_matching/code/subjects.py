#!/usr/bin/env python
# coding: utf-8

# # Pulling subject/genre information

# This file contains the code used to pull subject information and merge it into the Goodreads data.


import json
import pandas as pd
import numpy as np

from olclient.openlibrary import OpenLibrary

import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer


## Initial arguments at the top
input_file = input("Please input file name (no .csv) containing book meta data:\n")

min_k = input("Please select the minimum number of occurences of a subject"
    + "to be included as a feature\n(subject features with occurences below the "
    + "specified value will be dropped):\n")

output_file = input("Please input file name (no .csv) to output"
    + "final dataframe to:\n")


##-----------------##
## Functions
##-----------------##

def ol_pull(ibsn_vec, keys = ["genres", "subjects"]):
    '''
    Take list of isbn values and return information from Open Library based on categories given by 'keys.'
    Outputs dataframe with isbn13 and values for each listed key.
    Books without data listed in 'keys' are not included in the output.
    '''
    ol_data = []

    for isbn in isbn_vec:
        book = ol.Edition.get(isbn = isbn)
        if book != None:
            book_dat = [book.json().get(key) for key in keys]
            ol_data.append([isbn] + book_dat)

    return(pd.DataFrame(ol_data, columns = ["isbn13"] + keyvec))


def naive_feat_sel(df, k = 1):
    '''
    Drop subject features for which there exist k or less books having that subject
    '''
    sub_counts = df.sum(axis = 0)
    to_drop = sub_counts[sub_counts < k].index
    
    return(df.drop(columns = to_drop))



##-----------------##
## Goodreads Data 
##-----------------##

## Load Goodreads data
directory = '../data/'
gr = pd.read_csv(directory + input_file + ".csv")



## Clean data

## Change non-valid isbn numbers to "None"
letters = re.compile("[A-Za-z]")
e_12 = re.compile("E\+12")

for i in range(len(gr)):
    if letters.search(gr.isbn13[i]) != None:
        if e_12.search(gr.isbn13[i]) == None:
            gr.loc[i, 'isbn13'] = 'None'

            
## Remove rows with missing (and non-valid) isbn numbers
gr = gr[gr.isbn13 != 'None']
gr.index = range(len(gr))


## Expand ISBN numbers from E+12 format
for i in range(len(gr)):
    gr.loc[i, 'isbn13'] = str(int(pd.to_numeric(gr.loc[i, 'isbn13'])))



##--------------------##
## Open Library Data 
##--------------------##

## Pull data from Open Library given Goodreads ISBNs

## ISBN numbers from Goodreads dataset
isbn_list = gr.isbn13.unique()

## Pull OL book data
isbn_df = ol_pull(isbn_list)



##-----------------------------------##
## Convert subject data to features
##-----------------------------------##

## General Cleaning ##

## Pattern to remove any non-alphabetic characters
letter_patt = re.compile("[^A-Za-z \t]")

## Subject lists
sub_lists = isbn_df.subjects[isbn_df.subjects.notna()]
## Index values for books with subjects
sub_index = sub_lists.index

## For each book, combine subject lists into one string and remove punctuation/digits
sub_text = ["".join(l).lower() for l in sub_lists]
sub_text = [re.sub(letter_patt, " ", t) for t in sub_text]

## Manually change the word 'children' to 'child' because the stemmer doesn't
sub_text = [re.sub("children", "child", t) for t in sub_text]


## Stemming ##

lancaster = nltk.stem.LancasterStemmer()

stemmed_subs = []

for phrase in sub_text:
    stems = " ".join(set([lancaster.stem(word) for word in str.split(phrase)]))
    stemmed_subs.append(stems)

sub_clean = pd.Series(stemmed_subs, name = "clean_subjects", index = sub_index)



## Subjects to features ##

## Binary counts for each subject word
cv = CountVectorizer(stop_words = "english", binary = True)
cv.fit(sub_clean)
sub_feats = cv.transform(sub_clean)

## Change dense data to normal for sake of merging
col_names = np.sort(list(cv.vocabulary_.keys()))

nondense = pd.DataFrame(sub_feats.todense(), columns = col_names, index = sub_index)



## Merging ##

## Assign cleaned subjects to original ISBNs
isbn_clean = isbn_df.join(sub_clean, how = "left")[["isbn13", "clean_subjects"]]

## Assign features to original ISBNs
isbn_feats = isbn_clean.join(nondense, how = "left")



## Finalize output ##

## Remove features with little coverage
isbn_feats_clean = naive_feat_sel(isbn_feats, k = min_k)


## Also, create dataframe for every possible subject to decode stemmed features
uniq_subs = set(str.split(" ".join(sub_text)))
uniq_stems = [lancaster.stem(word) for word in uniq_subs]

decoder = pd.DataFrame({"stem":uniq_stems, "word":list(uniq_subs)})
decoder.sort_values(by = ["stem", "word"], inplace = True)



##--------------------##
## Output
##--------------------##

out_dir = "../output"

isbn_feats_clean.to_csv(out_dir + output_file + ".csv", index = False)

decoder.to_csv(out_dir + "feature_decoder.csv", index = False)




##--------------------##
## Match Statistics
##--------------------##


## Direct match rate
nomatch = len(isbn_list) - len(isbn_df)
total = len(isbn_list)

print("Unmatched ISBN count:", nomatch)

print("Unmatched ISBN proportion:", round(nomatch / total * 100, 2), "%")


## Subject/genre rate
val_vec = []

for i in range(len(isbn_df)):
    val = 0
    if isbn_df.genres[i] != None:
        val += 1
    if isbn_df.subjects[i] != None:
        val += 2

    val_vec.append(val)
    
val_vec = np.array(val_vec)


## Print stats

noinfo = ((val_vec == 0)).sum()
print("Number of ISBNs with no subject or genre info:", noinfo, "(", round((noinfo / total) * 100, 2), "%)")

genre_info = ((val_vec == 1)).sum()
print("Number of ISBNs with only genre info:", genre_info, "(", round((genre_info / total) * 100, 2), "%)")

sub_info = ((val_vec == 2)).sum()
print("Number of ISBNs with only subject info:", sub_info, "(", round((sub_info / total) * 100, 2), "%)")

both_info = ((val_vec == 3)).sum()
print("Number of ISBNs with genre and subject info:", both_info, "(", round((both_info / total) * 100, 2), "%)")




