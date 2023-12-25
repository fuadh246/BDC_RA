from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd
import numpy as np
import html5lib
import requests
from openpyxl import Workbook
from datetime import datetime
import webbrowser
import os


def get_response(url, headers):
    try:
        response = requests.get(url=url, headers=headers, timeout=20)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"An error occurred on get_response() : {e}")
        return None


def get_content(response):
    try:
        return parse_and_trim(response.content, "HTML")
    except Exception as e:
        print(f"An error occurred during parsing on get_content() : {e}")
        return None


def get_filingLinks(path):
    filing_links = pd.read_excel(path, engine='openpyxl')
    return filing_links


def parse_and_trim(content, content_type):
    if content_type == "HTML":
        soup = BeautifulSoup(content, 'html.parser')
    else:
        soup = BeautifulSoup(content, 'html.parser')
    for tag in soup.recursiveChildGenerator():
        try:
            tag.attrs = None
        except AttributeError:
            pass
    for linebreak in soup.find_all('br'):
        linebreak.extract()
    return soup


def get_file_url(date, filing_links) -> str:
    return filing_links[filing_links['Reporting date']
                        == date]['url'].values[0]
