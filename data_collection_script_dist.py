#import libraries
from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import random
import pandas as pd
import math
import sys

from bottle import route, run, template
import threading
import queue

#import classes

from parser_script import Review_Parser, Book_Parser
from scraper_script import Scraper
from data_classes import Book, Review

#SYNTAX EXAMPLE

    #@route('/hello')
    #def hello():
        #return "Hello World!"
