import pandas as pd
import numpy as np
import asyncio
from datetime import datetime
from cache_manager import *
# from binance_api_secretkey import *
import json
import os
import concurrent.futures
from binance.client import Client
import time
from datetime import datetime, timedelta
# Initial balance for each account

# Initial balance for each account
# Initial balance for each account
# initial_balance = {"your_account" : 129308, "your_account":129308, "your_account" :129308, "your_account" : 129308, "your_account": 129308, "your_account" : 115815}


# List of accounts
accounts = [
    "your_account",
    "your_account",
    "your_account",
    "your_account",
    "your_account",
    "your_account",
    "your_account"
]

# symbols = [
#     'BNBUSDT',
#     'ATOMUSDT',
#     'ADAUSDT',
#     'XRPUSDT',
#     'SOLUSDT',
#     'DOTUSDT',
#     'BNBUSDT',
#     'UNIUSDT',
# ]

# Dictionary to store the client instances for each account
# clients = {}
# for acc in accounts:
#     secret = os.environ.get(f"{acc}_secret")
#     key = os.environ.get(f"{acc}_key")
#     if secret and key:
#         client = Client(key, secret)
#         clients[acc] = client


# Function to get the total wallet balance for a Binance client

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
    


async def all_metrics_json_data(start_date, end_date):
    if not await validate_dates(start_date, end_date):
        return None
    
    try:
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        latest_entry = None
        latest_timestamp = datetime.min  # Initialize with the earliest possible timestamp
        
        file_path = r'C:\Users\User\Documents\financialDashboard_AUG\financialDashboard\dashboard\computation_data_app\account_metrics.json'
        
        # Print the current working directory
        print(f"Current working directory: {os.getcwd()}")
        
        with open(file_path, 'r') as file:
            data = json.load(file)
            for entry in data:
                timestamp_str = entry['timestamp']
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                
                # Check if the entry's timestamp is within the specified range
                if start_date_dt <= timestamp.date() <= end_date_dt:
                    # Check if this entry's timestamp is more recent than the current latest
                    if timestamp > latest_timestamp:
                        latest_timestamp = timestamp
                        latest_entry = entry
            
            if latest_entry is None:
                # If no valid entry found in the specified range, return None or an empty dictionary
                return None
            
            # Initialize aggregated data dictionaries
            total_unrealized_pnl_data = {}
            total_return_data = {}
            total_balance_data = {}
            margin_total_data = {}
            profit_dollar_data = {}
            
            metrics = latest_entry['metrics']
            
            # Aggregate total_unrealized_pnl_data
            for account, value in metrics.get('total_unrealized_pnl_data', {}).items():
                total_unrealized_pnl_data[account] = float(value or 0)
            
            # Aggregate total_return_data
            for account, value in metrics.get('total_return_data', {}).items():
                total_return_data[account] = float(value or 0)
            
            # Aggregate total_balance_data
            for account, value in metrics.get('total_balance_data', {}).items():
                total_balance_data[account] = float(value or 0)
            
            # Aggregate margin_total_data
            for account, value in metrics.get('margin_total_data', {}).items():
                margin_total_data[account] = float(value or 0)
            
            # Aggregate profit_dollar_data
            for account, value in metrics.get('profit_dollar_data', {}).items():
                profit_dollar_data[account] = float(value or 0)
            
            return {
                'total_unrealized_pnl_data': total_unrealized_pnl_data,
                'total_return_data': total_return_data,
                'total_balance_data': total_balance_data,
                'margin_total_data': margin_total_data,
                'profit_dollar_data': profit_dollar_data
            }

    except Exception as e:
        print(f"Error in all_metrics_json_data: {e}")
        return None
    

