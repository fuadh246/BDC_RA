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
    for linebreak in soup.find_all('br'):
        linebreak.extract()
    return soup


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


def process_filingLinks(filing_links):
    date_columns = ['Filing date', 'Reporting date']
    for col in date_columns:
        filing_links[col] = pd.to_datetime(
            filing_links[col], format='%Y-%m-%d')
    for col in date_columns:
        filing_links[col] = filing_links[col].dt.strftime("%B %d, %Y")
    return filing_links


def extract_tables(soup_content, qtr_date):
    master_table = None
    print(qtr_date)

    if qtr_date == 'December 31, 2015' or qtr_date == 'June 30, 2016':
        consolidated_schedule_regex = re.compile(
            r'(?i)^\s*.*\s*CONSOLIDATED\s+SCHEDULE(S|)\s+OF\s+INVESTMENTS\s*(\(.*\)|)\s*-.*\s*\(.*\)$|'
            r'(?i)^\s*.*\s*CONSOLIDATED\s+SCHEDULE(S|)\s+OF\s+INVESTMENTS\s*.*\s*$'
        )
    else:
        consolidated_schedule_regex = re.compile(
            r'(?i)^\s*.*\s*CONSOLIDATED\s+SCHEDULE(S|)\s+OF\s+INVESTMENTS\s*.*\s*$')

    date_regex_pattern = r'([A-Za-z]+\s+\d{1,2},\s+\d{4})'
    for tag in soup_content.find_all(text=re.compile(consolidated_schedule_regex)):
        date_str = re.search(date_regex_pattern, tag.find_next().text)
        if date_str is None:
            date_str = re.search(date_regex_pattern, tag.next.text)
        if date_str is None:
            date_str = re.search(date_regex_pattern,
                                 tag.find_next().next.next.next.text)
        if date_str is not None:
            date_str = str(date_str.group(1))
            date_str = unicodedata.normalize('NFKD', date_str)
            qtr_date_cleaned = qtr_date.replace(',', '').replace(
                ' ', '').replace('\n', '').lower()
            date_str_cleaned = date_str.replace(',', '').replace(
                ' ', '').replace('\n', '').lower()
            print(date_str, qtr_date_cleaned, date_str_cleaned)

            if qtr_date_cleaned == date_str_cleaned:
                html_table = tag.find_next('table')

                new_table = pd.read_html(
                    html_table.prettify(), keep_default_na=False, skiprows=0, flavor='bs4')[0]
                new_table = new_table.applymap(lambda x: unicodedata.normalize(
                    'NFKD', x.strip().strip(u'\u200b').replace('—', '0').replace('%', '')) if type(x) == str else x)

                new_table = new_table.replace(
                    r'^\s*$', np.nan, regex=True).replace(r'^\s*\$\s*$', np.nan, regex=True)
                new_table = new_table.dropna(how='all', axis=0)

                if master_table is None:
                    master_table = new_table
                else:
                    master_table = pd.concat(
                        [master_table, new_table], ignore_index=True)
<<<<<<< HEAD
<<<<<<< HEAD
=======
            # print(master_table)
>>>>>>> 9e06f79 (sep17)
=======
            # print(master_table)
>>>>>>> 9e06f79 (sep17)

            master_table = master_table.replace('N/A', 'No Value')

    master_table = master_table.applymap(
        lambda x: x.strip().strip(u'\u200b') if type(x) == str else x)
    master_table = master_table.replace(r'^\s*$', np.nan, regex=True).replace(
        r'^\s*\$\s*$', np.nan, regex=True).replace(r'^\s*\)\s*$', np.nan, regex=True)
    print(master_table.shape)
    return master_table


def shape(count, df):
    print(f"{count} : shape : {df.shape}")
    count += 1
    return count


def dropna_col_row(df):
    df = df.dropna(how='all', axis=0).reset_index(drop=True)
    df = df.dropna(how='all', axis=1).reset_index(drop=True)
    return df


