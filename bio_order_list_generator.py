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
SPREADSHEET_ID = '1IsR2uNiNM6aO227YxyxRUWXU2N25cEfZT9bXWvpGcGY' #RTF v1.0 Master mBOM & Traceability Template


# WRITE_SPREADSHEET_ID = '1It9ZOMteyUv6LCGQOmFZdXyMyJ2IjfA-LEfSC2rxxDA' #SR2.0 order list
WRITE_SPREADSHEET_ID = '1FAkxEasEU2nV6Pv2tz-fufmHyV4MYCgnnSvCdViqIoc' #SR2.1 LLI list
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

def get_sheet_names(creds, service):
    # Call the Sheets API
    # Get the sheet names from the SheetNames sheet
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range="'SheetNames'!A:B").execute()
    values = result.get('values', [])
    tab_names = []
    for i in range(len(values)):
        tab_names.append(values[i][0])

    # print(tab_names)
    return tab_names

def scan_for_line_items(creds, service, tab):
    # Scans each sheet of the master BOM and arranges into dataframe
    parent = tab[0:9]
    tab_name = "'" + tab + "'!A:M"
    # Call the Sheets API
    sheet = service.spreadsheets()

    cols = ('OWNERSHIP', 'PARENT', 'PARTNO', 'DESCRIPTION', 'UNITS', 
        'REV', 'QTY', 'VENDOR', 'VENDOR PARTNO', 'VENDOR LOT #', 
        'MANUFACTURER', 'MANUF. PARTNO', 'PART STORAGE TEMP', 
        'VOLUME PER KIT', 'VOLUME TO PREPARE', 
        'VOLUME PIPETTED INTO KIT', 'FINAL CONCENTRATION', 
        'CSY QC PASS INITIALS', 'PART KIT NAME', 'NOTES')

    # Conditional to skip tabs that don't match the search criteria.
    # Assumes assembly tabs start are of format -XXXXX
    prefix_dict = { 'CSY': ('OWNERSHIP', 'PARENT', 'PARTNO',  'DESCRIPTION', 'UNITS', 'QTY',    
                            'VENDOR',  'VENDOR PARTNO', 'VENDOR LOT #',
                            'PART STORAGE TEMP', 'VOLUME PER KIT',  'VOLUME TO PREPARE',   
                            'VOLUME PIPETTED INTO KIT', 'FINAL CONCENTRATION', 
                            'CSY QC PASS INITIALS', 'MULTIPLIER', 'EXTENDED_QTY', 'TYPE'),
                    'KTB': ('OWNERSHIP', 'PARENT', 'PARTNO', 'DESCRIPTION', 'UNITS', 'QTY', 'VENDOR', 
                            'VENDOR PARTNO', 'VENDOR LOT #', 'PART STORAGE TEMP',   
                            'NOTES', 'PART KIT NAME', 'MULTIPLIER', 'EXTENDED_QTY','TYPE'), 
                    'ASY': ('OWNERSHIP', 'PARENT', 'PARTNO', 'DESCRIPTION', 'REV', 'QTY', 'VENDOR',  
                            'VENDOR PARTNO', 'MANUFACTURER', 'MANUF. PARTNO', 
                            'APPROX. LEAD TIME [WEEKS]', 'COST EA.', 'EXT COST', 'NOTES',
                            'MULTIPLIER', 'EXTENDED_QTY', 'TYPE')}
    prefix = tab[0:3]
    if prefix not in prefix_dict.keys():
        print("Did not attempt to parse {}".format(tab_name))
        df = pd.DataFrame(columns=cols)
        return df
   
    row_list = []
    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=tab_name).execute()
        values = result.get('values', [])
        owner = "unknown"
        for row in values:
            try:
                for cell in row:
                    if cell == "RESPONSIBLE ENGINEER" or cell == "OWNERSHIP":
                        owner = row[row.index(cell) + 1]
                        break
                if owner != "unknown":
                    break
            except(IndexError):
                pass

        for row in values:
            try:
                row.insert(0, parent)
                row.insert(0, owner)
                row_list.append(row)
            except(IndexError):
                pass
    except HttpError as e:
        print("Couldn't find sheet {}".format(tab))
        pass
    empty_list = [''] * len(prefix_dict[prefix])
    row_list.append(empty_list)
    df = pd.DataFrame(row_list, columns=prefix_dict[prefix])
    df = clean_up_frame(df)  
    return df

