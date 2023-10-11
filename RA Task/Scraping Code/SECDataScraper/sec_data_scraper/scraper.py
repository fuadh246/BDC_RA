from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd
import numpy as np
import html5lib
import requests
from transform import soi as soi


def parse_and_trim(content, content_type):
    if content_type == 'HTML':
        soup = BeautifulSoup(content, 'html.parser')
    else:
        soup = BeautifulSoup(content, 'html.parser')

    for tag in soup.recursiveChildGenerator():
        try:
            tag.attrs = None
        except AttributeError:
            pass

    for linebreak in soup.find_all('a'):
        linebreak.extract()

    return soup