def drop_if_contain(pattern, df):
    matching_rows = df.apply(
        lambda row: row.str.contains(pattern, flags=re.IGNORECASE, regex=True).any(), axis=1)
    df = df[~matching_rows]
    return df


def rename_columns(df):
    num_cols = df.shape[1]
    data_col_mapper = dict(
        zip(df.columns.to_list(), [i for i in range(0, num_cols)]))
    df = df.rename(columns=data_col_mapper)
    return df


def process_table_function(soi_table_df):
    count = 1
    count = shape(count, soi_table_df)
    soi_table_df = soi_table_df.replace(
        r'^\s*\$\s*$', '', regex=True).replace(r'\n', '', regex=True)
    soi_table_df = soi_table_df.replace('-', '0')
    soi_table_df = dropna_col_row(soi_table_df)
    soi_table_df = soi_table_df.apply(
        lambda x: x.strip() if isinstance(x, str) else x)
    count = shape(count, soi_table_df)

    # drops all the extra top row
    pattern = r'Net asset value per common share|How We Addressed the Matter in Our Audit'
    matching_rows = soi_table_df.apply(
        lambda row: row.str.contains(pattern, flags=re.IGNORECASE, regex=True).any(), axis=1)
    # Check if the pattern exists in the DataFrame
    if matching_rows.any():
        # Extract rows from the first occurrence onwards
        soi_table_df = soi_table_df.iloc[matching_rows.idxmax(
        )+1:].reset_index(drop=True)
    count = shape(count, soi_table_df)

    # drops all the extra bottom row
    pattern = r'Total\s+Investments'
    # Use the apply function to check if the pattern is in any column for each row
    matching_rows = soi_table_df.apply(
        lambda row: row.str.contains(pattern, flags=re.IGNORECASE, regex=True).any(), axis=1)
    # Find the index of the first row that matches the pattern
    # Slice the DataFrame to keep only the rows up to and including the first matching row
    if soi_table_df[matching_rows].index[0] < 20:
        soi_table_df = soi_table_df.loc[:soi_table_df[matching_rows].index[1]].reset_index(
            drop=True)
    else:
        soi_table_df = soi_table_df.loc[:soi_table_df[matching_rows].index[0]].reset_index(
            drop=True)
    count = shape(count, soi_table_df)

    # drop all the col name
    pattern = r'(?:Spread\s*Above|cost|Percentage|Above)'
    soi_table_df = drop_if_contain(pattern, soi_table_df)
    pattern = r'^([Tt]otal)'
    soi_table_df = drop_if_contain(pattern, soi_table_df)
    count = shape(count, soi_table_df)

# drop nan col row
    soi_table_df = dropna_col_row(soi_table_df)
    count = shape(count, soi_table_df)
# drops the sub total
    soi_table_df = soi_table_df.dropna(subset=[soi_table_df.columns[0]])
    count = shape(count, soi_table_df)


# rename col
    soi_table_df = rename_columns(soi_table_df)

    for index, row in soi_table_df.iterrows():
        for column in soi_table_df.columns:
            # pattern = re.compile(r'\([a-zA-Z]\)')
            pattern = re.compile(r'\(\s*[a-zA-Z]\s*\)')
            if str(row[column])[-1] == "+" or '+' in str(row[column]):
                next_column_index = soi_table_df.columns.get_loc(
                    column) + 1
                if str(row[column])[-1] == "+":
                    if (next_column_index < len(soi_table_df.columns)
<<<<<<< HEAD
<<<<<<< HEAD
                                and not pd.isna(row[soi_table_df.columns[next_column_index]])
                            ):
=======
                            and not pd.isna(row[soi_table_df.columns[next_column_index]])
                        ):
>>>>>>> 9e06f79 (sep17)
=======
                            and not pd.isna(row[soi_table_df.columns[next_column_index]])
                        ):