def pull_old_order_list(creds, service):
    # Call the Sheets API
    tab = "'Procurement - Build Tracking Sheet'!A3:AH"
    sheet = service.spreadsheets()
    cols = ['OWNERSHIP', 'TYPE', 'PARENT', 'PARTNO',
            'DESCRIPTION', 'REV', 'QTY', 'UNITS',
            'VENDOR', 'VENDOR PARTNO', 'VENDOR LOT #',
            'MANUFACTURER', 'MANUF. PARTNO', 'PART STORAGE TEMP',
            'VOLUME PER KIT', 'VOLUME TO PREPARE', 'VOLUME PIPETTED INTO KIT',
            'FINAL CONCENTRATION', 'CSY QC PASS INITIALS',
            'PART KIT NAME', 'NOTES', 'MULTIPLIER',  
            'EXTENDED_QTY', 'APPROX. LEAD TIME [WEEKS]',   
            'COST EA.', 'EXT COST', 'MANUFACTURE RESPONSIBILITY', 'LOT #', 'QTY ORDERED', 
            'QTY RECEIVED', 'ORDERER', 'DATE ORDERED', 
            'EXP REC DATE', 'ORDER NOTES']

    row_list = []
    try:
        result = sheet.values().get(spreadsheetId=WRITE_SPREADSHEET_ID,
                                    range=tab).execute()
        # print(result)
        values = result.get('values', [])

        for row in values:
            try:
                row_list.append(row)
            except(IndexError):
                pass
    except HttpError as e:
        print("Couldn't find sheet {}".format(tab))
        pass
    row_list.append(['']*len(cols))
    df = pd.DataFrame(row_list, columns=cols)
    # df = clean_up_frame(df)  
    return df

def clean_up_frame(df):
    # Remove anything from the dataframe that is not a part line item
    # Any part that is listed before the PARTNO column header will be ignored
    BOM_start = 0
    BOM_end = int(len(df))
    for index in range(0, int(len(df))):
        if df["PARTNO"].iloc[index] == "PARTNO" or df["PARTNO"].iloc[index] == "RC PART NO":
            BOM_start = index + 1
        if df["PARTNO"].iloc[index] == 'General Manuacturing Guidelines':
            BOM_end = index
            break
    df = df[BOM_start : BOM_end]
    return df

def multiple_assy_check(parent, df, add_parts=0):
    # Searches the part number dataframe recursively until it has found
    # all parent assemblies for every individual part in the order list
    try:
        final_multiplier = 0
        df_parent_as_part = df.loc[df["PARTNO"] == parent]
        empty = df_parent_as_part.empty

        if  empty != True:
            for i in range(0, len(df_parent_as_part)):
                # print(df_parent_as_part)
                add_parts += int(df_parent_as_part["QTY"].iloc[i])
                new_parent = df_parent_as_part["PARENT"].iloc[i]
                add_parts *= multiple_assy_check(new_parent, df)
            return add_parts
        else:
            return 1
    except KeyError:
        print("No match found")
        return add_parts
    except IndexError:
        print("Not a part")
        return add_parts
    except ValueError:
        print("not a number")
        return add_parts

