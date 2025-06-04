# IMPORT LIBRARIES
import os
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import dataframe_image as dfi
from datetime import timedelta, datetime
import time
import pickle
import argparse
# import mlflow
import json
import sys
import os




sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# For the model
import xgboost
from sklearn.metrics import classification_report

from utils import *
from strategy_backtest3 import get_features

def log_accuracy(symbol, file, log):
    rep = pd.read_csv(f"{models_dir}/{symbol}_{file}.csv")
    accuracy_row = rep[rep['Unnamed: 0'] == 'accuracy']
    acc = accuracy_row['f1-score'].values[0]
    # mlflow.log_metric(f'{log} Accuracy', acc)

# if __name__ == "__main__":    

    # parser = argparse.ArgumentParser()
    # parser.add_argument('-exp', '--experiment_name', type = str, required = True)
    # parser.add_argument('-run', '--run_name', type = str, required = True)
    # parser.add_argument('-p_ver', '--param_version', type = str, required = True)
    # parser.add_argument('-runx', '--run_num', type = str, required = True)
    # parser.add_argument('-t', '--type', type = str, required = True)
    # args = parser.parse_args()

    # symbol = args.experiment_name
    # run_name = args.run_name

    # p_ver = args.param_version
    # run_x = args.run_num
    # param_runx = ''.join([p_ver, run_x])
    # version = '_'.join([symbol, param_runx])

    # mlflow.set_tracking_uri("http://localhost:5000")
    # mlflow.set_experiment(version)
    
    # mlflow.start_run(run_name = run_name)
    
    # mod_run = '_'.join(run_name.split('_')[:2])
    
    
models_dir = r'..\financialDashboard\backtest_implementation_ninja\validate_trades\models\ATOMUSDT\ATOMUSDT_P0501\ATOMUSDT_115'
output_dir = r'..\static\backtest_outputs'
os.makedirs(output_dir, exist_ok = True)


# # Parameters for getting the data