>>>>>>> 9e06f79 (sep17)
                        soi_table_df.at[index, column] = str(
                            soi_table_df.at[index, column])+str(row[soi_table_df.columns[next_column_index]])
                        soi_table_df.at[index,
                                        soi_table_df.columns[next_column_index]] = np.nan

                    next_column_index = soi_table_df.columns.get_loc(
                        next_column_index) + 1
                if (
                    next_column_index < len(soi_table_df.columns)
                    and pattern.search(str(row[soi_table_df.columns[next_column_index]]))
                    and not pd.isna(row[soi_table_df.columns[next_column_index]])
                ):
                    soi_table_df.at[index, column] = str(
                        soi_table_df.at[index, column])+str(row[soi_table_df.columns[next_column_index]])
                    soi_table_df.at[index,
                                    soi_table_df.columns[next_column_index]] = np.nan

            if row[column] == "No Value":
                pattern = re.compile(r'\([0-9]\)')
                next_column_index = soi_table_df.columns.get_loc(column) + 1
                if (
                    next_column_index < len(soi_table_df.columns)
                    and pattern.search(str(row[soi_table_df.columns[next_column_index]]))
                    and not pd.isna(row[soi_table_df.columns[next_column_index]])
                ):
                    soi_table_df.at[index,
                                    column] = row[soi_table_df.columns[next_column_index]]
                    soi_table_df.at[index,
                                    soi_table_df.columns[next_column_index]] = np.nan

    soi_table_df.insert(0, 'Industy', '')

    for index, row in soi_table_df.iterrows():
        if row.nunique() == 2:
            soi_table_df.at[index, 'Industy'] = row.loc[0]
    soi_table_df['Industy'] = soi_table_df['Industy'].replace('', np.nan)

    col_indices = [0, 1, 2]
    soi_table_df.iloc[:, col_indices] = soi_table_df.iloc[:, col_indices].fillna(
        method='ffill')
    col_indices = [0]
    soi_table_df.iloc[:, col_indices] = soi_table_df.iloc[:,
                                                          col_indices].fillna('No value')

    for index, row in soi_table_df.iterrows():
        cleanedList = [x for x in list(row) if str(x) != 'nan']
        row = pd.Series(cleanedList)
        soi_table_df.loc[index] = row

    for index, row in soi_table_df.iterrows():
        for column in soi_table_df.columns:
            if row[column] == "cash/":
                prev_column_index = soi_table_df.columns.get_loc(column) - 1
                next_column_index = soi_table_df.columns.get_loc(column) + 1
                soi_table_df.at[index, soi_table_df.columns[prev_column_index]] = str(row[soi_table_df.columns[prev_column_index]]) + str(
                    soi_table_df.at[index, column])+str(row[soi_table_df.columns[next_column_index]])+str(row[soi_table_df.columns[next_column_index+1]])
                soi_table_df.at[index,
                                soi_table_df.columns[next_column_index]] = np.nan
                soi_table_df.at[index,
                                soi_table_df.columns[next_column_index+1]] = np.nan
                soi_table_df.at[index, column] = np.nan

    for index, row in soi_table_df.iterrows():
        for column in soi_table_df.columns:
            if row[column] == "PIK" or row[column] == 'Non-Cash':
                prev_column_index = soi_table_df.columns.get_loc(column) - 1
                soi_table_df.at[index, soi_table_df.columns[prev_column_index]] = str(soi_table_df.at[index, soi_table_df.columns[prev_column_index]]) + str(
                    soi_table_df.at[index, column])

                soi_table_df.at[index, column] = np.nan
    for index, row in soi_table_df.iterrows():
        cleanedList = [x for x in list(row) if str(x) != 'nan']
        row = pd.Series(cleanedList)
        soi_table_df.loc[index] = row


# drop nan col row
    # soi_table_df = soi_table_df.dropna(axis=0, thresh=4)
    soi_table_df = dropna_col_row(soi_table_df)
    count = shape(count, soi_table_df)