def order_quantity(df, builds):
    # Calculated the order quantity for each part
    # Assumes quantities are integers
    for i in range(0, len(df["PARTNO"])):
        try:
            part_no = df["PARTNO"].iloc[i]
            # print("part number: {}".format(part_no))

            parent = df["PARENT"].iloc[i]
            single_quantity = df["QTY"].iloc[i]

            multiplier = multiple_assy_check(parent, df)

            df["MULTIPLIER"].iloc[i] = int(multiplier)
            df["EXTENDED_QTY"].iloc[i] = int(float(single_quantity.replace(',',''))) * multiplier * builds
        except ValueError:
            print(df['PARENT'].iloc[i], df['PARTNO'].iloc[i])
            print("single child assembly qty is not a number: {}".format(single_quantity))
            # print(df.iloc[i])
        except TypeError:
            print(df['PARENT'].iloc[i], df['PARTNO'].iloc[i])
            print("Type Error")
            # print(df.iloc[i])
        except AttributeError:
            print(df['PARENT'].iloc[i], df['PARTNO'].iloc[i])
            print("Attribute Error: {}".format(single_quantity))
    return df

def merge_lists(new, old):
    # Merges the old and new list on the parent, partno, and description

    old_drop_cols = ['OWNERSHIP', 'TYPE',
                    'DESCRIPTION', 'REV', 'QTY', 'UNITS',
                    'VENDOR', 'VENDOR PARTNO', 'VENDOR LOT #',
                    'MANUFACTURER', 'MANUF. PARTNO', 'PART STORAGE TEMP',
                    'VOLUME PER KIT', 'VOLUME TO PREPARE', 'VOLUME PIPETTED INTO KIT',
                    'FINAL CONCENTRATION', 'CSY QC PASS INITIALS',
                    'PART KIT NAME', 'NOTES', 'MULTIPLIER',  
                    'EXTENDED_QTY', 'APPROX. LEAD TIME [WEEKS]',   
                    'COST EA.', 'EXT COST']
    
    old = old.drop(columns=old_drop_cols)

    new = new.merge(old, on=["PARENT", "PARTNO"], how='left')
    new.replace(np.nan, '', inplace=True, regex=True)

    return new

def write_to_sheet(df, sheet_name):
    # Writes the updated order list to the SR2.0 order sheet
    request = service.spreadsheets().values().clear(spreadsheetId=WRITE_SPREADSHEET_ID, 
        range="'Procurement - Build Tracking Sheet'!A:AH", body = {})
    response = request.execute()
    print("Cleared range: {0}".format(response.get('clearedRange')))
    values = df
    data = [
        {
            'range': sheet_name,
            'values': values
        },
        # Additional ranges to update ...
    ]
    body = {
        'valueInputOption': "RAW",
        'data': data
    }
    result = service.spreadsheets().values().batchUpdate(
        spreadsheetId=WRITE_SPREADSHEET_ID, body=body).execute()
    print('{0} cells updated.'.format(result.get('totalUpdatedCells')))

