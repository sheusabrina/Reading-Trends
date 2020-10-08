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

from parser_script import Review_Parser
from parser_script import Book_Parser
from scraper_script import Scraper
from data_classes import Book, Review

class DistComponent:

    def __init__(self, host, port):
        work_queue = queue.LifoQueue(maxsize=0)
        results_queue = queue.LifoQueue(maxsize=0)

class Master(DistComponent):
    pass

class Slave(DistComponent):
    pass

class Review_Master(Master):
    pass

class Book_Master(Master):
    pass

class Review_Slave(Slave):
    pass

class Book_Slave(Slave):
    pass
