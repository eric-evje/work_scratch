from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

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
        tab_names.append("'" + values[i][0] + "'!A:K")
    # print(tab_names)

    return tab_names

def scan_for_dates(creds, service, tab):
    # Call the Sheets API
    sheet = service.spreadsheets()
    cols = ('ENGINEER', 'PARTNO', 'DESCRIPTION', 'QTY.', 'VENDOR', 
        'VENDOR PARTNO', 'MANUFACTURER', 'MANUF. PARTNO', 
        'APPROX. LEAD TIME [WEEKS]', 'COST EA.', 'EXT COST', 'NOTES')
    
    row_list = []
    try:
        result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                    range=tab).execute()
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
                    row.insert(0, engineer)
                    row_list.append(row)
            except(IndexError):
                # print("index error")
                pass
    except HttpError as e:
        print(e)
        pass
    row_list.append(['','','','','','','','','','','',''])
    df = pd.DataFrame(row_list, columns=cols)    
    return df

if __name__ == '__main__':
    creds, service = credentials()

    tab_names = get_sheet_names(creds, service)

    order_df = []
    for tab in tab_names:
        order_df.append(scan_for_dates(creds, service, tab))

    BOM_df = pd.concat(order_df)
    # print(order_df)
    

    BOM_df['PARTNO'].replace('', np.nan, inplace=True)
    BOM_df.dropna(subset=['PARTNO'], inplace=True)

    print(BOM_df)

    stats_file_name = "Results.csv" 
    BOM_df.to_csv(stats_file_name, sep=',', index=False)
    
