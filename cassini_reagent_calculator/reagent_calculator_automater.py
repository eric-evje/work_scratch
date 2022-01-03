'''
Script employing Google Sheets API to automate analysis of reagent use
calculations for Cassini
'''

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError

import pandas as pd
import numpy as np
import time

import argparse

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID of READ spreadsheet.
SPREADSHEET_ID = '1pVIvUz61vQ8UA74E1ngY5_-LhBnqBePjn6H54iaMd2c'

# The ID of WRITE spreadsheet.
WRITE_SPREADSHEET_ID = '1pVIvUz61vQ8UA74E1ngY5_-LhBnqBePjn6H54iaMd2c'

def credentials():
    # Gets credentials from google for accessing read/write access to sheets
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

def return_values(creds, service):
    '''
    gets values from appropriate cell ranges to return as a single row dataframe to append to main df
    and ultimately return as a single csv with results
    '''
    
    #Create empty dataframe
    cols = ['AP', 'SP', 'Img', 'quencher', 'total_wells_req', 'plates_req', 'largest_reservoir', 'waste_mL']
    df = pd.DataFrame(columns=cols)

    #Send get request via Google API for first range from spreadsheet and append to empty dataframe
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range="'Reagent Calculator'!D57:D61").execute()
    wells = result.get('values',[])
    df['AP'] =                  wells[0]
    df['SP'] =                  wells[1]
    df['Img'] =                 wells[2]
    df['quencher'] =            wells[3]
    df['total_wells_req'] =     wells[4]
    df['plates_req'] = np.ceil(float(df['total_wells_req'].iloc[0]) / 96)  

    #Send get request via Google API for second range from spreadsheet and appent to dataframe
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range="'Reagent Calculator'!I20:I21").execute()
    reservoirs = result.get('values', [])
    df['largest_reservoir'] = reservoirs[1]
    df['waste_mL'] = reservoirs[0]
    print(df.head())

    return df

def write_to_sheet(esiv=1000, img_overshoot=2.15, well_plate=2000, quencher_period=1, interweaving=0):
    # Write ESIV
    body = {
    'values': [[esiv],]
    }
    request = service.spreadsheets().values().update(spreadsheetId=WRITE_SPREADSHEET_ID, 
        range="'Reagent Calculator'!B4", valueInputOption='RAW', body=body)
    result = request.execute()
    print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

    # Write Imaging Volume Overshoot
    body = {
    'values': [[img_overshoot],]
    }
    request = service.spreadsheets().values().update(spreadsheetId=WRITE_SPREADSHEET_ID, 
        range="'Reagent Calculator'!B8", valueInputOption='RAW', body=body)
    result = request.execute()
    print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

    # Write Well Plate Effective Volume
    body = {
    'values': [[well_plate],]
    }
    request = service.spreadsheets().values().update(spreadsheetId=WRITE_SPREADSHEET_ID, 
        range="'Reagent Calculator'!B54", valueInputOption='RAW', body=body)
    result = request.execute()
    print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

    # Write quencher period
    body = {
    'values': [[quencher_period],]
    }
    request = service.spreadsheets().values().update(spreadsheetId=WRITE_SPREADSHEET_ID, 
        range="'Reagent Calculator'!B13", valueInputOption='RAW', body=body)
    result = request.execute()
    print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

     # Write interweaving boolean
    body = {
    'values': [[interweaving],]
    }
    request = service.spreadsheets().values().update(spreadsheetId=WRITE_SPREADSHEET_ID, 
        range="'Reagent Calculator'!B32", valueInputOption='RAW', body=body)
    result = request.execute()
    print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

########################## Main function ######################################
if __name__ == '__main__':
    creds, service = credentials()
    df_conditions = pd.read_csv('reagent_calculator_input.csv', dtype='float64')

    for i in range(df_conditions.shape[0]):
        # Write data from input spreadsheet to Google sheet
        esiv = df_conditions['esiv'].iloc[i]
        img_overshoot = df_conditions['img_overshoot'].iloc[i]
        well_plate = df_conditions['well_plate'].iloc[i]
        quencher_period = df_conditions['quencher_period'].iloc[i]
        interweaving=df_conditions['interweaving'].iloc[i]
        write_to_sheet(esiv=esiv, img_overshoot=img_overshoot, well_plate=well_plate, quencher_period=quencher_period, interweaving=interweaving)
        # Sleeps are required to avoid going over reading and writing requests via API
        time.sleep(2)

        # Read calculated values from Google sheet
        df_vals = return_values(creds, service)
        df_conditions['AP'].iloc[i] = df_vals['AP'].iloc[0]
        df_conditions['SP'].iloc[i] = df_vals['SP'].iloc[0]
        df_conditions['Img'].iloc[i] = df_vals['Img'].iloc[0]
        df_conditions['quencher'].iloc[i] = df_vals['quencher'].iloc[0]
        df_conditions['total_wells_req'].iloc[i] = df_vals['total_wells_req'].iloc[0]
        df_conditions['plates_req'].iloc[i] = df_vals['plates_req'].iloc[0]
        df_conditions['largest_reservoir'].iloc[i] = df_vals['largest_reservoir'].iloc[0]
        df_conditions['waste_mL'].iloc[i] = df_vals['waste_mL'].iloc[0]
        # Sleeps are required to avoid going over reading and writing requests via API
        time.sleep(2)

    # Output dataframe as csv for further analysis
    df_conditions.to_csv('reagent_calculator_input.csv', index=False)