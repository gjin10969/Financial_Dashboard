# import pandas as pd
# import os
# import time
# from binance.client import Client
# from datetime import datetime, timedelta
# import numpy as np
# import sys

# starting_date = '2024-08-01 00:00:00'
# ending_date = '2024-09-01 00:00:05'

# your_account_key = os.environ.get('your_account_key')
# your_account_secret = os.environ.get('your_account_secret')

# your_account_key = os.environ.get('your_account_key')
# your_account_secret = os.environ.get('your_account_secret')

# your_account_key = os.environ.get('your_account_key')
# your_account_secret = os.environ.get('your_account_secret')

# your_account_key = os.environ.get('your_account_key')
# your_account_secret = os.environ.get('your_account_secret')

# your_account_key = os.environ.get('your_account_key')
# your_account_secret = os.environ.get('your_account_secret')

# your_account_key = os.environ.get('your_account_key')
# your_account_secret = os.environ.get('your_account_secret')

# # client_your_account = Client(your_account_key, your_account_secret)
# client_your_account = Client(your_account_key, your_account_secret)
# # client_your_account = Client(your_account_key, your_account_secret)
# # client_your_account = Client(your_account_key, your_account_secret)
# # client_your_account = Client(your_account_key, your_account_secret)
# client_your_account = Client(your_account_key, your_account_secret)

# """acct_number: acc_name, acc_client, acc_init_balance"""
# accounts_dict = {
#     0: ["your_account", client_your_account, 104513.7171],
#     1: ["your_account", client_your_account, 12000],
#     }

# account_valid = False
# while account_valid != True:
#     try:
#         user_input = int(input(
#             """ 
            
#             0: FUND
#             1: your_account
#             Select account: """))
#         account_valid = True
#         account_number = user_input
#         account_name = accounts_dict[account_number][0]
#         account_client = accounts_dict[account_number][1]
#         account_init_balance = accounts_dict[account_number][2]
#     except ValueError:
#         print("Invalid account!")
#     except KeyError:
#         print(f"No account on index {user_input}.")
#         account_valid = False
#     except KeyboardInterrupt:
#         sys.exit()

# if account_number == 0:
#     #----------------------------------------------------------------
#     def list_to_dataframe(data_list):
#         df = pd.DataFrame(data_list)
#         df['date'] = df['time']
#         df['date'] = pd.to_datetime(df['date'], unit='ms')
#         df = df.set_index('date')
#         df.index = pd.to_datetime(df.index, unit='ms')
#         return df

#     def df_read_csv(file_name):
#         df_csv = pd.read_csv(file_name, header=0)
#         df_csv = list_to_dataframe(df_csv)

#         return df_csv

#     def run_history_V2(client, file_name, end = str(round(time.time()*1000))):
#         start = 0
#         while int(start) < int(end):
#             old_trades = df_read_csv(file_name)
#             if old_trades.empty:
#                 print('Empty File uploaded')
#                 first_update = 0
#                 last_update = 0
#                 break
#             else:
#                 if int(start) == 0:
#                     first_update = old_trades.iloc[-1,-4]
                    
#                 start = int(old_trades.iloc[-1,-4]) + 1
#                 new_trades = client.futures_account_trades(startTime = int(start))
#                 if new_trades == []:
#                     last_update = old_trades.iloc[-1,-4]
#                     break
#                 else:
#                     new_trades = list_to_dataframe(new_trades)
#                     trades_file = pd.concat([old_trades, new_trades], axis=0)
#                     last_update = trades_file.iloc[-1,-4]
                    
#                     trades_file.to_csv(file_name, mode='w', index = True, header=True)
#         print(f'\nUpdated : {file_name}') 
#         print(f'Last trade before : {datetime.fromtimestamp(first_update/1000.0)}')
#         print(f'Last trade after : {datetime.fromtimestamp(last_update/1000.0)}')

#     def update_csv(account_name, account_client):
#         acc_file = access_trades_live(account_name)
#         files=acc_file
#         clients=account_client
#         on = time.time()
#         run_history_V2(clients, files)
#         end = time.time()
#         print('\nTime function : ',end - on)

#     def access_trades_live(acc_name):
#         path = os.getcwd()
#         filename_trades = f"{acc_name}_4H_continuing_trades.csv"
#         live_trades_folder = os.path.join(path  , 'live_trades')
#         filepath_trades = os.path.join(live_trades_folder, filename_trades)
#         print(filepath_trades)
#         return filepath_trades
#     live_trades_file = access_trades_live(account_name)
#     acc_csv = [live_trades_file]
#     update_csv(account_name, account_client)
#     time.sleep(5)
#     #----------------------------------------------------------------
#     data = pd.read_csv(f"live_trades/{account_name}_4H_continuing_trades.csv")
#     df = pd.DataFrame(data)
#     df2 = df.groupby('orderId').agg({
#         'date':'first',
#         'symbol': 'first',
#         'realizedPnl': 'sum',
#         'commission': 'sum',
#         'qty': 'sum',
#         'price': 'mean',
#         'side': 'first',
#         'positionSide': 'first'
#         }).reset_index()
#     df2 = df2[df2['realizedPnl'] != 0]
#     df2 = df2.sort_values(by="date").reset_index(drop=True)

