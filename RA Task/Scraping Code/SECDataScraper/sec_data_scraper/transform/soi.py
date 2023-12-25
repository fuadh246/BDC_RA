from bs4 import BeautifulSoup
import re
import unicodedata
import pandas as pd
import numpy as np
import html5lib


def extract_tables(soup_content, qtr_date):
    master_table = None
    all_tags = soup_content.find_all(True)
    print(type(all_tags))
    for tag in soup_content.find_all(text=re.compile('^.*CONSOLIDATED SCHEDULE OF INVESTMENTS.*$')):
        if tag.next_sibling is None:  # regular
            date_str = tag.find_next().text.strip()
        else:
            date_str = tag.next_sibling.next_sibling.strip()
        # cnt+=1
        # try:
        #    print('tag is: '+str(tag.string))
        # except AttributeError:
        #    print('cannot print tag text. tag is '+ str(tag))
        # if cnt==12:
        #    tw_tag = tag
        #    print('tag next is '+str(tag.find_next().string))
        #    print(tag.findNext('table'))
        # else:
        #    tr_tag = tag
        date_str = unicodedata.normalize('NFKD', date_str)
        print(date_str)
        if qtr_date.lower() in date_str.lower():
            print('Table found: ')  # c
            html_table = tag.findNext('table')

            if master_table is None:
                master_table = pd.read_html(
                    html_table.prettify(), skiprows=0, flavor='bs4')[0]
                master_table = master_table.applymap(lambda x: unicodedata.normalize(
                    'NFKD', x.strip().strip(u'\u200b').replace('—', '-')) if type(x) == str else x)
                master_table = master_table.replace(r'^\s*$', np.nan, regex=True).replace(r'^\s*\$\s*$', np.nan,
                                                                                          regex=True)
                master_table = master_table.dropna(how='all', axis=0)
            else:
                new_table = pd.read_html(
                    html_table.prettify(), skiprows=0, flavor='bs4')[0]
                new_table = new_table.applymap(lambda x: unicodedata.normalize(
                    'NFKD', x.strip().strip(u'\u200b').replace('—', '-')) if type(x) == str else x)
                new_table = new_table.replace(r'^\s*$', np.nan, regex=True).replace(r'^\s*\$\s*$', np.nan,
                                                                                    regex=True)
                new_table = new_table.dropna(how='all', axis=0)
                print('head')
                print(new_table.head())
                master_table = master_table.append(
                    new_table.dropna(how='all', axis=0).reset_index(
                        drop=True).drop(index=0),
                    ignore_index=True)

    master_table = master_table.applymap(
        lambda x: x.strip().strip(u'\u200b') if type(x) == str else x)
    master_table = master_table.replace(r'^\s*$', np.nan, regex=True).replace(
        r'^\s*\$\s*$', np.nan, regex=True).replace(r'^\s*\)\s*$', np.nan, regex=True)
    return master_table


