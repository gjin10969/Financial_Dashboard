import mysql.connector
from sqlalchemy import create_engine
import threading
from mysql.connector import Error
import numpy as np
import requests
from datetime import datetime, timedelta
import pandas as pd
from binance.client import Client
from tabulate import tabulate
import time 
import os
import urllib.request
import pyfiglet
from tqdm import tqdm

# Database engine setup
engine = create_engine('mysql+mysqlconnector://root:password@localhost/afdashboard')

mirrorxaccount = ["your_account", "your_account", "your_account", "your_account", "your_account", "your_account"]
your_account_account = "your_account"

def get_client(account):
    secret = os.environ.get(f'{account}_secret')
    key = os.environ.get(f'{account}_key')
    if secret and key:
        client = Client(key, secret)
        return client
    else:
        return None

# Define client instances for each account
clients = {account: get_client(account) for account in mirrorxaccount}

def list_to_dataframe(data_list):
    df = pd.DataFrame(data_list)
    df['date'] = df['time']
    df = df.set_index('date')
    df.index = pd.to_datetime(df.index, unit='ms')
    return df

def access_trades_live(initial_mirrorx):
    path = os.getcwd()
    filename_trades = f"{initial_mirrorx}_4H_continuing_trades.csv"
    live_trades_folder = os.path.join(path, 'mirrorxfolder')
    filepath_trades = os.path.join(live_trades_folder, filename_trades)
    print(filepath_trades)
    return filepath_trades

def df_read_csv(file_name):
    df_csv = pd.read_csv(file_name, header=0)
    df_csv = list_to_dataframe(df_csv)
    return df_csv

def run_history_V2(client, file_name, end=str(round(time.time() * 1000))):
    start = 0
    while int(start) < int(end):
        old_trades = df_read_csv(file_name)
        if old_trades.empty:
            print('Empty File uploaded')
            first_update = 0
            last_update = 0
            break
        else:
            if int(start) == 0:
                first_update = old_trades.iloc[-1, -4]
            start = int(old_trades.iloc[-1, -4]) + 1
            new_trades = client.futures_account_trades(startTime=str(start), limit=1000, recWindow=1000)
            if not new_trades:
                last_update = old_trades.iloc[-1, -4]
                break
            else:
                new_trades = list_to_dataframe(new_trades)
                trades_file = pd.concat([old_trades, new_trades], axis=0)
                last_update = trades_file.iloc[-1, -4]
                trades_file.to_csv(file_name, mode='w', index=True, header=True)
    print(f'\nUpdated : {file_name}') 
    print(f'Last trade before : {datetime.fromtimestamp(first_update / 1000.0)}')
    print(f'Last trade after : {datetime.fromtimestamp(last_update / 1000.0)}')

def update_csv():
    files = [access_trades_live(account) for account in mirrorxaccount]
    print("Done Updating SQL")
    on = time.time()

    for client, file in zip(clients.values(), files):
        run_history_V2(client, file)

    end = time.time()
    print('\nTime function : ', end - on)
    time.sleep(0.01)

def connect_to_mysql():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='afdashboard'
    )

def read_csv_and_insert_to_mysql(conn, csv_file_path, table_name):
    def read_csv_and_insert_to_mysql_thread(conn, csv_file_path, table_name):
        try: 
            cursor = conn.cursor()
            cursor.execute(f"TRUNCATE TABLE {table_name}")

            with open(csv_file_path, 'r') as file:
                next(file)
                data = [line.strip().split(',') for line in file]

            for values in data:
                time_str = values[0]
                time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
                values[0] = time_obj.strftime('%Y-%m-%d %H:%M:%S.%f')
                values[3] = int(float(values[3]))

                cursor.execute(f"""
                    INSERT IGNORE INTO {table_name} (date, symbol, id, orderId, side, price, qty, realizedPnl, marginAsset, 
                                            quoteQty, commission, commissionAsset, time, positionSide, buyer, maker)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, values)

            conn.commit()
        except Exception as e:
            print("An error occurred:", e)
        finally:
            cursor.close()

    t = threading.Thread(target=read_csv_and_insert_to_mysql_thread, args=(conn, csv_file_path, table_name))
    t.start()
    t.join()

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Combine the script directory with the subdirectory name
base_dir = os.path.dirname(script_dir)
print(base_dir)

# Change the current working directory to base_dir
os.chdir(base_dir)
# update_csv()
for initial_mirrorx in tqdm(mirrorxaccount, desc='Processing to SQL'):
    conn = connect_to_mysql()
    
    csv_file_path = os.path.join(
        r'C:\Users\User\Documents\financialDashboard_AUG\financialDashboard\afdashboard\mirrorxfolder', 
        f'{initial_mirrorx}_4H_continuing_trades.csv'
    )
    
    your_account_csv_path = os.path.join(
        r'C:\Users\User\Documents\financialDashboard_AUG\financialDashboard\afdashboard\mirrorxfolder',
        f'{your_account_account}.csv'
    )
    
    read_csv_and_insert_to_mysql(conn, csv_file_path, initial_mirrorx)
    print("done", initial_mirrorx)
    
    # Insert data from your_account_csv_path into the your_account table
    read_csv_and_insert_to_mysql(conn, your_account_csv_path, your_account_account)
    print("done", your_account_account)
    
    # winning_rate_per_account(conn, initial_mirrorx)  # Uncomment if this function is required
    
    conn.close()

    ascii_banner = pyfiglet.figlet_format("financial DASHBOARD!!")
    print(ascii_banner)

print("processing cache data please wait for a while.")

with urllib.request.urlopen('http://localhost:8000/api/get_data') as response:
    html = response.read()
if html:
    print("Get data Successfully please refresh your webapp")
else:
    print("may error hehe")
