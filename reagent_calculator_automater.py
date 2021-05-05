'''
Copyright (c) ReadCoor, Inc. 2019. All Rights Reserved.

Order list generation script for Bio Kit Build Tracking
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

# The ID and range of a sample spreadsheet.
# SPREADSHEET_ID = '1gGkE6kCS571NcA29B6psceN2jIOLUue-NVYQJiv3KGY' #Sr2.0 BOM
# SPREADSHEET_ID = '1HDtEuJO9kTuiR1M8mG9s-hwDsXHXJcVFahQXsrDq_D0' #SR2.1 BOM
SPREADSHEET_ID = '1pVIvUz61vQ8UA74E1ngY5_-LhBnqBePjn6H54iaMd2c' #RTF v1.0 Master mBOM & Traceability Template


# WRITE_SPREADSHEET_ID = '1It9ZOMteyUv6LCGQOmFZdXyMyJ2IjfA-LEfSC2rxxDA' #SR2.0 order list
WRITE_SPREADSHEET_ID = '1pVIvUz61vQ8UA74E1ngY5_-LhBnqBePjn6H54iaMd2c' #SR2.1 LLI list
# WRITE_RANGE = ["'1_wk'!A1", "'2_wk'!A:Z", "'3_wk'!A:Z", "'4_wk'!A:Z", 
#             "'5_wk'!A:Z", "'6_wk'!A:Z","'7_wk'!A:Z", "'8_wk'!A:Z"]

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
    # Call the Sheets API
    # Get the sheet names from the SheetNames sheet
    cols = ['AP', 'SP', 'Img', 'quencher', 'total_wells_req', 'plates_req', 'largest_reservoir', 'waste_mL']
    df = pd.DataFrame(columns=cols)
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

    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range="'Reagent Calculator'!I20:I21").execute()
    reservoirs = result.get('values', [])
    df['largest_reservoir'] = reservoirs[1]
    df['waste_mL'] = reservoirs[0]
    print(df.head())

    return df

def write_to_sheet(esiv=1000, img_overshoot=2.15, well_plate=2000, quencher_period=1):
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

    # # Write ESIV
    # request = service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, 
    #     range="'Reagent Calculator'B4", valueInputOption=RAW, body=df['ESIV'].iloc[i])
    # print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

########################## Main function ######################################
if __name__ == '__main__':
    creds, service = credentials()
    df_conditions = pd.read_csv('reagent_calculator_input.csv', dtype='float64')

    for i in range(df_conditions.shape[0]):
        esiv = df_conditions['esiv'].iloc[i]
        img_overshoot = df_conditions['img_overshoot'].iloc[i]
        well_plate = df_conditions['well_plate'].iloc[i]
        quencher_period = df_conditions['quencher_period'].iloc[i]
        write_to_sheet(esiv=esiv, img_overshoot=img_overshoot, well_plate=well_plate, quencher_period=quencher_period)
        time.sleep(2)
        df_vals = return_values(creds, service)
        df_conditions['AP'].iloc[i] = df_vals['AP'].iloc[0]
        df_conditions['SP'].iloc[i] = df_vals['SP'].iloc[0]
        df_conditions['Img'].iloc[i] = df_vals['Img'].iloc[0]
        df_conditions['quencher'].iloc[i] = df_vals['quencher'].iloc[0]
        df_conditions['total_wells_req'].iloc[i] = df_vals['total_wells_req'].iloc[0]
        df_conditions['plates_req'].iloc[i] = df_vals['plates_req'].iloc[0]
        df_conditions['largest_reservoir'].iloc[i] = df_vals['largest_reservoir'].iloc[0]
        df_conditions['waste_mL'].iloc[i] = df_vals['waste_mL'].iloc[0]
        time.sleep(2)

    df_conditions.to_csv('reagent_calculator_input.csv', index=False)


    # print("Did you remember to update the sheetnames list?")

    # Argument parser
    # parser = argparse.ArgumentParser(
    #     description='This script extracts items and order quantities from the RC2 Master BOM.')
    # parser.add_argument('builds', type=int,
    #                     help='Number of builds to order for')
    # parser.add_argument('update_full', type=int,
    #                     help='Whether (1) or not (0) to update full bom sheet')
    # parser.add_argument('deleted_assy_as_parts', type = int,
    #                     help='Whether (1) or not (0) to delete assemblies in the PARTNO')
    # args = parser.parse_args()

    # Aquire Oauth credentials from google
    

    # write_to_sheet()
    # return_values(creds, service)

    # # Retrieve the tab names from the BOM spreadsheet
    # tab_names = get_sheet_names(creds, service)

    # # Retrieve the full BOM from the master BOM spreadsheet
    # full_BOM = []
    # for tab in tab_names:
    #     time.sleep(0.5)
    #     full_BOM.append(scan_for_line_items(creds, service, tab))

    # # Clean up dataframe and drop ros with empty part numbers
    # full_BOM_df = pd.concat(full_BOM, sort=False)
    # # full_BOM_df['QTY'] = full_BOM_df['QTY'].astype(str)
    # full_BOM_df['PARTNO'].replace('', np.nan, inplace=True)
    # full_BOM_df.dropna(subset=['PARTNO'], inplace=True)
    # full_BOM_df = full_BOM_df.loc[full_BOM_df['PARENT'] != full_BOM_df['PARTNO']]

    # for i in range(len(full_BOM_df)):
    #     string = full_BOM_df['PARTNO'].iloc[i][0:3]
    #     prefixes = ['CSY', 'ASY', 'KTB']
    #     if string in prefixes:
    #         full_BOM_df['TYPE'].iloc[i] = 'ASSEMBLY'
    #     else:
    #         full_BOM_df['TYPE'].iloc[i] = 'COMPONENT'

    # full_BOM_df = full_BOM_df[['OWNERSHIP', 'TYPE', 'PARENT', 'PARTNO',
    #                             'DESCRIPTION', 'REV', 'QTY', 'UNITS',
    #                             'VENDOR', 'VENDOR PARTNO', 'VENDOR LOT #',
    #                             'MANUFACTURER', 'MANUF. PARTNO', 'PART STORAGE TEMP',
    #                             'VOLUME PER KIT', 'VOLUME TO PREPARE', 'VOLUME PIPETTED INTO KIT',
    #                             'FINAL CONCENTRATION', 'CSY QC PASS INITIALS',
    #                             'PART KIT NAME', 'NOTES', 'MULTIPLIER',  
    #                             'EXTENDED_QTY', 'APPROX. LEAD TIME [WEEKS]',   
    #                             'COST EA.', 'EXT COST']]

    # # Determine the order quantity based on the builds and quantities from the master bom
    # order_df = order_quantity(full_BOM_df, args.builds)

    # # Save the dataframe to a csv for posterity and debugging
    # order_df.to_csv("BOM.csv") 


    # order_df = order_df.reset_index()

    # # Retrieve old order list from SR2.0 Order spreadsheet
    # old_order_list_df = pull_old_order_list(creds, service)
    # # Save for posterity and debugging
    # old_order_list_df.to_csv("old.csv")

    # # Merge the old and new order lists together.
    # updated_df = merge_lists(order_df, old_order_list_df)

    # # If directed, delete any assembly that is in the PARTNO column to clean up the ordering sheet 
    # if args.deleted_assy_as_parts == 1:
    #     m = ~updated_df['PARTNO'].str.contains('RC-ASY-\d+')
    #     updated_df = updated_df[m]

    # # Save for posterity and debugging
    # # updated_df.to_csv("results.csv")

    # # Get ready to send the merged order list back to the Google spreadsheet
    # del updated_df["index"]
    # full_order_list = updated_df.values.tolist()
    # full_order_list.insert(0, ['OWNERSHIP', 'TYPE', 'PARENT', 'PARTNO',
    #                             'DESCRIPTION', 'REV', 'QTY', 'UNITS',
    #                             'VENDOR', 'VENDOR PARTNO', 'VENDOR LOT #',
    #                             'MANUFACTURER', 'MANUF. PARTNO', 'PART STORAGE TEMP',
    #                             'VOLUME PER KIT', 'VOLUME TO PREPARE', 'VOLUME PIPETTED INTO KIT',
    #                             'FINAL CONCENTRATION', 'CSY QC PASS INITIALS',
    #                             'PART KIT NAME', 'NOTES', 'MULTIPLIER',  
    #                             'EXTENDED_QTY', 'APPROX. LEAD TIME [WEEKS]',   
    #                             'COST EA.', 'EXT COST', 'MANUFACTURE RESPONSIBILITY', 'LOT #', 'QTY ORDERED', 
    #                             'QTY RECEIVED', 'ORDERER', 'DATE ORDERED', 
    #                             'EXP REC DATE', 'ORDER NOTES'])
    # updated_df.to_csv("results.csv", index=False)
    # update_time = time.strftime("%c")
    # full_order_list.insert(0, ["Last updated: " + update_time])

    # # If directed, update the SR2.0 order list with merged and updated order list
    # if args.update_full == 1:
    #     print("updating full BOM sheet")
    #     write_to_sheet(full_order_list, "'Procurement - Build Tracking Sheet'!A1")

    # print("Did you remember to update the sheetnames list?")



