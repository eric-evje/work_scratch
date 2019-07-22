from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
# import sys

import pandas as pd
import numpy as np

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SAMPLE_SPREADSHEET_ID = '18mWf_41NHGjO9si4ZmuvqOpLuF-8BuHsBgv4AzrQmCY'
SAMPLE_RANGE_NAME = "'SheetNames'!A:B"

def credentials():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    return(creds, service)

def get_sheet_names(creds, service):
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="'SheetNames'!A:B").execute()
    values = result.get('values', [])
    tab_names = []
    for i in range(len(values)):
        tab_names.append(values[i][0])
        
    # print(tab_names)

    return tab_names

def scan_for_line_items(creds, service, tab):
    parent = "RC-ASY" + tab
    tab_name = "'" + tab + "'!A:K"
    # Call the Sheets API
    sheet = service.spreadsheets()
    cols = ('PARENT', 'PARTNO', 'QTY')

    if tab[0] != "-":
        df = pd.DataFrame(columns=cols)
        return df

    row_list = []
    try:
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=tab_name).execute()
        values = result.get('values', [])
        for row in values:
            try:
                row.insert(0, parent)
                row_list.append([row[0], row[1], row[3]])
            except(IndexError):
                # print("index error")
                pass
    except HttpError as e:
        print("Couldn't find sheet{}".format(tab))
        pass
    row_list.append(['','',''])
    df = pd.DataFrame(row_list, columns=cols)
    df = clean_up_frame(df)
    # print(df)   
    return df

def clean_up_frame(df):
    # print(df)
    BOM_start = 0
    for index in range(0, int(len(df))):
        print("value at index: {}".format(df["PARTNO"].iloc[index]))
        if df["PARTNO"].iloc[index] == "PARTNO":
            BOM_start = index + 1
            break 
    df = df[BOM_start:]
    # print("fixed df")
    # print(df)
    return df

def scan_for_dates(creds, service, tab):
    parent = "RC-ASY" + tab
    tab_name = "'" + tab + "'!A:K"
    # Call the Sheets API
    sheet = service.spreadsheets()
    cols = ('ENGINEER', 'PARENT', 'PARTNO', 'DESCRIPTION', 'QTY.', 'VENDOR', 
        'VENDOR PARTNO', 'MANUFACTURER', 'MANUF. PARTNO', 
        'APPROX. LEAD TIME [WEEKS]', 'COST EA.', 'EXT COST', 'NOTES', 'MULTIPLIER', 'EXTENDED_QTY')
    
    row_list = []
    try:
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=tab_name).execute()
        values = result.get('values', [])
        engineer = "unknown"
        for row in values:
            try:
                for cell in row:
                    if cell == "Responsible Engineer":
                        engineer = row[row.index(cell) + 1]
                        break
                if engineer != "unknown":
                    break
            except(IndexError):
                # print("index error")
                pass

        for row in values:
            try:
                if row[7] == '5':
                    # print(row)
                    row.insert(0, parent)
                    row.insert(0, engineer)
                    row_list.append(row)
            except(IndexError):
                # print("index error")
                pass
    except HttpError as e:
        print("Couldn't find sheet{}".format(tab))
        pass
    row_list.append(['','','','','','','','','','','','','','',''])
    df = pd.DataFrame(row_list, columns=cols)    
    return df

def multiple_assy_check(parent, df, add_parts=1):
    try:
        final_multiplier = 0
        df_parent_as_part = df.loc[df["PARTNO"] == parent]
        print("dataframe: \n{}".format(df_parent_as_part))
        # print("Boolean: {}".format(df_parent_as_part.empty()))
        empty = df_parent_as_part.empty
        if  empty != True:
            for i in range(0, len(df_parent_as_part)):
                add_parts *= int(df_parent_as_part["QTY"].iloc[i])
                print("add_parts: {}".format(add_parts))
                new_parent = df_parent_as_part["PARENT"].iloc[i]
                print("new_parent: {}".format(new_parent))
                add_parts *= multiple_assy_check(new_parent, df)
                print("add_parts after multiplication: {}".format(add_parts))
                final_multiplier += add_parts
            return final_multiplier
        else:
            # print("logic loop doesn't work")
            return 1
    except KeyError:
        print("No match found")
        return final_multiplier
    except IndexError:
        print("Not a part")
        return final_multiplier
    except ValueError:
        print("not a number")
        return final_multiplier
    # finally:
    #     print("going right to finally")
    #     return add_parts

def order_quantity(BOM_df, order_df):
    for i in range(0, len(order_df["PARTNO"])):
        try:
            # print(i)
            part_no = order_df["PARTNO"].iloc[i]
            print("root part number: {}".format(part_no))
            parent = order_df["PARENT"].iloc[i]
            single_quantity = order_df["QTY."].iloc[i]
            # print(part_no, single_quantity)

            multiplier = multiple_assy_check(parent, BOM_df)
            print("Final multiplier: {}\n\n".format(multiplier))

            order_df["MULTIPLIER"].iloc[i] = int(multiplier)
            order_df["EXTENDED_QTY"].iloc[i] = int(single_quantity) * multiplier
        except ValueError:
            print("single child assembly qty is not a number: {}".format(single_quantity))
    return order_df

if __name__ == '__main__':
    creds, service = credentials()

    tab_names = get_sheet_names(creds, service)

    full_BOM = []
    for tab in tab_names:
        full_BOM.append(scan_for_line_items(creds, service, tab))

    full_BOM_df = pd.concat(full_BOM)
    # print(order_df)
    
    full_BOM_df['PARTNO'].replace('', np.nan, inplace=True)
    full_BOM_df.dropna(subset=['PARTNO'], inplace=True)

    BOM_file_name = "BOM.csv" 
    full_BOM_df.to_csv(BOM_file_name, sep=',', index=False)
    # sys.open(BOM_file_name)

    order_df = []
    for tab in tab_names:
        order_df.append(scan_for_dates(creds, service, tab))

    weekly_BOM_df = pd.concat(order_df)

    # print("adding nan")
    weekly_BOM_df['PARTNO'].replace('', np.nan, inplace=True)
    # print("cleaning up df")
    weekly_BOM_df.dropna(subset=['PARTNO'], inplace=True)

    order_BOM_df = order_quantity(full_BOM_df, weekly_BOM_df)
    # print(weekly_BOM_df)

    stats_file_name = "Results.csv" 
    order_BOM_df.to_csv(stats_file_name, sep=',', index=False)