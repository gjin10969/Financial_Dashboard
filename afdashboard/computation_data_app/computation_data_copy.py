import pandas as pd
import numpy as np
import asyncio
from datetime import datetime
from dashboard.computation_data_app.cache_manager import *
# from binance_api_secretkey import *
import json
import os
import concurrent.futures
from binance.client import Client
import time
from datetime import datetime, timedelta

# Initial balance for each account

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
def profit_in_dollar(margin_balance, initial_balance):
    return round(margin_balance - initial_balance, 2)


def calculate_profit(account, client):
    total_balance = wallet_balance(client)
    initial_bal = initial_balance[account]
    profit_dollar = profit_in_dollar(total_balance, initial_bal)
    return account, profit_dollar



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
    return perc_return_for_account, unrealized_pnl_for_account, total_balance_for_account, margin_balance


# Function to calculate aggregated account metrics across all accounts
def account_metrics(account_name=None):
    total_return = 0.0
    total_unrealized_pnl = 0.0
    total_balance = 0.0
    margin_total = 0.0

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

        for perc_return_for_account, unrealized_pnl_for_account, total_balance_for_account, margin_balance in results:
            total_return += perc_return_for_account
            total_unrealized_pnl += unrealized_pnl_for_account
            total_balance += total_balance_for_account
            margin_total += margin_balance

    return total_return, total_unrealized_pnl, total_balance, margin_total





async def metrics(accounts):
    async def get_metrics(account):
        total_return, total_unrealized_pnl, total_balance, margin_total = await asyncio.to_thread(account_metrics, account)
        return {
            "account": account,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_return": total_return,
            "total_balance": total_balance,
            "margin_total": margin_total
        }

    # Fetch metrics for each account concurrently
    tasks = [get_metrics(account) for account in accounts]
    results = await asyncio.gather(*tasks)
    
    # Organize results by category
    organized_results = {
        "total_unrealized_pnl_data": {result["account"]: result["total_unrealized_pnl"] for result in results},
        "total_return_data": {result["account"]: result["total_return"] for result in results},
        "total_balance_data": {result["account"]: result["total_balance"] for result in results},
        "margin_total_data": {result["account"]: result["margin_total"] for result in results}
    }
    
    # Calculate total for each category
    total_unrealized_pnl_total = sum(organized_results["total_unrealized_pnl_data"].values())
    total_return_total = sum(organized_results["total_return_data"].values())
    total_balance_total = sum(organized_results["total_balance_data"].values())
    margin_total_total = sum(organized_results["margin_total_data"].values())
    
    # Add total account per data category
    organized_results["total_unrealized_pnl_data"]["MIRRORXTOTAL"] = total_unrealized_pnl_total
    organized_results["total_return_data"]["MIRRORXTOTAL"] = total_return_total
    organized_results["total_balance_data"]["MIRRORXTOTAL"] = total_balance_total
    organized_results["margin_total_data"]["MIRRORXTOTAL"] = margin_total_total

    print(organized_results)
    
    return organized_results



async def validate_dates(start_date, end_date):
    try:
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        if start_date_dt > end_date_dt:
            raise ValueError("Start date must be before end date.")
        return True  # Dates are valid
    except ValueError as ve:
        print(f"Error: {ve}")
        return False  # Dates are not valid


async def data_computations(cached_data, start_date, end_date, mirror_account, calculation_types, symbols):
    if not await validate_dates(start_date, end_date):
        return None

    try:
        if mirror_account:
            api_data = [entry for entry in cached_data if entry.get('mirrorx_account') == mirror_account]
        else:
            api_data = cached_data

        if symbols:
            api_data = [entry for entry in api_data if entry.get('symbol') in symbols]
        else:
            symbols = set(entry['symbol'] for entry in cached_data)  # Select all symbols
            api_data = [entry for entry in api_data if entry.get('symbol') in symbols]

        df = pd.DataFrame(api_data)
        df.to_csv(r"C:\Users\User\Documents\jonathan-dashboard\PINAKA_LATEST\financialDashboard\storage\data.csv", index=False)
        df['date'] = pd.to_datetime(df['date']).dt.date

        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        filtered_df = df[(df['date'] >= start_date_dt) & (df['date'] <= end_date_dt)]

        results = {}

        async def run_calculation(calculation_type):
            if calculation_type in calculation_functions:
                if calculation_type == 'max_draw':
                    return calculation_type, await calculation_functions[calculation_type](filtered_df, mirror_account)
                elif calculation_type == 'calculate_total_fees':
                    return calculation_type, await calculate_total_fees(filtered_df, start_date, end_date)
                else:
                    return calculation_type, await calculation_functions[calculation_type](filtered_df)
            return calculation_type, None

        tasks = [run_calculation(calculation_type) for calculation_type in calculation_types]
        calculation_results = await asyncio.gather(*tasks)

        for calculation_type, result in calculation_results:
            results[calculation_type] = result
        computation_results = await computation2(api_data, mirror_account, start_date)
        results.update(computation_results)

        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

