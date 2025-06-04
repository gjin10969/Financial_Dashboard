import os
import time
import asyncio
import pandas as pd
from datetime import datetime
from binance.client import Client
import concurrent.futures
import json
import pytz
print('hello world')
# Initial balance for each account
starting_bal = {"your_account" : 121890, "your_account": 121646, "your_account" : 121639, "your_account" : 121561, "your_account": 121935, "your_account" : 112220}
initial_balance = {"your_account" : 11198, "your_account": 11159, "your_account" : 11161, "your_account" : 11112, "your_account": 11185, "your_account" : 105370}
# Stored percentage
stored_perc = -6.27

# List of accounts
accounts = [
    "your_account",
    "your_account",
    "your_account",
    "your_account",
    "your_account",
    "your_account",
]

# Dictionary to store the client instances for each account
clients = {}
for acc in accounts:
    secret = os.environ.get(f"{acc}_secret")
    key = os.environ.get(f"{acc}_key")
    if secret and key:
        client = Client(key, secret)
        clients[acc] = client

# Function to get the total wallet balance for a Binance client
def wallet_balance(client):
    try:
        wallet_account = client.futures_account(recWindow=1000)
        total_balance = float(wallet_account["totalWalletBalance"])
        unrealizedPnl = float(wallet_account["totalUnrealizedProfit"])
        total_balance += unrealizedPnl
        return total_balance
    except Exception as e:
        print(f"Error: {e}")
        return 0  # Return a default value or handle the error accordingly

# Function to calculate and print the profit in dollars for each account
def calculate_profit(account, client):
    total_balance = wallet_balance(client)
    initial_bal = initial_balance[account]
    
    if account == "your_account":
        perc_return = ((8300 * ((total_balance - initial_bal) / initial_bal)) / 860) + stored_perc
        profit_dollar = starting_bal[account] * (perc_return / 100)
    else:
        perc_return = percent_return(total_balance, initial_bal) + stored_perc
        profit_dollar = starting_bal[account] * (perc_return / 100)
    
    return account, profit_dollar

def profit_in_dollar(margin_balance, initial_balance):
    return round(margin_balance - initial_balance, 2)

def print_profits(clients, initial_balances, account=None):
    def calculate_profit(acc, client):
        total_balance = wallet_balance(client)
        initial_bal = initial_balances[acc]
        profit_dollar = profit_in_dollar(total_balance, initial_bal)
        return profit_dollar

    if account:
        account = account.upper()
        
        if account in clients:
            client = clients[account]
            return calculate_profit(account, client)
        else:
            print(f"Account: {account} not found.")
            return None
    else:
        total_profit = 0.0

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_to_acc = {executor.submit(calculate_profit, acc, clients[acc]): acc for acc in clients}

            for future in concurrent.futures.as_completed(future_to_acc):
                try:
                    profit_dollar = future.result()
                    total_profit += profit_dollar
                except Exception as exc:
                    print(f"Account {acc} generated an exception: {exc}")

        return total_profit

# Function to get a Binance client instance for an account
def get_client(account):
    def thread_get_client(account):
        secret = os.environ.get(f"{account}_secret")
        key = os.environ.get(f"{account}_key")
        if secret and key:
            client = Client(key, secret)
            return client
        else:
            return None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(thread_get_client, account)
        client = future.result()

    return client

# Function to calculate the percentage return for an account
def percent_return(margin_balance, init_balance):
    percent_return = round(((margin_balance - init_balance) / init_balance) * 100, 2)
    return percent_return

# Function to calculate various account metrics for a specific client instance
def account_metrics(account_name, client):
    
    initial_balance_for_account = initial_balance[account_name]
    total_balance_for_account = wallet_balance(client)
    try:
        perc_return_for_account = percent_return(total_balance_for_account, initial_balance_for_account)
    except:
        perc_return_for_account = 0
    try:
        unrealized_pnl_for_account = float(client.futures_account()["totalUnrealizedProfit"])
    except:
        unrealized_pnl_for_account = 0
    try:
        total_balance_for_account = float(client.futures_account()["totalWalletBalance"])
    except:
        total_balance_for_account = 0

    margin_balance = total_balance_for_account + unrealized_pnl_for_account

    # Adjust profit calculation based on account type
    if account_name == "your_account":
        perc_return_for_account = ((8300 * ((margin_balance - initial_balance_for_account) / initial_balance_for_account)) / 860) + stored_perc
        profit_dollar = starting_bal[account_name] * (perc_return_for_account / 100)
    else:
        perc_return_for_account += stored_perc
        profit_dollar = starting_bal[account_name] * (perc_return_for_account / 100)

    return perc_return_for_account, unrealized_pnl_for_account, total_balance_for_account, margin_balance, profit_dollar

