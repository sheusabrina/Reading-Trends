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
