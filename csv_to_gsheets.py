import numpy as np
import pandas as pd
import os
import json
from datetime import datetime
import pytz
import pygsheets
from dotenv import load_dotenv

timezone = pytz.timezone('Europe/Berlin')

def json_file(gsheets_creds_json):
    with open('client.json', 'w') as f:
        json.dump(json.loads(gsheets_creds_json, strict=False), f)

def df_method_stock(df):
    df_edit = df.copy()
    cols = df_edit.columns.to_list()

    df_edit.dropna(axis=0, subset=[cols[1]],how='any',inplace=True)

    df_edit[cols[0]] = df_edit[cols[0]].str.strip()
    df_edit['numeric'] = pd.to_numeric(df_edit[cols[0]],errors='coerce',downcast='integer')
    df_edit.dropna(axis=0, subset=['numeric'],how='any',inplace=True) 
    df_edit = df_edit.loc[(df_edit['numeric']>=10000) & (df_edit['numeric']<=99999)]

    df_edit[cols[1]] = df_edit[cols[1]].astype(int)
    df_edit[cols[2]] = df_edit[cols[2]].astype(int)
    df_edit['numeric'] = df_edit['numeric'].astype(int)

    df_edit.reset_index(inplace=True, drop=True)
    return df_edit

def csv_to_df_select_method(csv_file, sep=',', method='no_change'):
    now = datetime.now(timezone)
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    
    df = pd.read_csv(csv_file, sep=sep)
    df['timestamp'] = timestamp
    
    if method == 'stock':
        return df_method_stock(df)
    else:
        return df

def set_df_to_gsheet(gc, gsheet_key, df):
    sh = gc.open_by_key(gsheet_key)
    wks = sh.sheet1
    wks.set_dataframe(df, (1,1), nan="", fit=True)

if __name__ == "__main__":
    try:
        dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
        load_dotenv(dotenv_path)
    except:
        print(' error local .env')

    gsheets_creds_json = os.environ["GSHEETS_CREDS_JSON"]
    json_file(gsheets_creds_json)
    gc = pygsheets.authorize(service_file='client.json')

    json_str = os.environ["CSV_SEP_METHOD_GSHEET"]
    
    for json_item in json.loads(json_str):
        csv_file = json_item['csv_file']
        sep = json_item['sep']
        method = json_item['method']
        gsheet_key = json_item['gsheet_key']

        df = csv_to_df_select_method(csv_file, sep, method)
        set_df_to_gsheet(gc, gsheet_key, df)
