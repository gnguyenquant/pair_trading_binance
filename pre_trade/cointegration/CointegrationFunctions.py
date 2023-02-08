import pandas as pd
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.stattools import adfuller
from decimal import Decimal


def get_data(data_path: str, chosen_symbol: str, compare_symbol: str, timeframe: str):
    chosen_symbol_df = pd.read_csv(
        '{}klines/{}_{}.csv'.format(data_path, chosen_symbol, timeframe))
    compare_symbol_df = pd.read_csv(
        '{}klines/{}_{}.csv'.format(data_path, compare_symbol, timeframe))
    return chosen_symbol_df, compare_symbol_df


def resize_data(chosen_symbol_df: pd.DataFrame, compare_symbol_df: pd.DataFrame):
    chosen_symbol_df_count = len(chosen_symbol_df.index)
    compare_symbol_df_count = len(compare_symbol_df.index)
    if chosen_symbol_df_count > compare_symbol_df_count:
        chosen_symbol_df = chosen_symbol_df.tail(compare_symbol_df_count)
        chosen_symbol_df.reset_index(drop=True, inplace=True)
    elif chosen_symbol_df_count < compare_symbol_df_count:
        compare_symbol_df = compare_symbol_df.tail(chosen_symbol_df_count)
        compare_symbol_df.reset_index(drop=True, inplace=True)
    return chosen_symbol_df, compare_symbol_df


def get_pairs(chosen_symbol_df: pd.DataFrame, compare_symbol_df: pd.DataFrame):
    pair_df = pd.DataFrame()
    pair_df['Open Time'] = chosen_symbol_df['Open Time']
    pair_df['log_price_chosen'] = np.log(chosen_symbol_df['TWAP_price'])
    pair_df['log_price_compare'] = np.log(compare_symbol_df['TWAP_price'])
    pair_df.dropna(axis=0, inplace=True)
    return pair_df


def get_training_test_sets(pair_df: pd.DataFrame):
    break_point = int(len(pair_df.index)/2)
    training_df = pair_df.iloc[0:break_point]
    test_df = pair_df.iloc[break_point:]
    test_df.reset_index(inplace=True, drop=True)
    return training_df, test_df


def get_correlation(pair_df: pd.DataFrame):
    crypto_correlation, eff = scipy.stats.pearsonr(pair_df['log_price_chosen'],
                                                   pair_df['log_price_compare'])
    pair_df.dropna(axis=0, inplace=True)
    return crypto_correlation


def get_cointegration(pair_df: pd.DataFrame):
    x = pair_df['log_price_chosen'].to_numpy().reshape((-1, 1))
    y = pair_df['log_price_compare'].to_numpy()
    model = LinearRegression()
    model.fit(x, y)
    slope = model.coef_[0]
    intercept = model.intercept_
    return slope, intercept


def get_ADFpvalue(pair_df: pd.DataFrame, slope: float, intercept: float):
    spread_series = list(pair_df['log_price_chosen']*slope -
                         pair_df['log_price_compare']+intercept)
    ADF_results = adfuller(spread_series)
    pvalue = ADF_results[1]
    return pvalue


def get_correlation_plots(chosen_symbol: str, compare_symbol: str, pair_df: pd.DataFrame, slope: float, intercept: float, pvalue: float):
    time_series = pd.to_datetime(pair_df['Open Time']/1000, unit='s')
    pair_df = pair_df.set_index(time_series)
    fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(15, 15))
    x = pair_df['log_price_chosen'].to_numpy().reshape((-1, 1))
    y = pair_df['log_price_compare'].to_numpy()
    regression_line = slope * x + intercept
    ax1.scatter(x, y)
    ax1.plot(x, regression_line, 'r',
             label='y={:.2f}x+{:.2f}'.format(slope, intercept))
    ax1.set_title('Regression')
    ax1.set(xlabel=chosen_symbol, ylabel=compare_symbol)
    ax1.legend(loc="upper right")
    ax2.plot(pair_df['log_price_chosen']*slope+intercept, label=chosen_symbol)
    ax2.plot(pair_df['log_price_compare'], label=compare_symbol)
    ax2.set_title('Regressed price movement')
    ax2.legend(loc="upper right")
    ax3.plot(pair_df['log_price_compare']-pair_df['log_price_chosen']*slope)
    ax3.plot(pair_df.index, [intercept]*(len(pair_df.index)),
             label='spread={:.2f}'.format(intercept))
    ax3.set_title('Cointegration')
    ax3.legend(title='pvalue={:.2E}'.format(
        Decimal(pvalue)), loc="upper right")