async def calculate_total_realized_pnl(filtered_df):
    return float(filtered_df['realizedPnl'].sum())


async def fetch_and_save_historical_klines(filename):
    end_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    start_str = (datetime.utcnow() - timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
    interval = Client.KLINE_INTERVAL_4HOUR
    symbol = 'BNBUSDT'
    klines = await asyncio.to_thread(client.get_historical_klines, symbol, interval, start_str, end_str)

    # Extract necessary columns from klines data
    klines_data = [[row[0], row[6], row[4]] for row in klines]  # open_time, close_time, close

    # Create DataFrame from the extracted data
    df_klines = pd.DataFrame(klines_data, columns=['open_time', 'close_time', 'close'])

    # Convert timestamp to datetime
    df_klines['open_time'] = pd.to_datetime(df_klines['open_time'], unit='ms')
    df_klines['close_time'] = pd.to_datetime(df_klines['close_time'], unit='ms')
    df_klines['close'] = df_klines['close'].astype(float)

    # Save DataFrame to CSV
    df_klines.to_csv(filename, index=False)

# Asynchronous function to calculate total fees from the filtered data

async def calculate_total_fees(filtered_df, start_date, end_date):
    try:
        filename = 'historical_klines.csv'
        await fetch_and_save_historical_klines(filename)

        df_klines = pd.read_csv(filename)
        df_klines['open_time'] = pd.to_datetime(df_klines['open_time']).dt.date

        if 'date' in filtered_df.columns:
            filtered_df = filtered_df.copy()
            filtered_df['date'] = pd.to_datetime(filtered_df['date']).dt.date

        start_date_dt = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d').date()

        price_data = {}
        for _, row in df_klines.iterrows():
            open_time = row['open_time']
            close_price = row['close']
            price_data[open_time] = close_price

        total_fees_usdt = 0.0
        for _, row in filtered_df.iterrows():
            date_only = row['date']

            if row['commissionAsset'] == 'BNB':
                price = price_data.get(date_only)
                if price is None:
                    continue
                commission_usdt = row['commission'] * price
            elif row['commissionAsset'] == 'USDT':
                commission_usdt = row['commission']
            else:
                commission_usdt = 0

            total_fees_usdt += commission_usdt

        return total_fees_usdt

    except Exception as e:
        print(f"Error in calculate_total_fees: {e}")
        return 0.0






async def calculate_trading_days(filtered_df):
    return filtered_df['date'].nunique()

async def calculate_winning_days(filtered_df):
    daily_pnl = filtered_df.groupby('date')['realizedPnl'].sum()
    return int((daily_pnl > 0).sum())

async def total_net_profit_loss(filtered_df):
    total_realized_pnl = filtered_df['realizedPnl'].sum()
    total_loss = filtered_df[filtered_df['realizedPnl'] < 0]['realizedPnl'].sum()
    return total_realized_pnl - total_loss

async def calculate_losing_days(filtered_df):
    daily_pnl = filtered_df.groupby('date')['realizedPnl'].sum()
    return int((daily_pnl < 0).sum())

async def breakeven_days(filtered_df):
    daily_pnl = filtered_df.groupby('date')['realizedPnl'].sum()
    return int((daily_pnl == 0).sum())

async def average_profit(filtered_df):
    daily_pnl = filtered_df.groupby('date')['realizedPnl'].sum()
    positive_daily_pnl = daily_pnl[daily_pnl > 0]
    return positive_daily_pnl.mean() if not positive_daily_pnl.empty else 0

async def average_loss(filtered_df):
    daily_pnl = filtered_df.groupby('date')['realizedPnl'].sum()
    negative_daily_pnl = daily_pnl[daily_pnl < 0]
    return negative_daily_pnl.mean() if not negative_daily_pnl.empty else 0

async def profit_loss_ratio(filtered_df):
    daily_pnl = filtered_df.groupby('date')['realizedPnl'].sum()
    positive_daily_pnl = daily_pnl[daily_pnl > 0]
    negative_daily_pnl = daily_pnl[daily_pnl < 0]

    average_profit = positive_daily_pnl.mean() if not positive_daily_pnl.empty else 0
    average_loss = negative_daily_pnl.mean() if not negative_daily_pnl.empty else 0
    return abs(average_profit / average_loss) if average_loss != 0 else float('inf')

async def calculate_total_winning_trades(filtered_df):
    total_trades = len(filtered_df)
    winning_trades = (filtered_df['realizedPnl'] > 0).sum()
    return (total_trades, winning_trades)


#changes

async def calculate_buy_sell(filtered_df):
    try:
        # Drop duplicates based on relevant columns (e.g., 'orderId' and 'coin')
        unique_orders = filtered_df.drop_duplicates(subset=['orderId', 'symbol'])
        
        # Filter rows where 'realizedPnl' is 0
        openposition_pnl = unique_orders[unique_orders['realizedPnl'] == 0]['side']
        
        if openposition_pnl.empty:
            return {'BUY Percentage': 0.0, 'SELL Percentage': 0.0, 'BUY': 0, 'SELL': 0}
        
        # Count the occurrences of 'BUY' and 'SELL'
        total_count_buy = (openposition_pnl == 'BUY').sum()
        total_count_sell = (openposition_pnl == 'SELL').sum()
        
        total_positions = len(openposition_pnl)
        
        perc_buy = (total_count_buy / total_positions) * 100
        perc_sell = (total_count_sell / total_positions) * 100
        
        result = {
            'BUY/LONG Percentage': round(float(perc_buy), 2),  # Convert to float and round to 2 decimal places
            'SELL/SHORT Percentage': round(float(perc_sell), 2),  # Convert to float and round to 2 decimal places
            'BUY/LONG': int(total_count_buy),  # Convert to integer
            'SELL/SHORT': int(total_count_sell)  # Convert to integer
        }
        
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

        
async def calculate_max_draw(filtered_df, mirror_account):
    try:
        metrics = await asyncio.to_thread(account_metrics, mirror_account)

        total_return, total_unrealized_pnl, total_balance, margin_total = metrics

        maxdd_list = {}
        win_list = {}

        filtered_df_copy = filtered_df.copy()
        filtered_df_copy['win'] = np.where(filtered_df_copy['realizedPnl'] > 0, 1, 0)
        filtered_df_copy['winrate'] = filtered_df_copy['win'].expanding(1).mean()
        win_list['total'] = filtered_df_copy['winrate']

        sf = filtered_df_copy.groupby('date')['realizedPnl'].sum().to_frame(name='PnL')
        sf['win'] = np.where(sf['PnL'] > 0, 1, 0)
        sf['winrate'] = sf['win'].expanding(1).mean()
        sf['running_bal'] = sf['PnL'].cumsum() + total_balance
        sf['peaks'] = sf['running_bal'].cummax()
        sf['drawdown'] = (sf['running_bal'] - sf['peaks']) / sf['peaks']
        maxdd_list['total'] = sf

        mdd = maxdd_list['total']['drawdown'].min()
        return round(mdd, 6) if not np.isnan(mdd) else 0.0

    except Exception as e:
        print(f"Error in calculate_max_draw: {e}")
        return 0.0

calculation_functions = {
    'total_realized_pnl': calculate_total_realized_pnl,
    'calculate_total_fees': calculate_total_fees,
    'calculate_trading_days': calculate_trading_days,
    'winning_days': calculate_winning_days,
    'losing_days': calculate_losing_days,
    'total_winning_trades': calculate_total_winning_trades,
    'max_draw': calculate_max_draw,
    'total_net_profit_loss': total_net_profit_loss,
    'breakeven_days': breakeven_days,
    'average_profit': average_profit,
    'average_loss': average_loss,
    'profit_loss_ratio': profit_loss_ratio,
    'calculate_buy_sell': calculate_buy_sell
}

# # Example usage:
# calculation_types = ['total_realized_pnl', 'calculate_total_fees', 'calculate_trading_days', 'winning_days', 'losing_days', 'total_winning_trades','max_draw']
# results = compute_data(cached_data, '2024-01-01', '2024-04-01', mirror_account, calculation_types)
calculation_types = ['total_realized_pnl', 'calculate_total_fees', 'calculate_trading_days', 'winning_days', 'total_winning_trades', 'max_draw','total_loss_realized_pnl', 'total_net_profit_loss', 'losing_days','breakeven_days', 'average_profit', 'average_loss', 'profit_loss_ratio', 'calculate_buy_sell']

    



#FROM AUTOMATION REPORT CODE
async def computation2(api_data, account_name, start_date):
    account_name = account_name.upper() if account_name is not None else None

    # print("computation2", account_name)
    # Account selection
    metrics = account_metrics(account_name)

    total_return, total_unrealized_pnl, total_balance, margin_total = metrics

    # global api_data
    
    # Fetching and processing data
    df = pd.DataFrame(api_data)
    # print(df)
    df = df[['mirrorx_account', 'date', 'symbol', 'orderId', 'realizedPnl', 'commission']]  # Added 'mirrorx_account' to select mirror account name
    
    # Grouping by 'mirrorx_account' before dropping duplicates
    grouped_df = df.groupby('mirrorx_account')
    
    processed_dfs = []  # List to store processed dataframes for each account
    for mirror_account, mirror_group in grouped_df:
        mirror_group = mirror_group.drop_duplicates(subset=['orderId'])
        mirror_group.loc[:, 'date'] = pd.to_datetime(mirror_group['date'])
        mirror_group.loc[:, 'date'] = mirror_group['date'].dt.strftime('%Y-%m-%d %H:00:00')
        mirror_group = mirror_group[mirror_group['date'] >= start_date]
        mirror_group = mirror_group.drop_duplicates(subset=['date', 'symbol'])
        mirror_group['realizedPnl'] = mirror_group['realizedPnl'].astype(float)
        mirror_group['commission'] = mirror_group['commission'].astype(float)
        mirror_group['adjustedpnl'] = mirror_group['realizedPnl'] - mirror_group['commission']
        mirror_group = mirror_group[mirror_group['realizedPnl'] != 0]
        mirror_group['win/lose'] = mirror_group['realizedPnl'].apply(lambda x: 1 if x > 0 else 0)
        mirror_group['adjust_winrate'] = mirror_group['adjustedpnl'].apply(lambda x: 1 if x > 0 else 0)
        processed_dfs.append(mirror_group)
    
    df = pd.concat(processed_dfs)  # Combining processed dataframes
    
    total_trades = df['realizedPnl'].count()
    total_win = df['win/lose'].sum()
    adjusted_total_win = df['adjust_winrate'].sum()
    winrate = round((total_win/total_trades)*100,2)
    adjusted_winrate = round((adjusted_total_win/total_trades)*100,2)


    # Calculating winrate per mirror account
    mirror_winrates = {}  # Dictionary to store winrates for each mirror account
    mirror_total_trades_count = {} # Dictionary to store trades for each mirror account
    mirror_accounts = df['mirrorx_account'].unique()  # List of unique mirror accounts
    for mirror_account in mirror_accounts:
        mirror_df = df[df['mirrorx_account'] == mirror_account]  # Filter DataFrame for each mirror account
        mirror_total_trades = mirror_df['realizedPnl'].count()
        mirror_total_win = mirror_df['win/lose'].sum()
        mirror_winrate = round((mirror_total_win / mirror_total_trades) * 100, 2)
        mirror_winrates[mirror_account] = mirror_winrate
        mirror_total_trades_count[mirror_account] = mirror_total_trades

    # Sorting the dataframe
    df.sort_values(by=['date', 'symbol'], inplace=True)
    
    
    #FILTER BY BTC
    df_BTC = df[df['symbol'] == 'BTCUSDT'].fillna(0)
    BTC_trades = df_BTC['realizedPnl'].count()
    BTC_win = df_BTC['win/lose'].sum()
    BTC_profit = df_BTC['realizedPnl'].sum()

    if BTC_trades == 0:
        BTC_win = 0
        BTC_winrate = 0
    else:
        BTC_winrate = round((BTC_win / BTC_trades) * 100, 2)

    #FILTER BY BNB
    df_BNB = df[df['symbol'] == 'BNBUSDT'].fillna(0)
    BNB_trades = df_BNB['realizedPnl'].count()
    BNB_win = df_BNB['win/lose'].sum()
    BNB_profit = df_BNB['realizedPnl'].sum()

    if BNB_trades == 0:
        BNB_win = 0
        BNB_winrate = 0
    else:
        BNB_winrate = round((BNB_win / BNB_trades) * 100, 2)

    #FILTER BY ETH
    df_ETH = df[df['symbol'] == 'ETHUSDT'].fillna(0)
    ETH_trades = df_ETH['realizedPnl'].count()
    ETH_win = df_ETH['win/lose'].sum()
    ETH_profit = df_ETH['realizedPnl'].sum()

    if ETH_trades == 0:
        ETH_win = 0
        ETH_winrate = 0
    else:
        ETH_winrate = round((ETH_win / ETH_trades) * 100, 2)

    #FILTER BY DOT
    df_DOT = df[df['symbol'] == 'DOTUSDT'].fillna(0)
    DOT_trades = df_DOT['realizedPnl'].count()
    DOT_win = df_DOT['win/lose'].sum()
    DOT_profit = df_DOT['realizedPnl'].sum()

    if DOT_trades == 0:
        DOT_win = 0
        DOT_winrate = 0
    else:
        DOT_winrate = round((DOT_win / DOT_trades) * 100, 2)

    #FILTER BY XRP
    df_XRP = df[df['symbol'] == 'XRPUSDT'].fillna(0)
    XRP_trades = df_XRP['realizedPnl'].count()
    XRP_win = df_XRP['win/lose'].sum()
    XRP_profit = df_XRP['realizedPnl'].sum()

    if XRP_trades == 0:
        XRP_win = 0
        XRP_winrate = 0
    else:
        XRP_winrate = round((XRP_win / XRP_trades) * 100, 2)

    #FILTER BY SOL
    df_SOL = df[df['symbol'] == 'SOLUSDT'].fillna(0)
    SOL_trades = df_SOL['realizedPnl'].count()
    SOL_win = df_SOL['win/lose'].sum()
    SOL_profit = df_SOL['realizedPnl'].sum()

    if SOL_trades == 0:
        SOL_win = 0
        SOL_winrate = 0
    else:
        SOL_winrate = round((SOL_win / SOL_trades) * 100, 2)

    #FILTER BY MATIC
    df_MATIC = df[df['symbol'] == 'MATICUSDT'].fillna(0)
    MATIC_trades = df_MATIC['realizedPnl'].count()
    MATIC_win = df_MATIC['win/lose'].sum()
    MATIC_profit = df_MATIC['realizedPnl'].sum()

    if MATIC_trades == 0:
        MATIC_win = 0
        MATIC_winrate = 0
    else:
        MATIC_winrate = round((MATIC_win / MATIC_trades) * 100, 2)

    #FILTER BY AVAX
    df_AVAX = df[df['symbol'] == 'AVAXUSDT'].fillna(0)
    AVAX_trades = df_AVAX['realizedPnl'].count()
    AVAX_win = df_AVAX['win/lose'].sum()
    AVAX_profit = df_AVAX['realizedPnl'].sum()

    if AVAX_trades == 0:
        AVAX_win = 0
        AVAX_winrate = 0
    else:
        AVAX_winrate = round((AVAX_win / AVAX_trades) * 100, 2)

    #FILTER BY LINK
    df_LINK = df[df['symbol'] == 'LINKUSDT'].fillna(0)
    LINK_trades = df_LINK['realizedPnl'].count()
    LINK_win = df_LINK['win/lose'].sum()
    LINK_profit = df_LINK['realizedPnl'].sum()

    if LINK_trades == 0:
        LINK_win = 0
        LINK_winrate = 0
    else:
        LINK_winrate = round((LINK_win / LINK_trades) * 100, 2)

    #FILTER BY ADA
    df_ADA = df[df['symbol'] == 'ADAUSDT'].fillna(0)
    ADA_trades = df_ADA['realizedPnl'].count()
    ADA_win = df_ADA['win/lose'].sum()
    ADA_profit = df_ADA['realizedPnl'].sum()

    if ADA_trades == 0:
        ADA_win = 0
        ADA_winrate = 0
    else:
        ADA_winrate = round((ADA_win / ADA_trades) * 100, 2)

    #FILTER BY ATOM
    df_ATOM = df[df['symbol'] == 'ATOMUSDT'].fillna(0)
    ATOM_trades = df_ATOM['realizedPnl'].count()
    ATOM_win = df_ATOM['win/lose'].sum()
    ATOM_profit = df_ATOM['realizedPnl'].sum()

    if ATOM_trades == 0:
        ATOM_win = 0
        ATOM_winrate = 0
    else:
        ATOM_winrate = round((ATOM_win / ATOM_trades) * 100, 2)

    #FILTER BY LTC
    df_LTC = df[df['symbol'] == 'LTCUSDT'].fillna(0)
    LTC_trades = df_LTC['realizedPnl'].count()
    LTC_win = df_LTC['win/lose'].sum()
    LTC_profit = df_LTC['realizedPnl'].sum()

    if LTC_trades == 0:
        LTC_win = 0
        LTC_winrate = 0
    else:
        LTC_winrate = round((LTC_win / LTC_trades) * 100, 2)

    #FILTER BY UNI
    df_UNI = df[df['symbol'] == 'UNIUSDT'].fillna(0)
    UNI_trades = df_UNI['realizedPnl'].count()
    UNI_win = df_UNI['win/lose'].sum()
    UNI_profit = df_UNI['realizedPnl'].sum()

    if UNI_trades == 0:
        UNI_win = 0
        UNI_winrate = 0
    else:
        UNI_winrate = round((UNI_win / UNI_trades) * 100, 2)

    overall = {
        'total_trades': total_trades,
        'return_percentage': np.nan_to_num(total_return, nan=0),
        'total_unrealized_pnl': np.nan_to_num(total_unrealized_pnl, nan=0),
        'overall_winrate': np.nan_to_num(winrate, nan=0),
        'adjusted_winrate': np.nan_to_num(adjusted_winrate, nan=0),
        'total_balance': np.nan_to_num(total_balance, nan=0),
        'margin_total': np.nan_to_num(margin_total, nan=0),
    }

    trades = {
        'BTC_trades': BTC_trades,
        'BNB_trades': BNB_trades,
        'ETH_trades': ETH_trades,
        'SOL_trades': SOL_trades,
        'XRP_trades': XRP_trades,
        'DOT_trades': DOT_trades,
        'MATIC_trades': MATIC_trades,
        'AVAX_trades': AVAX_trades,
        'LINK_trades': LINK_trades,
        'ADA_trades': ADA_trades,
        'ATOM_trades': ATOM_trades,
        'LTC_trades': LTC_trades,
        'UNI_trades': UNI_trades
    }

    winrates = {
        'BTCUSDT': BTC_winrate,
        'BNBUSDT': BNB_winrate,
        'ETHUSDT': ETH_winrate,
        'SOLUSDT': SOL_winrate,
        'XRPUSDT': XRP_winrate,
        'DOTUSDT': DOT_winrate,
        'MATICUSDT': MATIC_winrate,
        'AVAXUSDT': AVAX_winrate,
        'LINKUSDT': LINK_winrate,
        'ADAUSDT': ADA_winrate,
        'ATOMUSDT': ATOM_winrate,
        'LTCUSDT': LTC_winrate,
        'UNIUSDT': UNI_winrate
    }

    profits_by_coin = {
        'BTCUSDT': BTC_profit,
        'BNBUSDT': BNB_profit,
        'ETHUSDT': ETH_profit,
        'SOLUSDT': SOL_profit,
        'XRPUSDT': XRP_profit,
        'DOTUSDT': DOT_profit,
        'MATICUSDT': MATIC_profit,
        'AVAXUSDT': AVAX_profit,
        'LINKUSDT': LINK_profit,
        'ADAUSDT': ADA_profit,
        'ATOMUSDT': ATOM_profit,
        'LTCUSDT': LTC_profit,
        'UNIUSDT': UNI_profit
    }

    # print({"results": results, "trades": trades, "winrates": winrates})
    
    return {"overall": overall, "trades": trades, "winrate_per_symbol": winrates, "mirror_winrates": mirror_winrates, "profits_by_coin": profits_by_coin, "mirror_total_trades_count": mirror_total_trades_count}
    











calculation_types = ['total_realized_pnl', 'calculate_total_fees', 'calculate_trading_days', 'winning_days', 'total_winning_trades', 'max_draw','total_loss_realized_pnl', 'total_net_profit_loss', 'losing_days','breakeven_days', 'average_profit', 'average_loss', 'profit_loss_ratio', 'calculate_buy_sell']

# USAGE

start_date = input("PLEASE INPUT START_DATE (e.g., 2024-02-25): ") or "2024-07-01"
end_date = input("PLEASE INPUT END_DATE (e.g., 2024-03-25): ") or "2024-08-01"
symbols = input("Input Symbols: ") or None
mirror_account = input("PLEASE INPUT account: ") or None

print(mirror_account)


# async def main():
#     cached_data = await fetch_get_data()
#     result = await data_computations(cached_data, start_date, end_date, mirror_account, calculation_types, symbols)
#     # print(cached_data)

#     return result
# result = asyncio.run(main())
# print(result)



# # TO VIEW THE RAW DATA GO TO URL: http://localhost:8000/api/get_all_data PLEASE USE FIREFOX TO VIEW JSONFORMAT BUT FIRST IS RUN THE MANAGE.PY
async def value():


    cached_data = await fetch_get_data()
    # Create tasks for concurrent execution
    if cached_data is None:
        raise ValueError("Cached data is not available.")
    result = await data_computations(cached_data, start_date, end_date, mirror_account, calculation_types, symbols)
    profit_dollar = await asyncio.to_thread(print_profits, clients, initial_balance, mirror_account)

    # task2 = asyncio.create_task(computation2(mirror_account, start_date))
    # result = await task2
    # print(result)

    overall_account = result.get("overall")
    #total trades
    trades_account = result.get("trades")
    symbols_per_account_data = result.get("winrate_per_symbol")


    if result is None or not all(calc_type in result for calc_type in calculation_types):
        raise ValueError("Calculation types are not available or incomplete.")
    
    # winning rate for mirroraccounts
    winning_rate_per_account_dict = result.get('mirror_winrates')

    response_data = {
        'total_realized_pnl': profit_dollar,
        'trading_days': int(result.get('calculate_trading_days')),
        'winning_days': int(result.get('winning_days')),
        'total_fees': result.get('calculate_total_fees'),
        'max_draw': result.get('max_draw'),
    }

    # Convert NumPy int64 values in overall_account
    overall_account = {
        'total_trades': int(result.get("overall").get('total_trades')),
        'return_percentage': result.get("overall").get('return_percentage'),
        'total_unrealized_pnl': result.get("overall").get('total_unrealized_pnl'),
        'overall_winrate': result.get("overall").get('overall_winrate'),
        'adjusted_winrate': result.get("overall").get('adjusted_winrate'),
        'total_balance': result.get("overall").get('total_balance'),
        'margin_total': result.get("overall").get('margin_total'),
    }

    # Convert NumPy int64 values in trades_account
    trades_account = {k: int(v) for k, v in result.get("trades").items()}

    data_to_return = {"response_data": response_data, "winning_rate_acc": winning_rate_per_account_dict, "symbols_winrate": symbols_per_account_data, "overall": overall_account, "trades_account": trades_account}
    cache["/api/get_computation_load"] = data_to_return

    output_string = ""
    for key, value in data_to_return.items():
        output_string += f"{key}:\n"
        for sub_key, sub_value in value.items():
            output_string += f" {sub_key}: {sub_value}\n"

    print(output_string)
    json_data = json.dumps(data_to_return)

    # print(json_data)
    return json_data

asyncio.run(value())