def main(symbol, ver, interval, trade_start, trade_end):
    
    # # =========================================================
    # log_accuracy(symbol, 'pos_train', 'POS Train')
    # log_accuracy(symbol, 'pos_test', 'POS Test')
    # log_accuracy(symbol, 'neg_train', 'NEG Train')
    # log_accuracy(symbol, 'neg_test', 'NEG Test')
    # log_accuracy(symbol, 'svm_train', 'SVM Train')
    # log_accuracy(symbol, 'svm_test', 'SVM Test')
    # log_accuracy(symbol, 'svm_train1', 'SVM Train1')
    # log_accuracy(symbol, 'svm_test1', 'SVM Test1')
    # # =========================================================
    
    # mlflow.log_param('Symbol', symbol)
    set_globals(symb = symbol, tf = interval)
    
    start = time.time()

    print(f'Start backtesting the strategy with {symbol}.')
    ohlc = get_data(symbol, '1m')
    df = get_data(symbol, interval)
    df = get_features(df, symbol, model='one')

    # trade_start = '06-01-2024'
    # trade_end = datetime.now().date()

    # if args.type == 'past':
    #     trade_start = df.index[0] + pd.DateOffset(months = 1)
    #     trade_end = (datetime.now().date() - pd.DateOffset(months = 1)).date()
    # elif args.type == 'future':
    #     trade_start = (datetime.now().date() - pd.DateOffset(months = 1)).date()
    #     trade_end = datetime.now().date()

    df = df.loc[trade_start:trade_end]
    df_save = df.copy()

    print(f'Start predicting for {symbol}.')
    
    pos_model = xgboost.XGBClassifier()
    pos_model.load_model(models_dir + f"/{symbol}_pos_model_{ver}.json")
    # mlflow.log_artifact(models_dir + f"/{symbol}_pos_model.json")

    neg_model = xgboost.XGBClassifier()
    neg_model.load_model(models_dir + f"/{symbol}_neg_model_{ver}.json")
    # mlflow.log_artifact(models_dir + f"/{symbol}_neg_model.json")

    filename = models_dir + f'/{symbol}_stacked_{ver}.pickle'
    stacked_model = pickle.load(open(filename, 'rb'))
    # mlflow.log_artifact(models_dir + f'/{symbol}_stacked.pickle')

    X, y = df.drop('Signal', axis = 1), df.Signal
    pos_prob = pd.DataFrame(pos_model.predict_proba(X), columns=["Pos0", "Pos1"])
    neg_prob = pd.DataFrame(neg_model.predict_proba(X), columns=["Neg0", "Neg1"])
    
    stacked_X = pd.concat([pos_prob, neg_prob], axis = 1)
    stacked_X = stacked_X[['Pos1', 'Neg1']]
    
    df_save['Pred_Signal'] = stacked_model.predict(stacked_X)

    # =============================================
    # Plot Decision Boundary
    # =============================================
    kernel = stacked_model.get_params()['kernel']
    h = 0.01

    x_min, x_max = 0.0, 1.0
    y_min, y_max = 0.0, 1.0
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))

    Z = stacked_model.predict(np.c_[xx.ravel(), yy.ravel()])

    # Put the result into a color plot
    Z = Z.reshape(xx.shape)
    plt.contourf(xx, yy, Z, cmap=plt.cm.ocean, alpha=0.5)

    # Plot also the training points
    plt.scatter(stacked_X['Pos1'], stacked_X['Neg1'], cmap = plt.cm.ocean, c = y, alpha = 1.0)
    plt.xlabel('Pos1')
    plt.ylabel('Neg1')
    plt.xlim(xx.min(), xx.max())
    plt.ylim(yy.min(), yy.max())
    plt.title(f"Decision Boundary: {kernel.upper()}")
    decision_boundary_path = os.path.join(output_dir, f"{symbol}_decision_boundary.png")

    plt.savefig(os.path.join(output_dir, f"{symbol}_decision_boundary.png"), dpi = 300)

    # =============================================
    # Calculate the accuracy of the model.
    # =============================================
    df2 = df_save[['Signal', 'Pred_Signal']].copy()
    df2.dropna(inplace = True)

    acc_report = classification_report(df2['Signal'], df2['Pred_Signal'], output_dict = True)
    # mlflow.log_metric('Accuracy1', acc_report['accuracy'])

    acc_report.update({"accuracy": {"precision": '--',
                                    "recall": '--',
                                    "f1-score": acc_report["accuracy"],
                                    "support": acc_report['macro avg']['support']}})
    acc_df = pd.DataFrame(acc_report).transpose()
    
    svm_backtest1_path = os.path.join(output_dir, f"{symbol}_svm_backtest1.csv")
    
    acc_df.to_csv(svm_backtest1_path)
    # mlflow.log_artifact(pth)

    # =============================================
    # without 1
    # =============================================

    df2 = df2[df2['Pred_Signal'] != 1.0]

    acc_report = classification_report(df2['Signal'], df2['Pred_Signal'], output_dict = True)
    # mlflow.log_metric('Accuracy', acc_report['accuracy'])

    acc_report.update({"accuracy": {"precision": '--',
                                    "recall": '--',
                                    "f1-score": acc_report["accuracy"],
                                    "support": acc_report['macro avg']['support']}})
    acc_df = pd.DataFrame(acc_report).transpose()
    svm_backtest_path = os.path.join(output_dir, f"{symbol}_svm_backtest.csv")
    acc_df.to_csv(svm_backtest_path)
    # mlflow.log_artifact(pth)
    
    # Get the previous signal.
    df_save['Next_Signal'] = df_save['Pred_Signal'].shift(-1)

    df3 = df_save[['Next_Signal', 'Pred_Signal']].copy()
    df3 = df3.resample('Min').ffill()

    df_merge = pd.merge(ohlc, df3, how = 'left', left_index = True, right_index = True)
    df_merge['Next_Signal'] = df_merge['Next_Signal'].shift(1)
    df_merge['Pred_Signal'] = df_merge['Pred_Signal'].shift(1)
    df_merge['symbol'] = symbol
    df_merge = df_merge[df_merge['Pred_Signal'].notna()]
    df_merge = df_merge.loc[trade_start:trade_end]
    df_merge.sort_index(inplace = True)

    summary, trades = backtest_over_dataframe(df_merge)
    # trades_merge = pd.merge(df.reset_index(level='Time'),
    #      trades.reset_index(level='entry_dt'),
    #      how='inner',
    #      on='Time',
    # ).set_index('Time')

    # trades['entry_dt'] = pd.to_datetime(trades['entry_dt'])
    # trades.set_index('entry_dt', inplace=True)
    # trades.index.names = ['Time']
    # trades_merge = pd.merge_asof(trades, df, on='Time')
    # trades_merge['perc_return'] = ((trades_merge['exit_price']-trades_merge['entry_price'])/trades_merge['entry_price']*100)
    # filtered_trades = trades_merge[(trades_merge['perc_return'] > 2) | (trades_merge['perc_return'] < -2)]
    # filtered_trades.to_csv( output_dir + f"/merged_trades_{symbol}.csv")

    if len(trades) > 20:
        generated_files = [decision_boundary_path, svm_backtest1_path, svm_backtest_path]

        if len(trades) > 20:
            tradesheet_path = output_dir + f"/tradesheet_{symbol}.csv"
            trades.to_csv(tradesheet_path)
            generated_files.append(tradesheet_path)

            report = analyze_tradesheet(trades, output_dir)

            df_styled = report.style.background_gradient()
            report_png_path = output_dir + "/reports.png"
            dfi.export(df_styled, report_png_path, table_conversion="matplotlib")
            generated_files.append(report_png_path)

        end = time.time()
        duration = end - start
        print("End of Backtest")

        return generated_files
    # mlflow.log_param('Run Duration', time.strftime("%H:%M:%S", time.gmtime(duration)))
    # mlflow.end_run()
    print("End of Backtest")
