# Basic packages
import numpy as np
import pandas as pd
import json
import os

# For technical indicators
import pandas_ta as pta
import ta

def get_features(df2, symbol, model = None):

    windows_folder = r"..\AlgoforceDashboard\backtest_implementation_ninja\validate_trades\windows"
    
    default_periods = {
        'zscore_period': 7,
        'hmabb_period': 50,
        'rethma_period': 7,
        'conversion_line_period': 20,
        'baseline_period': 60,
        'leadspanb_period': 120,
        'poc_period': 200,
        'rsi_period': 11
    }
    
    if model is None:
        periods = default_periods
    else:
        filename = f'windows.json' if model == 'one' else f'posneg_windows.json'
        
        with open(os.path.join(windows_folder, filename), 'r') as file:
            dictionary = json.load(file)
        
        data = dictionary[symbol] if model == 'one' else dictionary[symbol][model]
        
        period_keys = ['zscore_period', 'hmabb_period', 'rethma_period', 'conversion_line_period', 
                       'baseline_period', 'leadspanb_period', 'poc_period', 'rsi_period']
        
        periods = {key: data.get(key, default_periods[key]) for key in period_keys}
    
    zscore_period = periods['zscore_period']
    hmabb_period = periods['hmabb_period']
    rethma_period = periods['rethma_period']
    conversion_line_period = periods['conversion_line_period']
    baseline_period = periods['baseline_period']
    leadspanb_period = periods['leadspanb_period']
    poc_period = periods['poc_period']
    rsi_period = periods['rsi_period']
    hmabbstdmult = 1.25

    df = df2.copy()
    
    df['Ret'] = (df['Open'].shift(-1) - df['Open']) / df['Open']
    df['Ret'] = df['Ret'].fillna(0.0)
    df['Signal'] = df['Ret'].apply(lambda x: 2 if x > 0.004 else 0 if x < -0.004 else 1)
    # df['Signal'] = df['Ret'].apply(lambda x: 2 if x > 0.002 and x < 0.07 else 0 if x < -0.002 and x > -0.07 else 1)

    df['High'] = df['High'].shift(1)
    df['Low'] = df['Low'].shift(1)
    df['Close'] = df['Close'].shift(1)
    df['Volume'] = df['Volume'].shift(1)
    #------------------------------------------------------------------------------------------------------------------
    # Z Score
    #------------------------------------------------------------------------------------------------------------------
    df['PriceMA'] = df['Close'].rolling(window = zscore_period).mean()
    df['PriceSTD'] = df['Close'].rolling(window = zscore_period).std()
    df['ZScore'] = (df['Close'] - df['PriceMA']) / df['PriceSTD']

    df['TimeOfDay'] = (df.index.hour * 3600 + df.index.minute * 60 + df.index.second) / 86400
    df['DayOfWeek'] = df.index.weekday / 6

    df['ZScoreLag1'] = df['ZScore'].shift(1)
    df['ZScoreLag2'] = df['ZScoreLag1'].shift(1)
    df['ZScoreLag3'] = df['ZScoreLag2'].shift(1)
    #------------------------------------------------------------------------------------------------------------------
    # Bollinger Bands of Hull MA
    #------------------------------------------------------------------------------------------------------------------
    hma = pta.hma(df['Close'], hmabb_period)
    hma_rolling_std = df['Close'].rolling(window = hmabb_period).std()
    hmabbupper = hma + hma_rolling_std * hmabbstdmult
    hmabblower = hma - hma_rolling_std * hmabbstdmult
    hmabbwidth = hmabbupper - hmabblower

    df['hmabb_WidthLag1'] = hmabbwidth
    df['hmabb_WidthLag2'] = df['hmabb_WidthLag1'].shift(1)
    df['hmabb_WidthLag3'] = df['hmabb_WidthLag2'].shift(1)
    #------------------------------------------------------------------------------------------------------------------
    # Return Lags
    #------------------------------------------------------------------------------------------------------------------
    df['RetLag1'] = df['Ret'].shift(1)
    df['RetLag2'] = df['RetLag1'].shift(1)
    df['RetLag3'] = df['RetLag2'].shift(1)
    #------------------------------------------------------------------------------------------------------------------
    # HMA of Returns
    #------------------------------------------------------------------------------------------------------------------
    df['RetHMALag1'] = pta.overlap.hma(df['RetLag1'], length =rethma_period)
    df['RetHMALag2'] = df['RetHMALag1'].shift(1)
    df['RetHMALag3'] = df['RetHMALag2'].shift(1)
    #------------------------------------------------------------------------------------------------------------------
    # Ichimoku Cloud
    #------------------------------------------------------------------------------------------------------------------
    high_conversion = df['High'].rolling(window = conversion_line_period).max()
    low_conversion = df['Low'].rolling(window = conversion_line_period).min()
    TenkanSen = (high_conversion + low_conversion) / 2

    high_base = df['High'].rolling(window = baseline_period).max()
    low_base = df['Low'].rolling(window = baseline_period).min()
    KijunSen = (high_base + low_base) / 2

    SenkouSpanA = (TenkanSen + KijunSen) / 2
    SenkouSpanB = (df['High'].rolling(window = leadspanb_period).max() + df['Low'].rolling(window = leadspanb_period).min()) / 2

    df['IchimokuCloudWidthLag1'] = SenkouSpanA - SenkouSpanB
    df['IchimokuCloudWidthLag2'] = df['IchimokuCloudWidthLag1'].shift(1)
    df['IchimokuCloudWidthLag3'] = df['IchimokuCloudWidthLag2'].shift(1)

    #------------------------------------------------------------------------------------------------------------------
    # Rolling Point of Control Ratio
    #------------------------------------------------------------------------------------------------------------------
    def RollingPoC(close, volume):
        if volume > 0.0:
            weighted_price = (close * volume).sum()
            return weighted_price / volume.sum()
        else:
            return 0.0

    df['RollingPoC'] = df.apply(lambda row: RollingPoC(row['Close'], row['Volume']), axis = 1).rolling(poc_period).mean()
    df['RollingPoCRatioLag1'] = df['Close'] / df['RollingPoC']
    df['RollingPoCRatioLag2'] = df['RollingPoCRatioLag1'].shift(1)
    df['RollingPoCRatioLag3'] = df['RollingPoCRatioLag2'].shift(1)
    #------------------------------------------------------------------------------------------------------------------
    # RSI
    #------------------------------------------------------------------------------------------------------------------
    df['RSILag1'] = ta.momentum.rsi((df['Close'] + df['Open'] + df['Low'] + df['High']) / 4, window = rsi_period)
    df['RSILag2'] = df['RSILag1'].shift(1)
    df['RSILag3'] = df['RSILag2'].shift(1)
    #------------------------------------------------------------------------------------------------------------------
    # RSI Bolling Bands
    #------------------------------------------------------------------------------------------------------------------
    bbandsRSI = pta.bbands(close = df['RSILag1'], length = 25, std = 2, append=True)

    df['RSIBBandWidth'] = bbandsRSI['BBB_25_2.0']
    df["RSIBBandUpper"] = bbandsRSI["BBU_25_2.0"]
    df["RSIBBandLower"] = bbandsRSI["BBL_25_2.0"]
    df["RSIBBandPerc"] = bbandsRSI["BBP_25_2.0"]

    df["RSIBBandWidthLag1"] = df['RSIBBandWidth'].shift(1)
    df["RSIBBandWidthLag2"] = df['RSIBBandWidthLag1'].shift(1)
    df["RSIBBandWidthLag3"] = df['RSIBBandWidthLag2'].shift(1)

    df["RSIBBandUpperLag1"] = df['RSIBBandUpper'].shift(1)
    df["RSIBBandUpperLag2"] = df['RSIBBandUpperLag1'].shift(1)
    df["RSIBBandUpperLag3"] = df['RSIBBandUpperLag2'].shift(1)

    df["RSIBBandLowerLag1"] = df['RSIBBandLower'].shift(1)
    df["RSIBBandLowerLag2"] = df['RSIBBandLowerLag1'].shift(1)
    df["RSIBBandLowerLag3"] = df['RSIBBandLowerLag2'].shift(1)

    df["RSIBBandPercLag1"] = df['RSIBBandPerc'].shift(1)
    df["RSIBBandPercLag2"] = df['RSIBBandPercLag1'].shift(1)
    df["RSIBBandPercLag3"] = df['RSIBBandPercLag2'].shift(1)
    #==================================================================================================================
    # Data Cleaning
    #==================================================================================================================
    df = df.drop(['Open', 'High', 'Low', 'Close', 'Volume', 'Ret', 'RollingPoC', "RSIBBandWidth", "RSIBBandUpper",
                    "RSIBBandLower", "RSIBBandPerc", "ZScore", "PriceMA", "PriceSTD"], axis = 1)
    # start_dt = df.index[0] + pd.DateOffset(months = 1)
    df = df.dropna()
    # df = df.loc[start_dt:]
    return df