async def metrics_json_data(start_date, end_date, accounts):
    if not await validate_dates(start_date, end_date):
        return None
    
    if accounts is None:
        accounts = 'MIRRORXTOTAL'
    elif isinstance(accounts, list):
        accounts = [acc.upper() for acc in accounts]
    else:
        accounts = accounts.upper()
        
    try:
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        latest_entry = None
        latest_timestamp = datetime.min
        
        file_path = r'C:\Users\User\Documents\financialDashboard_AUG\financialDashboard\dashboard\computation_data_app\account_metrics.json'
        
        # Print the current working directory
        print(f"Current working directory: {os.getcwd()}")
        
        with open(file_path, 'r') as file:
            data = json.load(file)
            has_data = False
            
            for entry in data:
                timestamp_str = entry['timestamp']
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                
                if start_date_dt <= timestamp.date() <= end_date_dt:
                    if timestamp > latest_timestamp:
                        latest_timestamp = timestamp
                        latest_entry = entry
                        has_data = True
            
            if not has_data:
                return [{
                    'timestamp': f"{start_date} to {end_date}",
                    'total_unrealized_pnl': 0.0,
                    'total_return': 0.0,
                    'total_balance': 0.0,
                    'margin_total': 0.0,
                    'profit_dollar_data': 0.0
                }]
            
            metrics = latest_entry['metrics']
            
            total_unrealized_pnl = metrics.get('total_unrealized_pnl_data', {})
            total_return = metrics.get('total_return_data', {})
            total_balance = metrics.get('total_balance_data', {})
            margin_total = metrics.get('margin_total_data', {})
            profit_dollar_data = metrics.get('profit_dollar_data', {})
            
            # Convert values to float if they exist
            total_unrealized_pnl = {k: float(v) for k, v in total_unrealized_pnl.items()}
            total_return = {k: float(v) for k, v in total_return.items()}
            
            if accounts == 'MIRRORXTOTAL':
                filtered_total_unrealized_pnl = float(total_unrealized_pnl.get('MIRRORXTOTAL', 0))
                filtered_total_return = float(total_return.get('MIRRORXTOTAL', 0))
                total_balance = float(total_balance.get('MIRRORXTOTAL', 0))
                margin_total = float(margin_total.get('MIRRORXTOTAL', 0))
                profit_dollar_data = float(profit_dollar_data.get('MIRRORXTOTAL', 0))
            elif isinstance(accounts, list):
                filtered_total_unrealized_pnl = {k: float(v) for k, v in total_unrealized_pnl.items() if k in accounts}
                filtered_total_return = {k: float(v) for k, v in total_return.items() if k in accounts}
                total_balance = sum(float(total_balance.get(acc, 0)) for acc in accounts)
                margin_total = sum(float(margin_total.get(acc, 0)) for acc in accounts)
                profit_dollar_data = sum(float(profit_dollar_data.get(acc, 0)) for acc in accounts)
            else:
                filtered_total_unrealized_pnl = float(total_unrealized_pnl.get(accounts, 0))
                filtered_total_return = float(total_return.get(accounts, 0))
                total_balance = float(total_balance.get(accounts, 0))
                margin_total = float(margin_total.get(accounts, 0))
                profit_dollar_data = float(profit_dollar_data.get(accounts, 0))
            
            return [{
                'timestamp': latest_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'total_unrealized_pnl': filtered_total_unrealized_pnl,
                'total_return': filtered_total_return,
                'total_balance': total_balance,
                'margin_total': margin_total,
                'profit_dollar_data': profit_dollar_data
            }]

    except Exception as e:
        print(f"Error in metrics_json_data: {e}")
        return None





async def data_computations(cached_data, start_date, end_date, mirror_accounts, calculation_types, symbols):
    if not await validate_dates(start_date, end_date):
        return None

    try:
        # Fetch data based on mirror accounts
        if mirror_accounts:
            # Handle case where mirror_accounts is not None and not empty
            filtered_data_list = []
            for account in mirror_accounts:
                data = await metrics_json_data(start_date, end_date, account)
                if data:
                    filtered_data_list.extend(data)
        else:
            # Handle case where mirror_accounts is None or empty
            filtered_data_list = await metrics_json_data(start_date, end_date, None)

        if not filtered_data_list:
            return None

        # Filter cached data based on mirror accounts if provided
        if mirror_accounts:
            api_data = [entry for entry in cached_data if entry.get('mirrorx_account') in mirror_accounts]
        else:
            api_data = cached_data

        # Filter data based on symbols
        if symbols:
            api_data = [entry for entry in api_data if entry.get('symbol') in symbols]
        else:
            symbols = set(entry['symbol'] for entry in cached_data)
            api_data = [entry for entry in api_data if entry.get('symbol') in symbols]

        df = pd.DataFrame(api_data)
        # df.to_csv(r"C:\Users\User\Documents\jonathan-dashboard\PINAKA_LATEST\financialDashboard\storage\data.csv", index=False)
        df['date'] = pd.to_datetime(df['date']).dt.date

        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        filtered_df = df[(df['date'] >= start_date_dt) & (df['date'] <= end_date_dt)]

        results = {}

        async def run_calculation(calculation_type):
            if calculation_type in calculation_functions:
                if calculation_type == 'max_draw':
                    return calculation_type, await calculate_max_draw(filtered_data_list, filtered_df, mirror_accounts, start_date, end_date)
                elif calculation_type == 'calculate_total_fees':
                    return calculation_type, await calculate_total_fees(filtered_df, start_date, end_date)
                elif calculation_type == 'fetch_csv_calculate_total_realized_pnl':
                    return calculation_type, await fetch_csv_calculate_total_realized_pnl(filtered_data_list)
                else:
                    return calculation_type, await calculation_functions[calculation_type](filtered_df)
            return calculation_type, None

        tasks = [run_calculation(calculation_type) for calculation_type in calculation_types]
        calculation_results = await asyncio.gather(*tasks)

        for calculation_type, result in calculation_results:
            results[calculation_type] = result

        computation_results = await computation2(filtered_data_list, api_data, mirror_accounts, start_date, end_date)
        results.update(computation_results)

        return results
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    




