import pandas as pd
import numpy as np
import requests
import html5lib
from bs4 import BeautifulSoup
from datetime import datetime
from openpyxl import workbook
import re
import os
import webbrowser
import helper


def main() -> None:
    headers = {
        'User-Agent': 'Goldman Sachs BDC, Inc. GSBD on NYSE'
    }

    filing_links = helper.get_filingLinks(
        '/Users/fuadhassan/Desktop/BDC_RA/GSBD/GSBC_sec_filing_links.xlsx')
    print(filing_links)


if __name__ == "__main__":
    main()