########################## Main function ######################################
if __name__ == '__main__':

    print("Did you remember to update the sheetnames list?")

    # Argument parser
    parser = argparse.ArgumentParser(
        description='This script extracts items and order quantities from the RC2 Master BOM.')
    parser.add_argument('builds', type=int,
                        help='Number of builds to order for')
    parser.add_argument('update_full', type=int,
                        help='Whether (1) or not (0) to update full bom sheet')
    parser.add_argument('deleted_assy_as_parts', type = int,
                        help='Whether (1) or not (0) to delete assemblies in the PARTNO')
    args = parser.parse_args()

    # Aquire Oauth credentials from google
    creds, service = credentials()

    # Retrieve the tab names from the BOM spreadsheet
    tab_names = get_sheet_names(creds, service)

    # Retrieve the full BOM from the master BOM spreadsheet
    full_BOM = []
    for tab in tab_names:
        time.sleep(0.5)
        full_BOM.append(scan_for_line_items(creds, service, tab))

    # Clean up dataframe and drop ros with empty part numbers
    full_BOM_df = pd.concat(full_BOM, sort=False)
    # full_BOM_df['QTY'] = full_BOM_df['QTY'].astype(str)
    full_BOM_df['PARTNO'].replace('', np.nan, inplace=True)
    full_BOM_df.dropna(subset=['PARTNO'], inplace=True)
    full_BOM_df = full_BOM_df.loc[full_BOM_df['PARENT'] != full_BOM_df['PARTNO']]

    for i in range(len(full_BOM_df)):
        string = full_BOM_df['PARTNO'].iloc[i][0:3]
        prefixes = ['CSY', 'ASY', 'KTB']
        if string in prefixes:
            full_BOM_df['TYPE'].iloc[i] = 'ASSEMBLY'
        else:
            full_BOM_df['TYPE'].iloc[i] = 'COMPONENT'

    full_BOM_df = full_BOM_df[['OWNERSHIP', 'TYPE', 'PARENT', 'PARTNO',
                                'DESCRIPTION', 'REV', 'QTY', 'UNITS',
                                'VENDOR', 'VENDOR PARTNO', 'VENDOR LOT #',
                                'MANUFACTURER', 'MANUF. PARTNO', 'PART STORAGE TEMP',
                                'VOLUME PER KIT', 'VOLUME TO PREPARE', 'VOLUME PIPETTED INTO KIT',
                                'FINAL CONCENTRATION', 'CSY QC PASS INITIALS',
                                'PART KIT NAME', 'NOTES', 'MULTIPLIER',  
                                'EXTENDED_QTY', 'APPROX. LEAD TIME [WEEKS]',   
                                'COST EA.', 'EXT COST']]

    # Determine the order quantity based on the builds and quantities from the master bom
    order_df = order_quantity(full_BOM_df, args.builds)

    # Save the dataframe to a csv for posterity and debugging
    order_df.to_csv("BOM.csv") 


    order_df = order_df.reset_index()

    # Retrieve old order list from SR2.0 Order spreadsheet
    old_order_list_df = pull_old_order_list(creds, service)
    # Save for posterity and debugging
    old_order_list_df.to_csv("old.csv")

    # Merge the old and new order lists together.
    updated_df = merge_lists(order_df, old_order_list_df)

    # If directed, delete any assembly that is in the PARTNO column to clean up the ordering sheet 
    if args.deleted_assy_as_parts == 1:
        m = ~updated_df['PARTNO'].str.contains('RC-ASY-\d+')
        updated_df = updated_df[m]

    # Save for posterity and debugging
    # updated_df.to_csv("results.csv")

    # Get ready to send the merged order list back to the Google spreadsheet
    del updated_df["index"]
    full_order_list = updated_df.values.tolist()
    full_order_list.insert(0, ['OWNERSHIP', 'TYPE', 'PARENT', 'PARTNO',
                                'DESCRIPTION', 'REV', 'QTY', 'UNITS',
                                'VENDOR', 'VENDOR PARTNO', 'VENDOR LOT #',
                                'MANUFACTURER', 'MANUF. PARTNO', 'PART STORAGE TEMP',
                                'VOLUME PER KIT', 'VOLUME TO PREPARE', 'VOLUME PIPETTED INTO KIT',
                                'FINAL CONCENTRATION', 'CSY QC PASS INITIALS',
                                'PART KIT NAME', 'NOTES', 'MULTIPLIER',  
                                'EXTENDED_QTY', 'APPROX. LEAD TIME [WEEKS]',   
                                'COST EA.', 'EXT COST', 'MANUFACTURE RESPONSIBILITY', 'LOT #', 'QTY ORDERED', 
                                'QTY RECEIVED', 'ORDERER', 'DATE ORDERED', 
                                'EXP REC DATE', 'ORDER NOTES'])
    updated_df.to_csv("results.csv", index=False)
    update_time = time.strftime("%c")
    full_order_list.insert(0, ["Last updated: " + update_time])

    # If directed, update the SR2.0 order list with merged and updated order list
    if args.update_full == 1:
        print("updating full BOM sheet")
        write_to_sheet(full_order_list, "'Procurement - Build Tracking Sheet'!A1")

    print("Did you remember to update the sheetnames list?")