#     #----------------------------------------------------------------
#     df2 = df2[df2.date >= starting_date]
#     df2 = df2[df2.date <= ending_date]
#     df2.reset_index(drop=True, inplace=True)
#     #----------------------------------------------------------------

#     df3 = pd.DataFrame()
#     df3["date"] = ""
#     df3["orderId_1"] = ""
#     df3["orderId_2"] = ""
#     df3["symbol_1"] = ""
#     df3["symbol_2"] = ""
#     df3["realizedPnl_1"] = ""
#     df3["realizedPnl_2"] = ""
#     df3["total_Pnl"] = ""
#     df3["qty_1"] = ""
#     df3["qty_2"] = ""
#     df3["price_1"] = ""
#     df3["price_2"] = ""
#     # df3["marketPrice_1"] = ""
#     # df3["marketPrice_2"] = ""
#     df3["side_1"] = ""
#     df3["side_2"] = ""
#     df3["positionSide_1"] = ""
#     df3["positionSide_2"] = ""
#     df3

#     for index, row in df2.iterrows():
#         if index%2 != 1:
#             date_temp1 = pd.to_datetime(row.date)
#             date_temp2 = date_temp1 + timedelta(minutes=1)
#             # print(date_temp1, date_temp2)
#             date = row.date
#             symbol_1 = row.symbol
#             realizedPnl_1 = row.realizedPnl
#             orderId_1 = row.orderId
#             qty_1 = row.qty
#             price_1 = row.price
#             # marketPrice_1 = (client_your_account.get_historical_klines(symbol_1, client_your_account.KLINE_INTERVAL_1MINUTE, str(date_temp1), str(date_temp2)))[0][1]
#             # time.sleep(1)
#             marketPrice_1 = row.price
#             side_1 = row.side
#             positionSide_1 = row.positionSide

#         else:
#             date2_temp1 = pd.to_datetime(row.date)
#             date2_temp2 = date2_temp1 + timedelta(minutes=1)
#             date2 = row.date
#             symbol_2 = row.symbol
#             realizedPnl_2 = row.realizedPnl
#             orderId_2 = row.orderId
#             qty_2 = row.qty
#             price_2 = row.price
#             # marketPrice_2 = (client_your_account.get_historical_klines(symbol_2, client_your_account.KLINE_INTERVAL_1MINUTE, str(date2_temp1), str(date2_temp2)))[0][1]
#             # time.sleep(1)
#             marketPrice_2 = row.price
#             side_2 = row.side
#             positionSide_2 = row.positionSide

#             temp_df = pd.DataFrame([{
#                 "date": date,
#                 "symbol_1": symbol_1,
#                 "symbol_2": symbol_2,
#                 'realizedPnl_1': realizedPnl_1,
#                 'realizedPnl_2': realizedPnl_2,
#                 'total_Pnl': realizedPnl_1 + realizedPnl_2,
#                 "orderId_1": orderId_1,
#                 "orderId_2": orderId_2,
#                 "qty_1": qty_1,
#                 "qty_2": qty_2,
#                 "price_1": price_1,
#                 "price_2": price_2,
#                 # "marketPrice_1": marketPrice_1,
#                 # "marketPrice_2": marketPrice_2,
#                 "side_1": side_1,
#                 "side_2": side_2,
#                 "positionSide_1": positionSide_1,
#                 "positionSide_2": positionSide_2,

#                 }])
#             df3 = pd.concat([df3, temp_df])
#     df3.reset_index(inplace=True, drop=True)
#     df3.to_csv("fund_tradesheet.csv")

#     #----------------------------------------------------------------
#     def count_position():
#         B_account, acc_name = account_client, account_name
#         position = B_account.futures_position_information()
#         position = pd.DataFrame(position)
#         notional_size = position['positionAmt'].astype(float)
#         count = 0
#         long_count = 0
#         short_count = 0
#         for i in notional_size:
#             if i > 0:
#                 count += 1
#                 long_count += 1
#             elif i < 0:
#                 count += 1
#                 short_count += 1
#         return count, long_count, short_count
#     def tpsl_count():
#         B_account, acc_name = account_client, account_name
#         open_orders = B_account.futures_get_open_orders()
#         open_orders = pd.DataFrame(open_orders)
#         tpsl_count = len(open_orders)
#         return tpsl_count

#     def wallet_balance():
#         B_account, acc_name = account_client, account_name
#         wallet_account = B_account.futures_account()
#         total_balance = float(wallet_account['totalWalletBalance'])
#         unrealizedPnl = float(wallet_account['totalUnrealizedProfit'])
#         # print(unrealizedPnl, total_balance)
#         total_balance = total_balance + unrealizedPnl
#         return float(total_balance), float(unrealizedPnl)

#     total_balance, unrealizedPnl = wallet_balance()
#     tpsl_count = tpsl_count()
#     count, long_count, short_count = count_position()

#     #----------------------------------------------------------------
#     trades_dict = {}
#     overall_trades = 0
#     overall_win_trades = 0

