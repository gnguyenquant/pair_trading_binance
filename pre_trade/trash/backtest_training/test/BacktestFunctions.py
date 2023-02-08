from time import time
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


def get_training_test_sets(pair_df: pd.DataFrame):
    break_point = int(len(pair_df.index)/2)
    training_df = pair_df.iloc[0:break_point]
    test_df = pair_df.iloc[break_point:]
    test_df.reset_index(inplace=True, drop=True)
    return training_df, test_df



def get_zscore(data_df: pd.DataFrame, slope: float, period: int):
    data_df['Open Time'] = pd.to_datetime(
        data_df['Open Time']/1000, unit='s')
    data_df['n_log_price_chosen'] = slope*data_df['log_price_chosen']
    data_df['spread'] = data_df['log_price_compare'] - \
        data_df['n_log_price_chosen']
    data_df['mean_spread'] = data_df['spread'].rolling(
        period).mean().shift()  # shift to avoid look-ahead bias
    data_df['std_spread'] = data_df['spread'].rolling(
        period).std().shift()
    data_df['z-score'] = (data_df['spread'] -
                              data_df['mean_spread'])/data_df['std_spread']
    data_df.dropna(inplace=True)
    return data_df

def get_data_lists(data_df:pd.DataFrame):
    data_df['price_chosen'] = np.exp(data_df['log_price_chosen'])
    data_df['price_compare'] = np.exp(data_df['log_price_compare'])
    time_series = data_df['Open Time'].tolist()
    price_chosen = data_df['price_chosen'].tolist()
    price_compare = data_df['price_compare'].tolist()
    zscore = data_df['z-score'].tolist()
    return time_series,price_chosen,price_compare,zscore


def get_entry(cash_initial: float, cash_percentage: float, price: float, transaction_cost: float):
    cash_spent = cash_initial * \
        cash_percentage  # calculate money spent
    # calculate the amount of bought coins
    amount = cash_spent/price
    commission = cash_spent * transaction_cost  # calculate commission fee
    cash_initial = cash_initial - commission  # calculate the remain cash
    return cash_spent, amount, commission, cash_initial


def get_out_position(amount: float, price: float, transaction_cost: float):
    cash_back = amount*price
    commission = cash_back*transaction_cost
    return cash_back, commission


def get_PnL(cash_spent_chosen: float, cash_back_chosen: float, cash_spent_compare: float, cash_back_compare: float):
    PnL_chosen = -cash_spent_chosen+cash_back_chosen
    PnL_compare = -cash_spent_compare+cash_back_compare
    return (PnL_chosen, PnL_compare)


def get_positions_subplot(ax, positions:list, time_series:list, price:list):
    for i in range(len(positions)):
        if positions[i] == 1:
            ax.scatter(time_series[i], price[i], marker='v', c='red')
        elif positions[i] == -1:
            ax.scatter(time_series[i], price[i], marker='^', c='green')
        elif positions[i] == 2:
            ax.scatter(time_series[i], price[i], marker='^', c='green')
        elif positions[i] == -2:
            ax.scatter(time_series[i], price[i], marker='v', c='red')


def get_backtest_plot(chosen_symbol: str, compare_symbol: str, time_series: pd.DataFrame, price_chosen: pd.DataFrame,
                      price_compare: pd.DataFrame, positions: pd.DataFrame, zscore: pd.DataFrame, critical_points: list):
    fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(15, 15))
    ax1.plot(time_series, price_chosen)
    ax1.set_title('{}'.format(chosen_symbol))
    get_positions_subplot(ax1, positions, time_series, price_chosen)
    ax2.plot(time_series, price_compare)
    ax2.set_title('{}'.format(compare_symbol))
    get_positions_subplot(ax2, positions, time_series, price_compare)
    ax3.plot(time_series, zscore)
    ax3.set_title('z-score')
    for i in range(len(positions)):
        if positions[i] == 1 or positions[i] == -1 or positions[i] == 2 or positions[i] == -2:
            ax3.scatter(time_series[i], zscore[i], marker='*', c='red')
    for point in critical_points:
        ax3.plot(time_series, [point]*len(positions), 'k--')
        ax3.plot(time_series, [-point]*len(positions), 'k--')
    return fig, ax1, ax2, ax3


