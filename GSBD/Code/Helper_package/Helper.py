"""Helper functions for fetching data, parsing content, and more."""
"""
List of functions defined in helper_functions.py:

1. get_response(url, headers)
    Parameters: url (str), headers (dict)
    Returns: response (requests.Response)

2. get_content(response)
    Parameters: response (requests.Response)
    Returns: content (BeautifulSoup object)

3. get_filing_links(path)
    Parameters: path (str)
    Returns: filing_links (DataFrame)

4. parse_and_trim(content, content_type='HTML')
    Parameters: content (bytes), content_type (str)
    Returns: soup (BeautifulSoup object)

5. get_file_url(date, filing_links)
    Parameters: date (str), filing_links (DataFrame)
    Returns: url (str)

6. fetch_filing_data(cik, headers)
    Parameters: cik (str), headers (dict)
    Returns: DataFrame containing recent filing data
"""




import json
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
def get_response(url, headers):
    """
    Fetches the HTTP response from the provided URL with the given headers.

    Args:
    - url (str): The URL to fetch.
    - headers (dict): HTTP headers to be sent with the request.

    Returns:
    - response (requests.Response): The HTTP response object if successful, None otherwise.
    """
    try:
        response = requests.get(url=url, headers=headers, timeout=20)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"An error occurred while fetching the response: {e}")
        return None


def get_content(response):
    """
    Extracts and parses content from the HTTP response.

    Args:
    - response (requests.Response): The HTTP response object.

    Returns:
    - content (BeautifulSoup object): Parsed content if successful, None otherwise.
    """
    try:
        if response is not None:
            return parse_and_trim(response.content, "HTML")
        else:
            print("Response object is None.")
            return None
    except (AttributeError, TypeError, ValueError) as e:
        print(f"An error occurred during content parsing: {e}")
        return None


def get_filing_links(path):
    """
    Reads filing links from an Excel file.

    Args:
    - path (str): Path to the Excel file.

    Returns:
    - filing_links (DataFrame): DataFrame containing filing links if successful, None otherwise.
    """
    try:
        filing_links = pd.read_excel(path, engine='openpyxl')
        return filing_links
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        return None
    except pd.errors.ParserError as e:
        print(f"An error occurred while parsing Excel file: {e}")
        return None


def parse_and_trim(content, content_type='HTML'):
    """
    Parses and trims HTML content using BeautifulSoup.

    Args:
    - content (bytes): Raw content to be parsed.
    - content_type (str): Type of content to be parsed (e.g., HTML).

    Returns:
    - soup (BeautifulSoup object): Parsed content if successful, None otherwise.
    """
    try:
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.recursiveChildGenerator():
            if hasattr(tag, 'attrs'):
                tag.attrs = None
        # Loop through each td element in the BeautifulSoup object
        for td in soup.find_all('td'):
            # Check if the td element is empty or contains only whitespace
            if not td.text.strip():
                # Remove the empty td element
                td.extract()
        for linebreak in soup.find_all('br'):
            linebreak.extract()
        for linebreak in soup.find_all(''):
            linebreak.extract()
        return soup
    except AttributeError as e:
        print(f"An attribute error occurred during parsing: {e}")
        return None
    except ValueError as e:
        print(f"An error occurred during parsing: {e}")
        return None


def get_file_url(date, filing_links) -> str:
    """
    Retrieves the file URL from the DataFrame based on the provided date.

    Args:
    - date (str): The date for which the file URL is required.
    - filing_links (DataFrame): DataFrame containing filing links.

    Returns:
    - url (str): File URL if successful, None otherwise.
    """
    try:
        url = filing_links.loc[filing_links['Reporting date']
                               == date, 'url'].values[0]
        return url
    except IndexError:
        print("No URL found for the given date.")
        return None
    except KeyError as e:
        print(f"Key error occurred: {e}")
        return None


def fetch_filing_data(cik, headers):
    """
    Fetches recent filing data for a given CIK number from the SEC Edgar API.

    Parameters:
    - cik (str): The Central Index Key (CIK) of the company.
    - headers (dict): Headers to be included in the HTTP request.

    Returns:
    - DataFrame: DataFrame containing recent filing data.
    """
    try:
        df = pd.DataFrame()

        # SEC Edgar API endpoint
        api_url = f"https://data.sec.gov/submissions/CIK{cik}.json"

        # Make the API request with timeout
        response = requests.get(api_url, headers=headers, timeout=20)
        response.raise_for_status()  # Raise an exception for bad response status
        time.sleep(1)  # Throttle requests to API
        data = response.json()

        # Check if the expected data is present
        if 'filings' in data and 'recent' in data['filings']:
            # Iterate over keys in 'recent' dictionary
            for key in data['filings']['recent'].keys():
                # Add each value as a row in the DataFrame with 'key' as column name
                df[key] = data['filings']['recent'][key]

            # Filter DataFrame for '10-K' and '10-Q' forms
            filtered_df = df[df['form'].isin(
                ['10-K', '10-Q'])].reset_index(drop=True)

            # Create 'File link' column
            filtered_df['fileLink'] = filtered_df.apply(
                lambda row: f"https://www.sec.gov/Archives/edgar/data/{cik}/{row['accessionNumber'].replace('-', '')}/{row['primaryDocument']}",
                axis=1
            )
            filtered_df['txtFileLink'] = filtered_df.apply(
                lambda row: f"https://www.sec.gov/Archives/edgar/data/{cik}/{row['accessionNumber'].replace('-', '')}/{row['accessionNumber']}.txt",
                axis=1
            )
            # Drop 'index' column if present
            if 'index' in filtered_df.columns:
                filtered_df.drop(columns='index', inplace=True)

            return filtered_df

        else:
            print("Data format is not as expected.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding JSON response.")
        return None
    except KeyError as e:
        print(f"Key error: {e}")
        return None
