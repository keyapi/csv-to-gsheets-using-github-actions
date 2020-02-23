import numpy as np
import pandas as pd
import os
import json
import pygsheets

def json_file(gsheets_creds_json):
    with open('client.json', 'w') as f:
        json.dump(json.loads(gsheets_creds_json, strict=False), f)
    
def get_worksheet(gsheet_key):
    gc = pygsheets.authorize(service_file='client.json')
    wks = gc.open_by_key(gsheet_key).sheet1
    return wks

def csv_to_gsheet(csv_link, wks):
    df = pd.read_csv(csv_link)
    cols = df.columns.to_list()

    df.dropna(axis=0, subset=[cols[1]],how='any',inplace=True)

    df[cols[0]] = df[cols[0]].str.strip()
    df['numeric'] = pd.to_numeric(df[cols[0]],errors='coerce',downcast='integer')
    df.dropna(axis=0, subset=['numeric'],how='any',inplace=True) 
    df = df.loc[(df['numeric']>=10000) & (df['numeric']<=99999)]

    df[cols[1]] = df[cols[1]].astype(int)
    df[cols[2]] = df[cols[2]].astype(int)
    df['numeric'] = df['numeric'].astype(int)

    df.reset_index(inplace=True, drop=True)
    wks.set_dataframe(df, (1,1), nan="", fit=True)

if __name__ == "__main__":
    gsheets_creds_json = os.environ["GSHEETS_CREDS_JSON"]
    json_file(gsheets_creds_json)
    
    gsheet_key = os.environ["GSHEET_KEY"]   
    wks = get_worksheet(gsheet_key)
    
    csv_link = os.environ["CSV_LINK"]
    csv_to_gsheet(csv_link, wks)
