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

engine = create_engine('mysql+mysqlconnector://root:password@localhost/dashboard')

mirrorxaccount = ["MIRRORX1", "MIRRORX2","MIRRORX3","MIRRORX4", "MIRRORX5","MIRRORXFUND"]

# mirrorxaccount = ["MIRRORX1", "MIRRORX2"]





def get_client(account):
    secret = os.environ.get(f'{account}_secret')
    key = os.environ.get(f'{account}_key')

    if secret and key:
        client = Client(key, secret)
        return client
    else:
        return None

# Define client instances for each account
client_MIRRORX1 = get_client('MIRRORX1')
client_MIRRORX2 = get_client('MIRRORX2')
client_MIRRORX3 = get_client('MIRRORX3')
client_MIRRORX4 = get_client('MIRRORX4')
client_MIRRORX5 = get_client('MIRRORX5')
client_MIRRORXFUND = get_client('MIRRORXFUND')

# Store clients in a dictionary
clients = {
    'MIRRORX1': client_MIRRORX1,
    'MIRRORX2': client_MIRRORX2,
    'MIRRORX3': client_MIRRORX3,
    'MIRRORX4': client_MIRRORX4,
    'MIRRORX5': client_MIRRORX5,
    'MIRRORXFUND': client_MIRRORXFUND
}

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


def run_history_V2(client, file_name, end = str(round(time.time()*1000))):
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
                first_update = old_trades.iloc[-1,-4]
            start = int(old_trades.iloc[-1,-4]) + 1
            new_trades = client.futures_account_trades(startTime = str(start), limit = 1000, recWindow = 1000)
            if new_trades == []:
                last_update = old_trades.iloc[-1,-4]
                break
            else:
                new_trades = list_to_dataframe(new_trades)
                trades_file = pd.concat([old_trades, new_trades], axis=0)
                last_update = trades_file.iloc[-1,-4]
                trades_file.to_csv(file_name, mode='w', index = True, header=True)
    print(f'\nUpdated : {file_name}') 
    print(f'Last trade before : {datetime.fromtimestamp(first_update/1000.0)}')
    print(f'Last trade after : {datetime.fromtimestamp(last_update/1000.0)}')

def update_csv():
    MIRRORX1_file = access_trades_live('MIRRORX1')
    MIRRORX2_file = access_trades_live('MIRRORX2')
    MIRRORX3_file = access_trades_live('MIRRORX3')
    MIRRORX4_file = access_trades_live('MIRRORX4')
    MIRRORX5_file = access_trades_live('MIRRORX5')
    MIRRORXFUND_file = access_trades_live('MIRRORXFUND')
    files=[MIRRORX1_file, MIRRORX2_file, MIRRORX3_file, MIRRORX4_file, MIRRORX5_file, MIRRORXFUND_file]
    clients=[client_MIRRORX1, client_MIRRORX2, client_MIRRORX3, client_MIRRORX4, client_MIRRORX5, client_MIRRORXFUND]
    print("Done Updating SQL")

    on = time.time()

    # end = '1673848061028' #1684260035000-MAY17 --> adjust this to initialize
    # start ='1669507200000'
    # file = files[0]
    
    # data = clients[0].futures_account_trades()
    # data = list_to_dataframe(data)
    # data.to_csv(file)

    run_history_V2(clients[0], files[0])
    run_history_V2(clients[1], files[1])
    run_history_V2(clients[2], files[2])
    run_history_V2(clients[3], files[3])
    run_history_V2(clients[4], files[4])
    run_history_V2(clients[5], files[5])

    end = time.time()

    print('\nTime function : ',end - on)
    time.sleep(0.01)


def connect_to_mysql():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='password',
        database='dashboard'
    )
def read_csv_and_insert_to_mysql(conn, csv_file_path, mirrorxaccount):
    def read_csv_and_insert_to_mysql_thread(conn, csv_file_path, mirrorxaccount):
        try: 
            cursor = conn.cursor()
            
            cursor.execute(f"TRUNCATE TABLE {mirrorxaccount}")

            with open(csv_file_path, 'r') as file:
                next(file)
                data = [line.strip().split(',') for line in file]

            for values in data:
                # print("Inserting values:", values)  # Add this line for debugging
                time_str = values[0]
                # Convert from m/d/Y H:M to Y-m-d H:M:S
                time_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S.%f')  # Add %f for milliseconds
                values[0] = time_obj.strftime('%Y-%m-%d %H:%M:%S')  # base on mysql data exported
                values[3] = int(float(values[3]))

                cursor.execute(f"""
                    INSERT IGNORE INTO {mirrorxaccount} (date, symbol, id, orderId, side, price, qty, realizedPnl, marginAsset, 
                                            quoteQty, commission, commissionAsset, time, positionSide, buyer, maker)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 

                """, values)  # Exclude 'id'
                # print(time_obj)

            conn.commit()
        except Exception as e:
            print("An error occurred:", e)
        finally:
            cursor.close()

    t = threading.Thread(target=read_csv_and_insert_to_mysql_thread, args=(conn, csv_file_path, mirrorxaccount))
    t.start()
    t.join()



script_dir = os.path.dirname(os.path.abspath(__file__))

# Combine the script directory with the subdirectory name
base_dir = os.path.dirname(script_dir)

print(base_dir)
# base_dir = r"..\financialDashboard"  # Adjust as needed

# Change the current working directory to base_dir
os.chdir(base_dir)



# update_csv()




# Function to list all tables in the MySQL database
def list_tables(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    return [table[0] for table in tables]

# Main function to update MySQL tables for all accounts
def main():
    conn = connect_to_mysql()
    if conn:
        tables = list_tables(conn)
        mirrorxaccount = ["MIRRORX1", "MIRRORX2", "MIRRORX3", "MIRRORX4", "MIRRORX5", "MIRRORXFUND"]

        # Convert all table names from the database to lowercase
        tables = [table.lower() for table in tables]

        for table in mirrorxaccount:
            lower_table = table.lower()  # Convert the mirrorxaccount table name to lowercase for comparison
            if lower_table in tables:
                csv_file_path = access_trades_live(table)
                if os.path.isfile(csv_file_path):
                    read_csv_and_insert_to_mysql(conn, csv_file_path, lower_table)
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
                    print("Get data Successfully. Please refresh your webapp")
                else:
                    print("Error occurred.")
        except Exception as e:
            print(f"Error accessing API endpoint: {e}")

if __name__ == "__main__":
    main()
