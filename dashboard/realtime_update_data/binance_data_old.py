import pandas as pd
import numpy as np
import asyncio
from datetime import datetime
# from binance_api_secretkey import *
import json
import os
import concurrent.futures
from binance.client import Client
from datetime import datetime, timedelta
import time
from tqdm import tqdm

import pytz

# Get the current local time
local_time = datetime.now()

# Convert local time to UTC time
utc_time = local_time.astimezone(pytz.utc)

# Format UTC time as a string



# Initial balance for each account
initial_balance = {"your_account" : 121890, "your_account": 121646, "your_account" : 121639, "your_account" : 121561, "your_account": 121935, "your_account" : 112220}

# List of accounts
accounts = [
    "your_account",
    "your_account",
    "your_account",
    "your_account",
    "your_account",
    "your_account",
]

symbols = [
    'BNBUSDT',
    'ATOMUSDT',
    'ADAUSDT',
    'XRPUSDT',
    'SOLUSDT',
    'DOTUSDT',
    'BNBUSDT',
    'UNIUSDT',
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
    profit_dollar = profit_in_dollar(total_balance, initial_bal)
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
def account_metrics_for_client(account_name, client_instance):
    initial_balance_for_account = initial_balance[account_name]
    total_balance_for_account = wallet_balance(client_instance)
    perc_return_for_account = percent_return(total_balance_for_account, initial_balance_for_account)
    unrealized_pnl_for_account = float(client_instance.futures_account()["totalUnrealizedProfit"])
    total_balance_for_account = float(client_instance.futures_account()["totalWalletBalance"])
    margin_balance = total_balance_for_account + unrealized_pnl_for_account
    profit_dollar = profit_in_dollar(margin_balance, initial_balance_for_account)

    return perc_return_for_account, unrealized_pnl_for_account, total_balance_for_account, margin_balance, profit_dollar

# Function to calculate aggregated account metrics across all accounts
def account_metrics(account_name=None):
    total_return = 0.0
    total_unrealized_pnl = 0.0
    total_balance = 0.0
    margin_total = 0.0
    total_profit_dollar = 0.0

    if account_name:
        client = clients.get(account_name)
        if client:
            account_metrics_result = account_metrics_for_client(account_name, client)
            return account_metrics_result  # Return the metrics directly if account_name is provided

    else:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = executor.map(
                lambda item: account_metrics_for_client(item[0], item[1]), clients.items()
            )

        for perc_return_for_account, unrealized_pnl_for_account, total_balance_for_account, margin_balance ,profit_dollar_acc in results:
            total_return += perc_return_for_account
            total_unrealized_pnl += unrealized_pnl_for_account
            total_balance += total_balance_for_account
            margin_total += margin_balance
            total_profit_dollar += profit_dollar_acc

    return total_return, total_unrealized_pnl, total_balance, margin_total, total_profit_dollar

async def metrics(accounts):
    async def get_metrics(account):
        total_return, total_unrealized_pnl, total_balance, margin_total, profit_dollar = await asyncio.to_thread(account_metrics, account)
        return {
            "account": account,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_return": total_return,
            "total_balance": total_balance,
            "margin_total": margin_total,
            'profit_dollar': profit_dollar,
        }

    # Fetch metrics for each account concurrently
    tasks = [get_metrics(account) for account in accounts]
    
    # Initialize tqdm progress bar
    with tqdm(total=len(accounts)) as pbar:
        async def track_progress(tasks):
            results = []
            for task in asyncio.as_completed(tasks):
                result = await task
                results.append(result)
                pbar.update(1)  # Update progress bar for each completed task
            return results

        results = await track_progress(tasks)
    
    # Organize results by category
    organized_results = {
        "total_unrealized_pnl_data": {result["account"]: result["total_unrealized_pnl"] for result in results},
        "total_return_data": {result["account"]: result["total_return"] for result in results},
        "total_balance_data": {result["account"]: result["total_balance"] for result in results},
        "margin_total_data": {result["account"]: result["margin_total"] for result in results},
        "profit_dollar_data": {result["account"]: result["profit_dollar"] for result in results}
    }
    
    # Calculate total for each category
    total_unrealized_pnl_total = sum(organized_results["total_unrealized_pnl_data"].values())
    total_return_total = sum(organized_results["total_return_data"].values())
    total_balance_total = sum(organized_results["total_balance_data"].values())
    margin_total_total = sum(organized_results["margin_total_data"].values())
    profit_dollar_total = sum(organized_results["profit_dollar_data"].values())
    
    # Add total account per data category
    organized_results["total_unrealized_pnl_data"]["MIRRORXTOTAL"] = total_unrealized_pnl_total
    organized_results["total_return_data"]["MIRRORXTOTAL"] = total_return_total
    organized_results["total_balance_data"]["MIRRORXTOTAL"] = total_balance_total
    organized_results["margin_total_data"]["MIRRORXTOTAL"] = margin_total_total
    organized_results["profit_dollar_data"]["MIRRORXTOTAL"] = profit_dollar_total
    
    return organized_results

# Function to save the organized results to a JSON file
def save_metrics_to_json(metrics, timestamp, file_path):
    # Attempt to read existing data from the file
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        data = []  # Initialize empty list if file doesn't exist

    # Append new metrics data under the given timestamp
    data.append({
        "timestamp": timestamp,
        "metrics": metrics
    })

    # Write updated data back to the file
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

# Example usage
if __name__ == "__main__":
    print('Updating JSON data, please do not close hehehe')
    # timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    timestamp_utc = utc_time.strftime("%Y-%m-%d %H:%M:%S")

    metrics_result = asyncio.run(metrics(accounts))
    save_metrics_to_json(metrics_result, timestamp_utc, r'C:\Users\User\Documents\jonathan-dashboard\PINAKA_LATEST\financialDashboard\account_metrics.json')
    print(f"Metrics have been saved to account_metrics.json with timestamp: {timestamp_utc}")

print('Successfully')
time.sleep(2)


