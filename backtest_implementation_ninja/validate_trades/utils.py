import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import calendar
import sqlalchemy as db
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
# import mlflow
from scipy.stats import t, kurtosis, skew
import warnings
warnings.filterwarnings("ignore")
def set_globals(symb = 'BTCUSDT', tp = 5.0, sl = 5.0, tf = '4h'):
    """
    VIP2: 0.000315, 0.000126
    VIP4: 0.00027, 0.00009
    """
    # GLOBAL VARIABLES
    global market_fee, limit_fee, init_balance, symbol, take_profit, stop_loss, interval
    market_fee = 0.000315
    limit_fee = 0.000126
    init_balance = 500000
    take_profit = tp
    stop_loss = sl
    symbol = symb

    interval = tf

    # mlflow.log_param('Take Profit', take_profit)
    # mlflow.log_param('Stop Loss', stop_loss)
    # mlflow.log_param('Market Fee', market_fee)
    # mlflow.log_param('Limit Fee', limit_fee)

def get_data(symb, interval = '4h'):

    # Data from Server
    
    if interval == '1m':
        table_name = f"{symb.lower()}_{interval}"
    else:
        table_name = f'{symb.lower()}_{interval}'

    try:
        engine = db.create_engine('mysql+mysqlconnector://afdashboard:password@192.168.50.39:3306/ohlc')
        query = f"SELECT * FROM {table_name};"
        
        with engine.connect() as conn, conn.begin():
            frame = pd.read_sql_query(text(query), conn)
            
        frame.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume']
        frame['Time'] = pd.to_datetime(frame['Time'])
        frame = frame.set_index('Time')
    except SQLAlchemyError as e:
    # except Exception as error:
        print("no data on sql or network connection error", e)
        frame = None
    
    print(f'Finished importing the {interval} data for {symb}.')
    return frame







# get_data()
def reset(df):
    df['position'] = False
    df['type'] = 'NA'
    df['entry_dt'] = 0.0
    df['entryprice'] = 0.0
    return df