# Function to calculate aggregated account metrics across all accounts
def calculate_aggregated_metrics():
    total_return = 0.0
    total_unrealized_pnl = 0.0
    total_balance = 0.0
    margin_total = 0.0
    total_profit_dollar = 0.0

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(lambda item: account_metrics(item[0], item[1]), clients.items())

    for perc_return_for_account, unrealized_pnl_for_account, total_balance_for_account, margin_balance, profit_dollar_acc in results:
        total_return += perc_return_for_account
        total_unrealized_pnl += unrealized_pnl_for_account
        total_balance += total_balance_for_account
        margin_total += margin_balance
        total_profit_dollar += profit_dollar_acc

    return total_return, total_unrealized_pnl, total_balance, margin_total, total_profit_dollar

# Function to update CSV files with trade history for each account
def update_csv(client, file_name, start=0, end=None):
    while True:
        old_trades = df_read_csv(file_name)
        if old_trades.empty:
            print('Empty File uploaded')
            first_update = 0
            last_update = 0
            break
        else:
            if start == 0:
                first_update = old_trades.iloc[-1, -4]

            new_trades = client.futures_account_trades(startTime=start, limit=1000)
            if not new_trades:
                last_update = old_trades.iloc[-1, -4]
                break
            else:
                new_trades = list_to_dataframe(new_trades)
                trades_file = pd.concat([old_trades, new_trades], axis=0)
                last_update = trades_file.iloc[-1, -4]

                trades_file.to_csv(file_name, mode='w', index=True, header=True)
                start = int(old_trades.iloc[-1, -4]) + 1

    print(f'\nUpdated : {file_name}')
    print(f'Last trade before : {datetime.fromtimestamp(first_update / 1000.0)}')
    print(f'Last trade after : {datetime.fromtimestamp(last_update / 1000.0)}')

# Function to read CSV file and convert to DataFrame
def df_read_csv(file_name):
    df_csv = pd.read_csv(file_name, header=0)
    df_csv = list_to_dataframe(df_csv)
    return df_csv

# Function to convert list to DataFrame
def list_to_dataframe(data_list):
    df = pd.DataFrame(data_list)
    df['date'] = pd.to_datetime(df['time'], unit='ms')
    df = df.set_index('date')
    return df

def save_metrics_to_json(metrics, timestamp, file_path):
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = []

    data.append({
        "timestamp": timestamp,
        "metrics": metrics
    })

    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Entry point of the script
if __name__ == '__main__':
    # timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    utc_zone = pytz.UTC
    timestamp = datetime.now(utc_zone).strftime('%Y-%m-%d %H:%M:%S')
    # Calculate metrics for each account
    metrics = {
        "total_unrealized_pnl_data": {},
        "total_return_data": {},
        "total_balance_data": {},
        "margin_total_data": {},
        "profit_dollar_data": {}
    }

    for acc_name, client in clients.items():
        perc_return, unrealized_pnl, total_balance, margin_balance, profit_dollar = account_metrics(acc_name, client)

        # Update metrics dictionary
        metrics["total_unrealized_pnl_data"][acc_name] = unrealized_pnl
        metrics["total_return_data"][acc_name] = perc_return
        metrics["total_balance_data"][acc_name] = total_balance
        metrics["margin_total_data"][acc_name] = margin_balance
        metrics["profit_dollar_data"][acc_name] = profit_dollar

    # Calculate MIRRORXTOTAL
    mirrorx_total_unrealized_pnl = sum(metrics["total_unrealized_pnl_data"].values())
    mirrorx_total_return = sum(metrics["total_return_data"].values())
    mirrorx_total_balance = sum(metrics["total_balance_data"].values())
    mirrorx_total_margin = sum(metrics["margin_total_data"].values())
    mirrorx_total_profit_dollar = sum(metrics["profit_dollar_data"].values())

    # Add MIRRORXTOTAL to metrics dictionary
    metrics["total_unrealized_pnl_data"]["MIRRORXTOTAL"] = mirrorx_total_unrealized_pnl
    metrics["total_return_data"]["MIRRORXTOTAL"] = mirrorx_total_return
    metrics["total_balance_data"]["MIRRORXTOTAL"] = mirrorx_total_balance
    metrics["margin_total_data"]["MIRRORXTOTAL"] = mirrorx_total_margin
    metrics["profit_dollar_data"]["MIRRORXTOTAL"] = mirrorx_total_profit_dollar




    # Ensure the path is relative to the script's location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, '..', 'computation_data_app', 'account_metrics.json')
    
    save_metrics_to_json(metrics, timestamp, file_path)

    print(f"Metrics saved to {file_path}")