# rename col
    soi_table_df = rename_columns(soi_table_df)

    new_column_names = ['Industry', 'Company', 'Investment Type', 'Spread Above Index',
                        'Interest Rate', 'Maturity Date', 'Principal Shares', 'Amortized Cost',
                        'Percentage of Net Assets', 'Fair Value']

# Set the first 10 column headers
    soi_table_df.columns = new_column_names + list(soi_table_df.columns[10:])
    soi_table_df['Principal Shares'] = pd.to_numeric(
        soi_table_df['Principal Shares'], errors='coerce')
    soi_table_df['Amortized Cost'] = pd.to_numeric(
        soi_table_df['Amortized Cost'], errors='coerce')
    soi_table_df['Percentage of Net Assets'] = pd.to_numeric(
        soi_table_df['Percentage of Net Assets'], errors='coerce')
    soi_table_df['Fair Value'] = pd.to_numeric(
        soi_table_df['Fair Value'], errors='coerce')

    return soi_table_df


def test_file(date, filing_links):
    url = filing_links[filing_links['Reporting date']
                       == date]['Filings URL'].values[0]

    master_table = extract_tables(get_content(
        get_response(url=url, headers=header)), qtr_date=date)
<<<<<<< HEAD
<<<<<<< HEAD
    # processed_table = process_table_function(master_table)
    return master_table
=======
    processed_table = process_table_function(master_table)
    return processed_table
>>>>>>> 9e06f79 (sep17)
=======
    processed_table = process_table_function(master_table)
    return processed_table
>>>>>>> 9e06f79 (sep17)


def run_all(path, filing_links) -> None:
    if not os.path.exists('../MT_csv_file'):
        os.makedirs('../MT_csv_file')
    if not os.path.exists('../PT_csv_file'):
        os.makedirs('../PT_csv_file')

    writer = pd.ExcelWriter(path, engine='openpyxl')
    for qtr_date, html_link in zip(filing_links['Reporting date'], filing_links['Filings URL']):
        print(html_link, qtr_date)
        master_table = extract_tables(get_content(get_response(
            url=html_link, headers=header)), qtr_date=qtr_date)
        master_table.to_csv(
            '../MT_csv_file/'+qtr_date.replace(',', '')+'.csv')

        processed_table = process_table_function(master_table)
        processed_table.to_excel(
            writer, sheet_name=qtr_date.replace(',', ''), index=False)
        processed_table.to_csv(
            '../PT_csv_file/'+qtr_date.replace(',', '')+'.csv')
        writer.book .save(path)
    writer.close()


def main() -> None:
    global header
    header = {'User-Agent': 'GOLUB CAPITAL BDC, Inc.'}
    filling_links_path = "/Users/fuadhassan/Desktop/BDC_RA/GBDC/GBDC__sec_filing_links.xlsx"
    filing_links = process_filingLinks(
        get_filingLinks(path=filling_links_path))
<<<<<<< HEAD
<<<<<<< HEAD
    # test = test_file("September 30, 2017", filing_links=filing_links)
    # print(test)
    # run_all(path='../process_tables_GBDC_Investment.xlsx',
    #         filing_links=filing_links)

    mt = pd.read_csv('September 30 2017.csv')
    pt = process_table_function(mt)
    pt.to_excel("p_September.xlsx")

    mt = pd.read_excel('September 30 2017.xlsx')
    pt.to_excel("p_September.xlsx")
=======
=======
>>>>>>> 9e06f79 (sep17)
    test = test_file("December 31, 2015", filing_links=filing_links)
    print(test)
    run_all(path='../process_tables_GBDC_Investment.xlsx',
            filing_links=filing_links)
<<<<<<< HEAD
>>>>>>> 9e06f79 (sep17)
=======
>>>>>>> 9e06f79 (sep17)


if __name__ == '__main__':
    main()