def backtest_over_dataframe(df):
    
    balance = init_balance
    position_size = 50000
    
    limit = {'15m': 15, '30m': 30, '1h': 60, '2h': 120, '4h': 240, '1d': 1440}

    # Initialize a dataframe for tracking the trades.
    trades = pd.Series()
    trades['position'] = False
    trades['type'] = 'NA'
    trades['entry_dt'] = 0.0
    trades['entryprice'] = 0.0

    # Initialize a list for storing data for the trades.
    trades_list = []
    pos = {}

    for i in range(len(df)):
        
        # Get the current candle
        current = df.iloc[i]

        # Get the time elapsed from start of the bar.
        current_time = current.name
        time_elapsed = (60 * current_time.hour + current_time.minute) % limit[interval]

        # -----------------------------------------
        # ENTRY CONDITIONS
        # -----------------------------------------
        long_condition = True
        long_condition = long_condition and current['Pred_Signal'] == 2.0
        long_condition = long_condition and time_elapsed == 1.0
        
        short_condition = True
        short_condition = short_condition and current['Pred_Signal'] == 0.0
        short_condition = short_condition and time_elapsed == 1.0

        # -----------------------------------------
        # EXIT CONDITIONS
        # -----------------------------------------
        exit_condition = True
        exit_condition = exit_condition and time_elapsed == 0.0
        exit_condition = exit_condition and current['Pred_Signal'] != current['Next_Signal']

        # Check if there is an open trade.
        if trades['position'] == True:

            if trades['type'] == 'Long':
                
                # Check if the stop loss was hit.
                # Stop loss has priority over take profit.
                if current['Low'] <= pos['sl']:
                    
                    # Calculate profit/loss.
                    profit_loss = - position_size * stop_loss
                    pos['exit_dt'] = current.name
                    pos['exit_price'] = pos['sl']
                    pos['exit_type'] = 'stoploss'

                    # Calculate the fees.
                    open_fee = position_size * market_fee
                    close_fee = abs(position_size + profit_loss) * market_fee
                    total_fee = open_fee + close_fee
                    pos['profit_loss'] = profit_loss
                    pos['fees'] = total_fee

                    # Update the balance.
                    balance = balance + position_size + profit_loss - total_fee

                    # Update the tracker.
                    trades = reset(trades)

                    # Update the trades_list.
                    trades_list.append(pos)

                    # Remove the position for the symbol.
                    pos = {}
                
                # Check if the take profit was hit.
                elif current['High'] >= pos['tp']:
                
                    # Calculate profit/loss.
                    profit_loss = position_size * take_profit
                    pos['exit_dt'] = current.name
                    pos['exit_price'] = pos['tp']
                    pos['exit_type'] = 'takeprofit'

                    # Calculate the fees.
                    open_fee = position_size * market_fee
                    close_fee = abs(position_size + profit_loss) * limit_fee
                    total_fee = open_fee + close_fee
                    pos['profit_loss'] = profit_loss
                    pos['fees'] = total_fee

                    # Update the balance.
                    balance = balance + position_size + profit_loss - total_fee

                    # Update the tracker.
                    trades = reset(trades)

                    # Update the trades_list.
                    trades_list.append(pos)

                    # Remove the position for the symbol.
                    pos = {}
                
                elif exit_condition:
                    
                    # Calculate profit/loss.
                    profit_loss = (current['Open'] - pos['entry_price']) * pos['qty']
                    pos['exit_dt'] = current.name
                    pos['exit_price'] = current['Open']
                    pos['exit_type'] = 'barclose'

                    # Calculate the fees.
                    open_fee = position_size * market_fee
                    close_fee = abs(position_size + profit_loss) * market_fee
                    total_fee = open_fee + close_fee
                    pos['profit_loss'] = profit_loss
                    pos['fees'] = total_fee

                    # Update the balance.
                    balance = balance + position_size + profit_loss - total_fee

                    # Update the tracker.
                    trades = reset(trades)

                    # Update the trades_list.
                    trades_list.append(pos)

                    # Remove the position for the symbol.
                    pos = {}
                
                else:

                    continue
            
            elif trades['type'] == 'Short':

                # Check if the stop loss was hit.
                # Stop loss has priority over take profit.
                if current['High'] >= pos['sl']:
                    
                    # Calculate profit/loss.
                    profit_loss = - position_size * stop_loss
                    pos['exit_dt'] = current.name
                    pos['exit_price'] = pos['sl']
                    pos['exit_type'] = 'stoploss'

                    # Calculate the fees.
                    open_fee = position_size * market_fee
                    close_fee = abs(position_size + profit_loss) * market_fee
                    total_fee = open_fee + close_fee
                    pos['profit_loss'] = profit_loss
                    pos['fees'] = total_fee

                    # Update the balance.
                    balance = balance + position_size + profit_loss - total_fee

                    # Update the tracker.
                    trades = reset(trades)

                    # Update the trades_list.
                    trades_list.append(pos)

                    # Remove the position for the symbol.
                    pos = {}
                
                # Check if the take profit was hit.
                elif current['Low'] <= pos['tp']:
                    
                    # Calculate profit/loss.
                    profit_loss = position_size * take_profit
                    pos['exit_dt'] = current.name
                    pos['exit_price'] = pos['tp']
                    pos['exit_type'] = 'takeprofit'

                    # Calculate the fees.
                    open_fee = position_size * market_fee
                    close_fee = abs(position_size + profit_loss) * limit_fee
                    total_fee = open_fee + close_fee
                    pos['profit_loss'] = profit_loss
                    pos['fees'] = total_fee

                    # Update the balance.
                    balance = balance + position_size + profit_loss - total_fee

                    # Update the tracker.
                    trades = reset(trades)

                    # Update the trades_list.
                    trades_list.append(pos)

                    # Remove the position for the symbol.
                    pos = {}
                
                elif exit_condition:
                    # Calculate profit/loss.
                    profit_loss = (current['Open'] - pos['entry_price']) * pos['qty']
                    pos['exit_dt'] = current.name
                    pos['exit_price'] = current['Open']
                    pos['exit_type'] = 'barclose'

                    # Calculate the fees.
                    open_fee = position_size * market_fee
                    close_fee = abs(position_size + profit_loss) * market_fee
                    total_fee = open_fee + close_fee
                    pos['profit_loss'] = profit_loss
                    pos['fees'] = total_fee

                    # Update the balance.
                    balance = balance + position_size + profit_loss - total_fee

                    # Update the tracker.
                    trades = reset(trades)

                    # Update the trades_list.
                    trades_list.append(pos)

                    # Remove the position for the symbol.
                    pos = {}
                
                else:
                    continue

        else:

            if long_condition:

                # LONG
                entry_price = current['Open']
                quantity = position_size / entry_price

                # Calculate TP-SL.
                SL_price = entry_price * (1 - stop_loss)
                TP_price = entry_price * (1 + take_profit)

                # Update the tracker.
                trades['position'] = True
                trades['type'] = 'Long'
                trades['entry_dt'] = current.name
                trades['entryprice'] = entry_price

                # Add the new position.
                pos = {
                    'symbol': symbol,
                    'entry_dt': current.name,
                    'entry_price': entry_price,
                    'amt': position_size,
                    'qty': quantity,
                    'tp': TP_price,
                    'sl': SL_price,
                    'exit_dt': None,
                    'exit_price': None,
                    'exit_type': None,
                    'profit_loss': 0.0,
                    'fees': 0.0
                    }
                
                # Update the balance.
                balance = balance - position_size
        
            elif short_condition:
                
                # SHORT
                entry_price = current['Open']
                quantity = position_size / entry_price

                # Calculate TP-SL.
                SL_price = entry_price * (1 + stop_loss)
                TP_price = entry_price * (1 - take_profit)

                # Update the tracker.
                trades['position'] = True
                trades['type'] = 'Short'
                trades['entry_dt'] = current.name
                trades['entryprice'] = entry_price

                # Add the new position.
                pos = {
                    'symbol': symbol,
                    'entry_dt': current.name,
                    'entry_price': entry_price,
                    'amt': position_size,
                    'qty': - quantity,
                    'tp': TP_price,
                    'sl': SL_price,
                    'exit_dt': None,
                    'exit_price': None,
                    'exit_type': None,
                    'profit_loss': 0.0,
                    'fees': 0.0
                    }
                
                # Update the balance.
                balance = balance - position_size
            
            else:
                continue

    tradesheet = pd.DataFrame(trades_list)

    summary = {
        'final_balance': balance,
        'open_trades': 0 if not pos else 1,
        }
    
    return summary, tradesheet