#     for index, row in df3.iterrows():
#         pair = str(row.symbol_1) + "_" + str(row.symbol_2)
#         # print(curr_pair)
#         if pair not in trades_dict:
#             trades_dict[pair] = {"trades": 0, "win_trades": 0, 'realizedPnl': 0}

#     for index, row in df3.iterrows():
#         pair = str(row.symbol_1) + "_" + str(row.symbol_2)
#         try:
#             trades_dict[pair]['trades'] += 1
#             overall_trades += 1
#             if row.total_Pnl > 0:
#                 trades_dict[pair]['win_trades'] += 1
#                 overall_win_trades += 1
#             trades_dict[pair]['realizedPnl'] += row.realizedPnl_1 + row.realizedPnl_2
#         except:
#             print("error")

#     #----------------------------------------------------------------
#     from dateutil import tz
#     time_now = datetime.now(tz.gettz()).strftime("%m/%d/%Y, %H:%M")
#     message_dict = {
#             'Account': account_name,
#             'Date': f"{time_now}",
#             'Overall Trade(s)': len(df3),
#             '% Return': f"{round(((total_balance-account_init_balance)/account_init_balance)*100, 4)}%",
#             'Profit' : f"$ {round(total_balance-account_init_balance, 2)}",
#             'Overall Winrate': f"{round((overall_win_trades/overall_trades)*100,2)}%",
#             'Wallet Balance': f"$ {round(total_balance,2)}",
#             'Current Unrealized PNL': f"$ {round(unrealizedPnl,2)}",
#             'Open position(s)': "{:.0f} \n".format((long_count + short_count)),
#             'Historical PNL': ""
        
#         }

#     for key, value in trades_dict.items():
#         key_index = "".join((key.split("USDT")))
#         message_dict[key_index] =  f"$ {round(value['realizedPnl'], 2)}" 
#     #----------------------------------------------------------------
#     import pywhatkit
#     message = ""
#     for var_name, var_value in message_dict.items():
#         message += f"{var_name}: {var_value}\n"
#     print("\n")
#     print(message)
#     sending = input("Send now (Y/N): ").upper()
#     if sending == "Y":
#         # pywhatkit.sendwhatmsg_instantly("+33767666272",message,20, tab_close=False)
#         pywhatkit.sendwhatmsg_instantly("+639952915505",message,20, tab_close=False)
#         time.sleep(60)
#     else: 
#         pass
#     #----------------------------------------------------------------


# if account_number == 1:
#     df = pd.read_csv("C:\\Users\\User\\Documents\\your_account\\tradesheet.csv")
#     df = df[5:]
#     df_first5rows = pd.read_csv("x2_first_5rows_modified.csv")
#     final_df = pd.concat([df_first5rows,df])
#     final_df["realizedPnl"] = (final_df.qty_0 * (final_df.exit_price_0 - final_df.entry_price_0)) + (final_df.qty_1 * (final_df.exit_price_1 - final_df.entry_price_1))
#     #----------------------------------------------------------------
#     def count_position():
#         B_account, acc_name = account_client, account_name
#         position = B_account.futures_position_information()
#         position = pd.DataFrame(position)
#         notional_size = position['positionAmt'].astype(float)
#         count = 0
#         long_count = 0
#         short_count = 0
#         for i in notional_size:
#             if i > 0:
#                 count += 1
#                 long_count += 1
#             elif i < 0:
#                 count += 1
#                 short_count += 1
#         return count, long_count, short_count
#     def wallet_balance():
#         B_account, acc_name = account_client, account_name
#         wallet_account = B_account.futures_account()
#         total_balance = float(wallet_account['totalWalletBalance'])
#         unrealizedPnl = float(wallet_account['totalUnrealizedProfit'])
#         # print(unrealizedPnl, total_balance)
#         total_balance = total_balance + unrealizedPnl
#         return float(total_balance), float(unrealizedPnl)
#     total_balance, unrealizedPnl = wallet_balance()
#     count, long_count, short_count = count_position()

#     #----------------------------------------------------------------
#     trades_dict = {}
#     overall_trades = 0
#     overall_win_trades = 0

#     for index, row in final_df.iterrows():
#         #trades_dict init
#         if row.pair not in trades_dict:
#             trades_dict[row.pair] = {"trades": 0, "win_trades": 0, "realizedPnl": 0}

#     for index, row in final_df.iterrows():
#         try:
#             trades_dict[row.pair]['trades'] += 1
#             overall_trades += 1
#             if row.realizedPnl > 0:
#                 trades_dict[row.pair]['win_trades'] += 1
#                 overall_win_trades += 1
#             trades_dict[row.pair]["realizedPnl"] += row.realizedPnl
#         except:
#             print("error")

#     #----------------------------------------------------------------
#     import json
#     with open('C:\\Users\\User\\Documents\\your_account\\positions.json') as file:
#         data = json.load(file)

#     df_position = pd.DataFrame(list(data.items()), columns=["pair", "position"])

#     num_pairs = 0
#     for index,row in df_position.iterrows():
#         if row.position == 1:
#             num_pairs += 1


#     else: 
#         pass