async def calculate_total_realized_pnl(filtered_df):
    return float(filtered_df['realizedPnl'].sum())



async def fetch_csv_calculate_total_realized_pnl(filtered_data_list):

    for filtered_data in filtered_data_list:
        profit_dollar_data = filtered_data['profit_dollar_data']

    return profit_dollar_data
    # else:
        # return 0.0  # or some default value if filtered_data_list is empty
    
async def fetch_and_save_historical_klines(filename):
    end_str = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    start_str = (datetime.utcnow() - timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
    interval = Client.KLINE_INTERVAL_4HOUR
    symbol = 'BNBUSDT'

    client = Client (api_key= None, api_secret= None)
    klines = await asyncio.to_thread(client.get_historical_klines, symbol, interval, start_str, end_str)

    klines_data = [[row[0], row[6], row[4]] for row in klines]  # open_time, close_time, close

    df_klines = pd.DataFrame(klines_data, columns=['open_time', 'close_time', 'close'])

    df_klines['open_time'] = pd.to_datetime(df_klines['open_time'], unit='ms')
    df_klines['close_time'] = pd.to_datetime(df_klines['close_time'], unit='ms')
    df_klines['close'] = df_klines['close'].astype(float)

    df_klines.to_csv(filename, index=False)

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

async def calculate_buy_sell(filtered_df):
    try:
        openposition_pnl = filtered_df[filtered_df['realizedPnl'] == 0]['side']
        
        if openposition_pnl.empty:
            return {'BUY Percentage': 0.0, 'SELL Percentage': 0.0, 'BUY': 0, 'SELL': 0}

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

async def calculate_max_draw(filtered_data_list, filtered_df, accounts, start_date, end_date):
    try:
        # filtered_data_list  = await metrics_json_data(start_date, end_date, accounts)
        if filtered_data_list:
            maxdd_list = {}
            win_list = {}

            for filtered_data in filtered_data_list:
                total_return = filtered_data['total_return']
                total_unrealized_pnl = filtered_data['total_unrealized_pnl']
                total_balance = filtered_data['total_balance']
                margin_total = filtered_data['margin_total']
            
            filtered_df_copy = filtered_df.copy()
            filtered_df_copy['win'] = np.where(filtered_df_copy['realizedPnl'] > 0, 1, 0)
            filtered_df_copy['winrate'] = filtered_df_copy['win'].expanding(1).mean()
            win_list['total'] = filtered_df_copy['winrate']

            sf = filtered_df_copy.groupby('date')['realizedPnl'].sum().to_frame(name='PnL')
            sf['win'] = np.where(sf['PnL'] > 0, 1, 0)
            sf['winrate'] = sf['win'].expanding(1).mean()
            sf['running_bal'] = sf['PnL'].cumsum() + float(total_balance)
            sf['peaks'] = sf['running_bal'].cummax()
            sf['drawdown'] = (sf['running_bal'] - sf['peaks']) / sf['peaks']
            maxdd_list['total'] = sf

            mdd = maxdd_list['total']['drawdown'].min()
            return round(mdd, 6) if not np.isnan(mdd) else 0.0
        else:
            return 0.0

    except Exception as e:
        print(f"Error in calculate_max_draw: {e}")
        return 0.0

calculation_functions = {
    'fetch_csv_calculate_total_realized_pnl' : fetch_csv_calculate_total_realized_pnl,
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

# Example usage:
# calculation_types = ['total_realized_pnl', 'calculate_total_fees', 'calculate_trading_days', 'winning_days', 'losing_days', 'total_winning_trades','max_draw']
# results = compute_data(cached_data, '2024-01-01', '2024-04-01', mirror_account, calculation_types)
calculation_types = ['fetch_csv_calculate_total_realized_pnl','total_realized_pnl', 'calculate_total_fees', 'calculate_trading_days', 'winning_days', 'total_winning_trades', 
'max_draw','total_loss_realized_pnl', 'total_net_profit_loss', 'losing_days','breakeven_days', 'average_profit', 'average_loss', 'profit_loss_ratio', 'calculate_buy_sell']


#FROM AUTOMATION REPORT CODE
async def computation2(filtered_data_list, api_data, account_name, start_date, end_date):
    account_name = account_name.upper() if account_name is not None else None

    # print("computation2", account_name)
    # Account selection

    

    for filtered_data in filtered_data_list:
        total_return = filtered_data['total_return']
        total_unrealized_pnl = filtered_data['total_unrealized_pnl']
        total_balance = filtered_data['total_balance']
        margin_total = filtered_data['margin_total']

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
    











# calculation_types = ['total_realized_pnl', 'calculate_total_fees', 'calculate_trading_days', 'winning_days', 'total_winning_trades', 'max_draw','total_loss_realized_pnl', 'total_net_profit_loss', 'losing_days','breakeven_days', 'average_profit', 'average_loss', 'profit_loss_ratio', 'calculate_buy_sell']

# USAGE

start_date = input("PLEASE INPUT START_DATE (e.g., 2024-02-25): ") or "2024-07-01"
end_date = input("PLEASE INPUT END_DATE (e.g., 2024-03-25): ") or "2024-07-20"
symbols = input("Input Symbols: ") or None
mirror_account = input("PLEASE INPUT account: ") or None

# print(mirror_account)


# async def main():
#     cached_data = await fetch_get_data()
#     result = await data_computations(cached_data, start_date, end_date, mirror_account, calculation_types, symbols)
#     # print(cached_data)

#     return result
# result = asyncio.run(main())
# print(result)



# TO VIEW THE RAW DATA GO TO URL: http://localhost:8000/api/get_all_data PLEASE USE FIREFOX TO VIEW JSONFORMAT BUT FIRST IS RUN THE MANAGE.PY
async def value():
    cached_data = await fetch_get_data()

    # Convert the list to a DataFrame
    df = pd.DataFrame(cached_data)

    # Save DataFrame to CSV
    # df.to_csv(r"C:\Users\User\Documents\jonathan-dashboard\PINAKA_LATEST\financialDashboard\storage\cached_data.csv", index=False)

    # Create tasks for concurrent execution
    if cached_data is None:
        raise ValueError("Cached data is not available.")
    result = await data_computations(cached_data, start_date, end_date, mirror_account, calculation_types, symbols)

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
        'total_realized_pnl': result.get('fetch_csv_calculate_total_realized_pnl'),
        'trading_days': int(result.get('calculate_trading_days')),
        'winning_days': int(result.get('winning_days')),
        'total_fees': result.get('calculate_total_fees'),
        'max_draw': result.get('max_draw'),
    }
    account_metrics = await all_metrics_json_data(start_date, end_date)
    # Convert NumPy int64 values in overall_account
    overall_account = {
        'total_trades': int(result.get("overall").get('total_trades')),
        'return_percentage': result.get("overall").get('return_percentage'),
        'total_unrealized_pnl': result.get("overall").get('total_unrealized_pnl'),
        'overall_winrate': result.get("overall").get('overall_winrate'),
        'metrics_data': account_metrics,
        'adjusted_winrate': result.get("overall").get('adjusted_winrate'),
        'total_balance': result.get("overall").get('total_balance'),
        'margin_total': result.get("overall").get('margin_total'),
    }

    # print('\n\n', account_metrics)

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