def analyze_tradesheet(df, file_path):
    """
    Function for analyzing the tradesheet.
    THINGS TO DO:
    3. Omega
    12. Expected Daily Return
    13. Expected Monthly Return
    14. Expected Yearly Return
    15. Risk of Ruin
    16. Daily Value-at-Risk
    """
    reports = {}
    final_balance = init_balance + df['profit_loss'].sum() - df['fees'].sum()
    # mlflow.log_metric("Final Balance", final_balance)
    
    reports['Initial Balance'] = init_balance
    reports['Final Balance'] = str(round(final_balance, 2))
    reports['Fees'] = str(round(df['fees'].sum(), 2))
    # mlflow.log_metric("Total Fees", round(df['fees'].sum(), 2))

    # Get the dates.
    df['exit_dt'] = pd.to_datetime(df['exit_dt'])
    df['date'] = df['exit_dt'].apply(lambda x: x.date())
    reports['Start Date'] = df['date'].min()
    reports['End Date'] = df['date'].max()
    # mlflow.log_param("Start Date", df['date'].min())
    # mlflow.log_param("End Date", df['date'].max())

    # Calculate the win rate.
    reports['Total Trades'] = len(df)
    # mlflow.log_metric('Number of Trades', len(df))

    # Longest losing streak
    df['win'] = np.where(df['profit_loss'] > 0, 1, 0)
    df['g'] = (df['win'] != df['win'].shift(1)).cumsum()
    longest_loss = df.groupby('g').cumcount() + 1
    reports['Longest Losing Streak'] = longest_loss.max()
    # mlflow.log_metric('Longest Losing Streak', longest_loss.max())

    tp_hitrate = len(df[df['exit_type'] == 'takeprofit']) / len(df)
    reports['TP Hit Rate'] = tp_hitrate
    # mlflow.log_metric('TP Hit Rate', tp_hitrate)

    sl_hitrate = len(df[df['exit_type'] == 'stoploss']) / len(df)
    reports['SL Hit Rate'] = sl_hitrate
    # mlflow.log_metric('SL Hit Rate', sl_hitrate)
    
    win_rate = len(df[df['profit_loss'] > 0]) / len(df)
    reports['Win Rate w/o Fees'] = '{:,.2%}'.format(win_rate)
    # mlflow.log_metric('Win Rate w/o Fees', win_rate)

    df['pnl_fee'] = df['profit_loss'] - df['fees']
    win_rate_fee = np.where(df['pnl_fee'] > 0, 1, 0).mean()
    reports['Win Rate w/ Fees'] = '{:,.2%}'.format(win_rate_fee)
    # mlflow.log_metric('Win Rate w/ Fees', win_rate_fee)

    # =============================================================================================
    # PLOT THE DISTRIBUTION OF TRADE RETURNS
    # =============================================================================================
    df['trade_ret'] = df['pnl_fee'] / df['amt']
    beans = np.linspace(df['trade_ret'].min(), df['trade_ret'].max(), 101)
    
    n, _, _ = t.fit(df['trade_ret'])
    
    def map_pdf(x, **kwargs):
        nu, mu, std = t.fit(x)
        x0, x1 = df['trade_ret'].min(), df['trade_ret'].max()
        x_pdf = np.linspace(x0, x1, 1000)
        y_pdf = t.pdf(x_pdf, df = nu, loc = mu, scale = std)
        plt.plot(x_pdf, y_pdf, c='r')
    
    sns.set_style("darkgrid")
    ret = sns.displot(data = df, x = 'trade_ret', kde = True, stat = 'density', bins = beans)
    ret.map(map_pdf, 'trade_ret')
    ret.set(xlabel = 'Return', xlim = (df['trade_ret'].min(), df['trade_ret'].max()), title = 'Distribution of Trade Returns')
    plt.legend(['KDE', 't-Distribution'], fontsize = 'xx-small')
    plt.axvline(df['trade_ret'].mean(), ls = '--', c = 'red')
    plt.tight_layout()
    ret.figure.savefig(os.path.join(file_path, "trade_returns.png"), dpi = 200)
    plt.close()
    
    # mlflow.log_artifact(os.path.join(file_path, "trade_returns.png"))
    
    # =============================================================================================
    # DAILY RETURNS
    # =============================================================================================
    total_return = df['pnl_fee'].sum() / init_balance
    reports['Cumulative Return'] = '{:,.2%}'.format(total_return)
    # mlflow.log_metric('Cumulative Return', total_return)
    
    # PnL per Trade
    pnl_per_trade = df['pnl_fee'].sum() / len(df)
    reports['PnL per Trade'] = "%.2f" % pnl_per_trade
    # mlflow.log_metric('PnL per Trade', pnl_per_trade)

    # Calculate annual return.
    years = pd.Timedelta(df['date'].max() - df['date'].min()).days / 365
    reports['Average Annual Return'] = '{:,.2%}'.format(total_return / years)
    cagr = ((final_balance / init_balance) ** (1/years)) - 1
    reports['CAGR'] = '{:,.3%}'.format(cagr)
    # mlflow.log_metric('Average Annual Return', total_return / years)
    # mlflow.log_metric('CAGR', cagr)

    # =============================================================================================
    # DRAWDOWNS
    # =============================================================================================
    sf = df.groupby('date')['pnl_fee'].sum()
    sf = sf.to_frame(name = 'PnL')
    sf['running_bal'] = sf['PnL'].cumsum() + init_balance
    sf['peaks'] = sf['running_bal'].cummax()
    sf['drawdown'] = (sf['running_bal'] - sf['peaks']) / sf['peaks']
    dd_idx = sf['drawdown'].argmin()
    mdd_dollars = sf['running_bal'].iloc[dd_idx] - sf['peaks'].iloc[dd_idx]
    pldd_ratio = df['pnl_fee'].sum() / abs(mdd_dollars)
    reports['PL/DD Ratio'] = "%.2f" % pldd_ratio
    # mlflow.log_metric('PL/DD Ratio', pldd_ratio)

    simple_drawdown = mdd_dollars / init_balance
    reports['Simple MDD'] = '{:,.3%}'.format(simple_drawdown)
    # mlflow.log_metric('Simple MDD', simple_drawdown)
    
    profit_factor = df.loc[df['pnl_fee'] > 0, 'pnl_fee'].sum() / abs(df.loc[df['pnl_fee'] < 0, 'pnl_fee'].sum())
    reports['Profit Factor'] = str(round(profit_factor, 2))
    # mlflow.log_metric('Profit Factor', profit_factor)
    
    win_num = len(df[df['pnl_fee'] > 0.0])
    lose_num = len(df[df['pnl_fee'] < 0.0])
    win = df[df['pnl_fee'] > 0.0]['pnl_fee'].sum()
    loss = abs(df[df['pnl_fee'] < 0.0]['pnl_fee'].sum())
    payoff_ratio = (win / loss) * (lose_num / win_num)
    reports['Payoff Ratio'] = "%.2f" % payoff_ratio
    # mlflow.log_metric('Payoff Ratio', payoff_ratio)

    mdd = sf['drawdown'].min()
    reports['Maximum Drawdown'] = '{:,.2%}'.format(mdd)
    # mlflow.log_metric('Maximum Drawdown', mdd)

    # =============================================================================================
    # DRAWDOWN PERIOD, HIT AND RECOVERY
    # =============================================================================================
    # maxdd = sf['drawdown'].argmin()

    # sf['to_check'] = sf.loc[:, 'drawdown']
    # sf['to_check'] = sf['to_check'].apply(lambda x: 0 if x >= 0 else -1)

    # m = sf['drawdown'].lt(0)
    # value = (m != m.shift())[m].cumsum()

    # sf['to_check'] = value
    # sf['to_check'] = sf['to_check'].fillna(0)
    # dd = sf['to_check'].iloc[maxdd]
    # sf = sf.reset_index()

    # dd_period = 0
    # dd_hit = 0

    # for index, row in sf.iterrows():
    #     if row['to_check'] == dd:
    #         dd_period += 1

    # for index, row in sf.iterrows():
    #     if row['to_check'] == dd:
    #         dd_hit += 1
    #         if index == maxdd:
    #             break
    
    # reports['Drawdown Period'] = dd_period
    # reports['Drawdown Hit'] = dd_hit
    # rec_period = dd_period - dd_hit
    # reports['Recovery Period'] = rec_period

    # dd_date = sf['date'].iloc[maxdd]
    # reports['Drawdown Hit Date'] = dd_date
    # sf = sf.set_index('date')

    ###### PLOT THE DRAWDOWN ######
    fig, ax = plt.subplots()  
    ax.plot(sf.index, 'drawdown', data = sf, color = "green")
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval = 6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.setp(ax.get_xticklabels(), rotation = 45, ha = "right")
    fig.suptitle('Plot of the Drawdown', size = 14)
    fig.tight_layout()
    plt.savefig(os.path.join(file_path, "drawdown.png"), dpi = 100)
    plt.close()
    
    # mlflow.log_artifact(os.path.join(file_path, "drawdown.png"))

    ###### PLOT THE EQUITY CURVE ######
    fig, ax = plt.subplots()  
    ax.plot(sf.index, 'running_bal', data = sf)
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval = 6))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.setp(ax.get_xticklabels(), rotation = 45, ha = "right")
    fig.suptitle('Equity Curve', size = 14)
    fig.tight_layout()
    plt.savefig(os.path.join(file_path, "equity_curve.png"), dpi = 100)
    plt.close()
    
    # mlflow.log_artifact(os.path.join(file_path, "equity_curve.png"))

    ###### PLOT THE WIN RATE ######
    # fig = plt.figure(figsize = (10, 5 * rws))
    # fig.suptitle('Convergence of the Win Rates')
    
    # for i in range(tot):
    #     ax = fig.add_subplot(rws, 2, post[i])
    #     symb = symbols[i]
    #     win_list[symb].plot()
    #     ax.set_title(symb)
    
    # ax = fig.add_subplot(rws, 2, tot + 1)
    # win_list['total'].plot()
    # ax.set_title('ALL')

    # fig.tight_layout()
    # plt.savefig(file_path + "/win_rates.png", dpi = 100)
    # plt.close()
    # mlflow.log_artifact(file_path + "/win_rates.png")

    ###### MONTHLY RETURNS ######
    sf['returns'] = sf['running_bal'].pct_change().fillna((sf['running_bal'][0] / init_balance) - 1)
    reports['Average Daily Return'] = "%.2f" % sf['returns'].mean()
    reports['Average Win'] = '{:,.2f}'.format(sf[sf['returns'] > 0]['PnL'].mean())
    reports['Average Loss'] = '{:,.2f}'.format(abs(sf[sf['returns'] < 0]['PnL'].mean()))
    reports['Worst Daily Return'] = '{:,.2%}'.format(sf['returns'].min())
    # mlflow.log_metric('Average Win', sf[sf['returns'] > 0]['PnL'].mean())
    # mlflow.log_metric('Average Loss', abs(sf[sf['returns'] < 0]['PnL'].mean()))
    # mlflow.log_metric('Worst Daily Return', sf['returns'].min())

    # =====================================================
    # CORRELATION
    # =====================================================
    spx = get_data("spx", "1d")
    spx['Return'] = spx['Close'].pct_change()
    spx = spx.loc[df['date'].min():df['date'].max()]
    rf = sf.loc[df['date'].min():df['date'].max()].copy()
    corr_spx = spx['Return'].corr(rf['returns'])
    reports['SP500 Corr'] = corr_spx
    # mlflow.log_metric('SP500 Correlation', corr_spx)
    
    dxy = get_data("dxy", "1d")
    dxy['Return'] = dxy['Close'].pct_change()
    dxy = dxy.loc[df['date'].min():df['date'].max()]
    rf = sf.loc[df['date'].min():df['date'].max()].copy()
    corr_dxy = dxy['Return'].corr(rf['returns'])
    reports['DXY Corr'] = corr_dxy
    # mlflow.log_metric('DXY Correlation', corr_dxy)

    btc = get_data("btcusdt", "1d")
    btc['Return'] = btc['Close'].pct_change()
    btc = btc.loc[df['date'].min():df['date'].max()]
    rf = sf.loc[df['date'].min():df['date'].max()].copy()
    corr_btc = btc['Return'].corr(rf['returns'])
    reports['BTC Corr'] = corr_btc
    # mlflow.log_metric('BTC Correlation', corr_btc)

    sf.index = pd.to_datetime(sf.index)
    tf = sf.groupby(pd.Grouper(freq = 'M'))['PnL'].sum()
    tf = tf.to_frame(name = 'mr')
    tf['monthly_bal'] = tf['mr'].cumsum() + init_balance
    tf['monthly_ret'] = tf['monthly_bal'].pct_change().fillna((tf['monthly_bal'][0] / init_balance) - 1)
    tf['mr'] = tf['monthly_ret'] * 100
    tf['Month'] = tf.index.month
    tf['Year'] = tf.index.year
    tf['Month'] = tf['Month'].apply(lambda x: calendar.month_abbr[x])
    tf = tf.pivot(values = 'mr', index = 'Year', columns = 'Month')
    cols = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for month in months:
        if month in tf.columns.tolist():
            cols.append(month)
    tf = tf[cols]
    tf.columns.name = None
    tf = tf.fillna(0.0)
    fig, ax = plt.subplots(figsize = (20, 10))
    sns.set_theme(font_scale = 1.3)
    ax = sns.heatmap(tf, ax = ax, annot = True, annot_kws = {"size": 20}, center = 0, fmt = "0.2f",
                     linewidths = 0.1, square = True, cbar = True, cbar_kws = {"shrink": 0.5, "pad": 0.02}, cmap = 'RdYlGn')
    cbar = ax.collections[0].colorbar
    cbar.ax.tick_params(labelsize = 18)
    ax.set_xticklabels(ax.get_xmajorticklabels(), fontsize = 18)
    ax.set_title("Monthly Return (%)\n", fontsize = 28, color = "black", fontweight = "bold")
    ax.set_xlabel("\nMonth", size = 25)
    ax.set_ylabel("Year\n", size = 25)
    plt.tight_layout()
    plt.savefig(os.path.join(file_path, "monthly_return.png"))
    plt.close()
    
    # mlflow.log_artifact(os.path.join(file_path, "monthly_return.png"))
    
    # sf = tf.resample('M')['returns'].agg([('mr', lambda value: (value + 1).prod() - 1)])
    # sf['mr'] = sf['mr'] * 100
    # sf['Month'] = sf.index.month
    # sf['Year'] = sf.index.year
    # sf['Month'] = sf['Month'].apply(lambda x: calendar.month_abbr[x])
    # sf = sf.pivot(values = 'mr', index = 'Year', columns = 'Month')
    # cols = []
    # months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    # for month in months:
    #     if month in sf.columns.tolist():
    #         cols.append(month)
    # sf = sf[cols]
    # sf.columns.name = None
    # sf = sf.fillna(0.0)
    # fig, ax = plt.subplots(figsize = (10, 5))
    # ax = sns.heatmap(sf, ax = ax, annot = True, annot_kws = {"size": 10}, center = 0, fmt = "0.2f",
    #                  linewidths = 0.5, square = True, cbar = True, cbar_kws = {"shrink": 0.4, "pad": 0.02}, cmap = 'RdYlGn')
    # ax.set_title("Monthly Returns (%)\n", fontsize = 14, color = "black", fontweight = "bold")
    # ax.set_xlabel("\nMonth", size = 12)
    # ax.set_ylabel("Year\n", size = 12)
    # plt.tight_layout()
    # plt.savefig(file_path + "/monthly_returns.png")
    # plt.close()
    # mlflow.log_artifact(file_path + "/monthly_returns.png")

    # Distribution of the Daily Returns
    # beans = np.linspace(-0.05, 0.05, 101)
    # ret = sns.displot(data = tf, x = 'returns', kde = True, stat = 'density', bins = beans)
    # ret.set(xlabel = 'Returns', xlim = (-0.04, 0.04), title = 'Distribution of Daily Returns')
    # plt.axvline(tf['returns'].mean(), ls = '--', c = 'red')
    # plt.tight_layout()
    # ret.figure.savefig(file_path + "/daily_returns.png")
    # plt.close()
    # mlflow.log_artifact(file_path + "/daily_returns.png")

    ###### SHARPE, SORTINO, and CALMAR RATIOS ######
    sharpe = np.sqrt(365) * sf['returns'].mean() / sf['returns'].std()
    reports['Risk-free Rate'] = '{:,.2}'.format(0.00)
    reports['Sharpe Ratio'] = str(round(sharpe, 2))
    # mlflow.log_metric('Sharpe Ratio', sharpe)
    
    ###### SKEWNESS, KURTOSIS, TAIL RATIO ######
    skewness = skew(sf['returns'])
    kurt = kurtosis(sf['returns'], fisher = True)
    reports['Skew'] = '{:,.3f}'.format(skewness)
    reports['Kurtosis'] = '{:,.3f}'.format(kurt)
    # mlflow.log_metric('Skew', skewness)
    # mlflow.log_metric('Kurtosis', kurt)
    
    returns = sf['returns'].copy()
    up_tail = np.percentile(returns, 95)
    down_tail = abs(np.percentile(returns, 5))
    tail_ratio = up_tail / down_tail
    reports['Tail Ratio'] = '{:,.3f}'.format(tail_ratio)
    # mlflow.log_metric('Tail Ratio', tail_ratio)
    
    sortino = np.sqrt(365) * sf['returns'].mean() / sf[sf['returns'] < 0]['returns'].std()
    reports['Sortino Ratio'] = '{:,.3}'.format(sortino)
    # mlflow.log_metric('Sortino Ratio', sortino)

    calmar = sf['returns'].mean() * 365 / abs(mdd)
    reports['Calmar Ratio'] = '{:,.4}'.format(calmar)
    # mlflow.log_metric('Calmar Ratio', calmar)

    # Rearrange the entries in the 'reports' dictionary.
    order_list = ['Start Date', 'End Date', 'Initial Balance', 'Final Balance' , 'Fees', 'Total Trades', 'PnL per Trade', 'Win Rate w/o Fees',
                  'Win Rate w/ Fees', 'Longest Losing Streak', 'TP Hit Rate', 'SL Hit Rate', 'Average Win', 'Average Loss', 'Average Daily Return', 'Profit Factor', 'Payoff Ratio', 'Cumulative Return',
                  'Average Annual Return', 'CAGR', 'PL/DD Ratio', 'Maximum Drawdown', 'Simple MDD',  #'Drawdown Period', 'Drawdown Hit', 'Recovery Period', 'Drawdown Hit Date',
                  'Skew', 'Kurtosis', 'Tail Ratio', 'Risk-free Rate', 'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio', 'SP500 Corr', 'DXY Corr', 'BTC Corr']
    
    reports = {k: reports[k] for k in order_list}

    reps = pd.DataFrame.from_dict(reports, orient='index')
    reps.columns = ['Statistics']
    return reps

def generate_orders(df, file_path):
    tf = []
    for i, row in df.iterrows():
        tf.append({'Date': row['entry_dt'], 'Symbol': row['symbol'], 'Side': 'BUY' if row['qty'] > 0 else 'SELL',
                   'Price': row['entry_price'], 'Quantity': abs(row['qty']), 'Amount': 130000, 'Fee': row['fees']/2,
                   'Fee Coin': 'USDT', 'Realized Profit': 0.0, 'Quote Asset': 'USDT'})
        tf.append({'Date': row['exit_dt'], 'Symbol': row['symbol'], 'Side': 'SELL' if row['qty'] > 0 else 'BUY',
                   'Price': row['exit_price'], 'Quantity': abs(row['qty']), 'Amount': 130000, 'Fee': row['fees']/2,
                   'Fee Coin': 'USDT', 'Realized Profit': row['qty'] * (row['exit_price'] - row['entry_price'])})
    
    tf = pd.DataFrame(tf)
    tf.to_csv(file_path + "/orders.csv", index = False)