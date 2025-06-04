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
# from dashboard.binance_data import *
import urllib.request
import pyfiglet
import csv
# from scheduler import url

engine = create_engine('mysql+mysqlconnector://root:password@localhost/dashboard')

mirrorxaccount = ["your_account", "your_account","your_account","your_account", "your_account","your_account"]

# mirrorxaccount = ["your_account", "your_account"]


# print(url)


def get_client(account):
    secret = os.environ.get(f'{account}_secret')
    key = os.environ.get(f'{account}_key')

    if secret and key:
        client = Client(key, secret)
        return client
    else:
        return None

# Define client instances for each account
client_your_account = get_client('your_account')
client_your_account = get_client('your_account')
client_your_account = get_client('your_account')
client_your_account = get_client('your_account')
client_your_account = get_client('your_account')
client_your_account = get_client('your_account')

# Store clients in a dictionary
clients = {
    'your_account': client_your_account,
    'your_account': client_your_account,
    'your_account': client_your_account,
    'your_account': client_your_account,
    'your_account': client_your_account,
    'your_account': client_your_account
}


# Function to access the live trades CSV file path for a given account name
def access_trades_live(acc_name):
    path = os.getcwd()
    filename_trades = f"{acc_name}_4H_continuing_trades.csv"
    live_trades_folder = os.path.join(path, r'C:\Users\User\Documents\financialDashboard_AUG\financialDashboard\dashboard\mirrorxfolder')
    filepath_trades = os.path.join(live_trades_folder, filename_trades)
    return filepath_trades

def list_to_dataframe(data_list):
    df = pd.DataFrame(data_list)
    df['date'] = pd.to_datetime(df['time'], unit='ms')
    df = df.set_index('date')
    return df

def df_read_csv(file_name):
    try:
        df_csv = pd.read_csv(file_name, header=0)
        df_csv['date'] = pd.to_datetime(df_csv['time'], unit='ms')
        df_csv = df_csv.set_index('date')
    except FileNotFoundError:
        df_csv = pd.DataFrame()  # Return an empty DataFrame if file does not exist
    return df_csv

def run_history_V2(client, file_name, end=str(round(time.time()*1000))):
    start = 0
    while int(start) < int(end):
        try:
            old_trades = df_read_csv(file_name)
            
            if old_trades.empty:
                print('Empty File uploaded')
                first_update = 0
                last_update = 0
            else:
                if int(start) == 0:
                    first_update = old_trades.index[-1].timestamp() * 1000
                    
                start = int(old_trades.index[-1].timestamp() * 1000) + 1
                new_trades = client.futures_account_trades(startTime=start, limit=1000)
                
                if isinstance(new_trades, list):  # Check if new_trades is a list
                    if not new_trades:  # Check if the list is empty
                        last_update = old_trades.index[-1].timestamp() * 1000
                        break
                    else:
                        new_trades = list_to_dataframe(new_trades)
                elif isinstance(new_trades, pd.DataFrame):  # Check if new_trades is already a DataFrame
                    if new_trades.empty:
                        last_update = old_trades.index[-1].timestamp() * 1000
                        break
                
                # Remove duplicates before concatenating
                new_trades = new_trades[~new_trades.index.isin(old_trades.index)]
                
                if not old_trades.empty:
                    first_update = old_trades.index[0].timestamp() * 1000
                    
                trades_file = pd.concat([old_trades, new_trades])
                last_update = trades_file.index[-1].timestamp() * 1000
                trades_file.to_csv(file_name, mode='w', header=True)  # Overwrite existing file
        
        except Exception as e:
            print(f"Error updating {file_name}: {str(e)}")
            # Handle the error (e.g., log, retry, etc.)
            break
    
    print(f'\nUpdated : {file_name}') 
    print(f'Last trade before : {datetime.fromtimestamp(first_update / 1000.0)}')
    print(f'Last trade after : {datetime.fromtimestamp(last_update / 1000.0)}')