def process_table(soi_table_df, append_str):
    soi_table_df = soi_table_df.replace(r'^\s*\$\s*$', np.nan, regex=True)
    soi_table_df = soi_table_df.dropna(how='all', axis=1)
    soi_table_df = soi_table_df.dropna(
        how='all', axis=0).reset_index(drop=True)

    # Separate header and data
    soi_table_header = soi_table_df.iloc[0].dropna(how='any')
    print('header: ')
    print(soi_table_header)
    soi_table_data_df = soi_table_df.iloc[1:]
    print('1: ' + str(soi_table_data_df.shape))

    # Drop Full NnN rows
    soi_table_data_df = soi_table_data_df.dropna(how='all', axis=1)
    soi_table_data_df = soi_table_data_df.dropna(
        how='all', axis=0).reset_index(drop=True)
    print('2: ' + str(soi_table_data_df.shape))

    # Rename columns to integer range
    num_cols = soi_table_data_df.shape[1]
    data_col_mapper = dict(zip(soi_table_data_df.columns.to_list(), [
                           i for i in range(0, num_cols)]))
    soi_table_data_df = soi_table_data_df.rename(columns=data_col_mapper)
    print('3: ' + str(soi_table_data_df.shape))
    soi_table_data_df.to_csv('3_'+append_str+'.csv')

    # Drop "Control Instruments" rows
    # soi_table_data_df = soi_table_data_df.dropna(subset=[i for i in range(1, num_cols)], how='all')
    # print('4: ' + str(soi_table_data_df.shape))

    # if num_cols > 7:
    #    # Drop labeled subtotal/total rows
    #    soi_table_data_df = soi_table_data_df.dropna(subset=[1, 3, 5, 6, 7], how='all')
    #    print('5: ' + str(soi_table_data_df.shape))

    # Drop labeled subtotal rows
    soi_table_data_df = soi_table_data_df.dropna(
        subset=[i for i in range(1, num_cols - 2)], how='all')
    print('5: ' + str(soi_table_data_df.shape))

    # Drop subtotal/total rows based on regex
    sub_total_filter_pattern = r'^([Ss]ubtotal)|([Tt]otal)'
    sub_total_filter = soi_table_data_df[0].str.contains(
        sub_total_filter_pattern).replace(np.NaN, False)
    print(sub_total_filter)
    soi_table_data_df = soi_table_data_df[~sub_total_filter]

    # Drop Full NnN rows/cols
    soi_table_data_df = soi_table_data_df.dropna(how='all', axis=1)
    soi_table_data_df = soi_table_data_df.dropna(
        how='all', axis=0).reset_index(drop=True)
    print('6: ' + str(soi_table_data_df.shape))

    # Rename columns to integer range
    num_cols = soi_table_data_df.shape[1]
    data_col_mapper = dict(zip(soi_table_data_df.columns.to_list(), [
                           i for i in range(0, num_cols)]))
    soi_table_data_df = soi_table_data_df.rename(columns=data_col_mapper)

    # Drop totals rows
    soi_table_data_df = soi_table_data_df.dropna(
        subset=[i for i in range(0, num_cols-2)], how='all')
    print('7: ' + str(soi_table_data_df.shape))

    # Forward Fill first 2 columns
    ffill_cols = [i for i in range(0, num_cols-4)]
    soi_table_data_df[ffill_cols] = soi_table_data_df[ffill_cols].fillna(
        method='ffill')
    print('8: ' + str(soi_table_data_df.shape))
    soi_table_data_df.to_csv('8_'+append_str+'.csv')

    # Drop rows with only first 2/3 columns present
    soi_table_data_df = soi_table_data_df.dropna(
        subset=[i for i in range(num_cols-4, num_cols)], how='all')
    print('9: ' + str(soi_table_data_df.shape))

    # Fill data cols NaN with 0
    soi_table_data_df = soi_table_data_df.fillna(0)
    soi_table_data_df = soi_table_data_df.replace('—', 0)
    print('10: ' + str(soi_table_data_df.shape))
    soi_table_data_df.to_csv('10_'+append_str+'.csv', index=False)

    # Replace hyphen with 0
    soi_table_data_df = soi_table_data_df.replace('-', 0, regex=False)

    # Typecast data cols to int
    datatype_conv_dict = dict(
        zip([i for i in range(num_cols-3, num_cols)], [int, int, int]))
    soi_table_data_df = soi_table_data_df.astype(datatype_conv_dict)
    print('11: ' + str(soi_table_data_df.shape))

    numeric_cols = [i for i in range(num_cols-3, num_cols)]
    soi_table_data_df[numeric_cols] = soi_table_data_df[numeric_cols].applymap(
        lambda x: x*1000)

    # first_str = soi_table_data_df[3].iloc[0]
    # print(first_str)
    # ord_l = [ord(c) for c in first_str]

    # print(ord_l)
    # Rename columns to table headers
    header_col_mapper = dict(
        zip(soi_table_data_df.columns.to_list(), soi_table_header))
    soi_table_data_df = soi_table_data_df.rename(columns=header_col_mapper)
    print('12: ' + str(soi_table_data_df.shape))

    return soi_table_data_df