def update_csv():
    your_account_file = access_trades_live('your_account')
    your_account_file = access_trades_live('your_account')
    your_account_file = access_trades_live('your_account')
    your_account_file = access_trades_live('your_account')
    your_account_file = access_trades_live('your_account')
    your_account_file = access_trades_live('your_account')

    files = [your_account_file, your_account_file, your_account_file, your_account_file, your_account_file, your_account_file]
    clients = [client_your_account, client_your_account, client_your_account, client_your_account, client_your_account, client_your_account]

    on = time.time()

    for client, file in zip(clients, files):
        run_history_V2(client, file)

    end = time.time()

    print('\nTime function : ', end - on)
update_csv()
# Function to connect to MySQL database
def connect_to_mysql():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='dashboard'
    )


# Function to list all tables in the MySQL database
def list_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    return [table[0] for table in tables]


# Function to read CSV file and insert data into MySQL table

def read_csv_and_insert_to_mysql(conn, csv_file_path, mirrorxaccount):
    def read_csv_and_insert_to_mysql_thread(conn, csv_file_path, mirrorxaccount):
        try:
            cursor = conn.cursor()

            # Truncate table before inserting new data
            cursor.execute(f"TRUNCATE TABLE {mirrorxaccount}")

            with open(csv_file_path, 'r', newline='') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)  # Skip header
                for row in csv_reader:
                    try:
                        # Perform data type conversions
                        time_str = row[0]
                        time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')
                        row[0] = time_obj.strftime('%Y-%m-%d %H:%M:%S.%f')

                        # Convert orderId to BIGINT
                        if row[3].strip():  # Assuming orderId is not empty
                            row[3] = int(float(row[3].strip()))  # Convert orderId to int after float conversion
                        else:
                            row[3] = None  # Handle case where orderId is empty or not a valid integer
                        
                        row[5] = float(row[5])  # Convert price to float
                        row[6] = float(row[6])  # Convert qty to float
                        row[7] = float(row[7])  # Convert realizedPnl to float
                        
                        if row[9].strip():  # Convert quoteQty to float or None
                            row[9] = float(row[9].strip())
                        else:
                            row[9] = None

                        # Use parameterized query to avoid SQL injection
                        sql = f"""
                            INSERT IGNORE INTO {mirrorxaccount} (date, symbol, id, orderId, side, price, qty, realizedPnl, marginAsset, 
                                                          quoteQty, commission, commissionAsset, time, positionSide, buyer, maker)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        cursor.execute(sql, row)
                    except ValueError as ve:
                        print(f"ValueError converting row: {row}, Error: {ve}")
                    except Exception as e:
                        print(f"Error converting row: {row}, Error: {e}")

            conn.commit()
        except Exception as e:
            print("An error occurred:", e)
        finally:
            cursor.close()

    t = threading.Thread(target=read_csv_and_insert_to_mysql_thread, args=(conn, csv_file_path, mirrorxaccount))
    t.start()
    t.join()


# Main function to update MySQL tables for all accounts
def main():
    conn = connect_to_mysql()
    if conn:
        tables = list_tables(conn)
        mirrorxaccount = ["your_account", "your_account", "your_account", "your_account", "your_account", "your_account"]

        # Convert all table names from the database to lowercase
        tables = [table.lower() for table in tables]

        for table in mirrorxaccount:
            lower_table = table.lower()  # Convert the mirrorxaccount table name to lowercase for comparison
            if lower_table in tables:
                csv_file_path = access_trades_live(table)
                if os.path.isfile(csv_file_path):
                    read_csv_and_insert_to_mysql(conn, csv_file_path, table)
                    print(f"Data inserted into {table} SQL!")

                    ascii_banner = pyfiglet.figlet_format("financial DASHBOARD!!")
                    print(ascii_banner)

                else:
                    print(f"File {csv_file_path} does not exist")
            else:
                print(f"Table {table} does not exist")

        conn.close()

        # Check API endpoint after updating MySQL tables
        try:
            with urllib.request.urlopen('http://localhost:8000/api/get_data') as response:
                html = response.read()
                if html:
                    print("Get data Successfully please refresh your webapp")
                else:
                    print("may error hehe")
        except Exception as e:
            print(f"Error accessing API endpoint: {e}")
if __name__ == "__main__":
    main()