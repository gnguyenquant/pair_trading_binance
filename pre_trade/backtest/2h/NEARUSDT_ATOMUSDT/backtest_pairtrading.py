# modules
import pandas as pd
import numpy as np
import BacktestFunctions as bf
import sys
from matplotlib import pyplot as plt

# parameters
chosen_symbol = 'NEARUSDT'
compare_symbol = 'ATOMUSDT'
mode = 'training'  # or 'test'
timeframe = '2h'  # or '1h',, '15m', '1d'
threshold = int(sys.argv[1])
takeprofit = 0
stoploss = threshold+1
period = int(sys.argv[2])
critical_points = [threshold, takeprofit, stoploss]
# 0.036 for transaction fee and 0.114 for slippage, market impact etc.
transaction_cost = 0.036/100
risk_free_rate=0.05/(365*(24/2))
cash_initial = 1000
cash_percentage = 0.95

# variables
data_path = '../../../../data/'
tables_path = data_path+'cointegration/tables/'
results_path = 'results/{}/'.format(mode)
figures_path = results_path+'figures/'
texts_path = results_path+'texts/'
PnL_path=results_path+'PnL/'
cointegration_data = pd.read_csv(tables_path+'layer1_{}.csv'.format(timeframe))
cointegration_data = cointegration_data[(cointegration_data['chosen_symbol'] == chosen_symbol) & (
    cointegration_data['compare_symbol'] == compare_symbol)]
[slope] = cointegration_data['hedgingratio_slope'].values

#print('chosen symbol: {}\n compare symbol: {}'.format(chosen_symbol,compare_symbol))


# get data and resize data
chosen_symbol_df, compare_symbol_df = bf.get_data(
    data_path, chosen_symbol, compare_symbol, timeframe)
chosen_symbol_df, compare_symbol_df = bf.resize_data(
    chosen_symbol_df, compare_symbol_df)
pair_df = bf.get_pairs(chosen_symbol_df, compare_symbol_df)
# split into training set and test set
training_df, test_df = bf.get_training_test_sets(pair_df)
# calculate z-score
if mode == 'training':
    used_data_df = training_df
elif mode == 'test':
    used_data_df = test_df
used_data_df = bf.get_zscore(used_data_df, slope, period)

# backtest
time_series, price_chosen, price_compare, zscore = bf.get_data_lists(
    used_data_df)
# parameters for backtest
cash_spent_chosen = 0
cash_spent_compare = 0
amount_chosen = 0
amount_compare = 0
commission=0
cash_initial_compare = cash_initial
cash_initial_chosen = cash_initial*slope
in_position = 0  # 0:out 1:long 2:short
positions = [0]*len(zscore)
PnL_final = 0
PnL=[0]*len(zscore)

# headings for output files
with open('{}{}_{}_{}_{}_{}.txt'.format(texts_path, chosen_symbol, compare_symbol, timeframe,
                                         threshold, period), 'a') as f:
    f.write('Trading pair: {} vs {}.\n'.format(chosen_symbol, compare_symbol))
    f.write('Criteria: timeframe= {}, threshold= {}, takeprofit={}, stoploss={}, period={}, cash{}= {:.2f}, cash{}= {:.2f}\n'
            .format(timeframe, threshold, takeprofit, stoploss, period, chosen_symbol, cash_initial_chosen, compare_symbol, cash_initial_compare))
for i in range(len(zscore)):
    if in_position == 1:  # if position is long
        if zscore[i] < -stoploss or zscore[i] > -takeprofit:
            cash_back_chosen, commission_chosen = bf.get_out_position(
                amount_chosen, price_chosen[i], transaction_cost)
            cash_back_compare, commission_compare = bf.get_out_position(
                amount_compare, price_compare[i], transaction_cost)
            amount_chosen = 0
            amount_compare = 0
            commission=commission+commission_chosen+commission_compare
            PnL_chosen, PnL_compare = bf.get_PnL(
                cash_spent_chosen, cash_back_chosen, cash_spent_compare, cash_back_compare)
            PnL_total = -PnL_chosen+PnL_compare
            PnL[i]=PnL_total/(cash_spent_chosen+cash_spent_compare)
            #PnL[i]=PnL_total
            PnL_final = PnL_final+PnL_total
            cash_initial_chosen = cash_initial_chosen-PnL_chosen-commission_chosen
            cash_initial_compare = cash_initial_compare+PnL_compare-commission_compare
            in_position = 0
            positions[i] = -1
            if zscore[i] < -stoploss:
                # stop loss
                action = 'STOP LOSS'
            elif zscore[i] > -takeprofit:
                # take profit
                action = 'TAKE PROFIT'
            with open('{}{}_{}_{}_{}_{}.txt'.format(texts_path, chosen_symbol, compare_symbol, timeframe,
                                                     threshold, period), 'a') as f:
                f.write('{}, {}, PnL = {:.2f}\n'.format(
                    time_series[i], action, PnL_total))
    elif in_position == 2:  # short
        if zscore[i] > stoploss or zscore[i] < takeprofit:
            # stop loss
            cash_back_chosen, commission_chosen = bf.get_out_position(
                amount_chosen, price_chosen[i], transaction_cost)
            cash_back_compare, commission_compare = bf.get_out_position(
                amount_compare, price_compare[i], transaction_cost)
            amount_compare = 0
            amount_chosen = 0
            commission=commission+commission_chosen+commission_compare
            PnL_chosen, PnL_compare = bf.get_PnL(
                cash_spent_chosen, cash_back_chosen, cash_spent_compare, cash_back_compare)
            PnL_total = PnL_chosen-PnL_compare
            PnL[i]=PnL_total/(cash_spent_chosen+cash_spent_compare)
            #PnL[i]=PnL_total
            PnL_final = PnL_final+PnL_total
            cash_initial_chosen = cash_initial_chosen+PnL_chosen-commission_chosen
            cash_initial_compare = cash_initial_compare-PnL_compare-commission_compare
            in_position = 0
            positions[i] = -2
            if zscore[i] > stoploss:
                action = 'STOP LOSS'
            elif zscore[i] < takeprofit:
                action = 'TAKE PROFIT'
            with open('{}{}_{}_{}_{}_{}.txt'.format(texts_path, chosen_symbol, compare_symbol, timeframe,
                                                     threshold, period), 'a') as f:
                f.write('{}, {}, PnL = {:.2f}\n'.format(
                    time_series[i], action, PnL_total))
    elif in_position == 0:
        # entry position
        if zscore[i] < -threshold or zscore[i] > threshold:
            cash_spent_chosen, amount_chosen, commission_chosen, cash_initial_chosen =\
                bf.get_entry(
                    cash_initial_chosen, cash_percentage, price_chosen[i], transaction_cost)
            cash_spent_compare, amount_compare, commission_compare, cash_initial_compare =\
                bf.get_entry(
                    cash_initial_compare, cash_percentage, price_compare[i], transaction_cost)
            commission=commission+commission_chosen+commission_compare
            if zscore[i] < -threshold:
                # long compare, short chosen
                in_position = 1
                positions[i] = 1
                with open('{}{}_{}_{}_{}_{}.txt'.format(texts_path, chosen_symbol, compare_symbol, timeframe,
                                                         threshold, period), 'a') as f:
                    f.write('{}, ENTRY, short {}, long {}\n'.format(
                        time_series[i], chosen_symbol, compare_symbol))
            elif zscore[i] > threshold:
                # long chosen, short compare
                in_position = 2
                positions[i] = 2
                with open('{}{}_{}_{}_{}_{}.txt'.format(texts_path, chosen_symbol, compare_symbol, timeframe,
                                                         threshold, period), 'a') as f:
                    f.write('{}, ENTRY, long {}, short {}\n'.format(
                        time_series[i], chosen_symbol, compare_symbol))

with open('{}{}_{}_{}_{}_{}.txt'.format(texts_path, chosen_symbol, compare_symbol, timeframe,
                                         threshold, period), 'a') as f:
    f.write('PnL_final: {:.2f}\n'.format(PnL_final))


# plot
fig, ax1, ax2, ax3 = bf.get_backtest_plot(chosen_symbol, compare_symbol, time_series, price_chosen,
                                          price_compare, positions, zscore, critical_points)
fig.savefig('{}{}_{}_{}_{}_{}.png'.format(figures_path, chosen_symbol, compare_symbol, timeframe,
                                          threshold, period))
plt.close('{}{}_{}_{}_{}_{}.png'.format(figures_path, chosen_symbol, compare_symbol, timeframe,
                                          threshold, period))

#analysis PnL
fee_over_PnL=abs(commission/PnL_final)
annualized_Sharpe,max_drawdown=bf.analysis_PnL(chosen_symbol,compare_symbol,time_series,PnL,risk_free_rate,fee_over_PnL)
plt.savefig('{}{}_{}_{}_{}_{}.png'.format(PnL_path, chosen_symbol, compare_symbol, timeframe,
                                     threshold, period))
plt.close('{}{}_{}_{}_{}_{}.png'.format(PnL_path, chosen_symbol, compare_symbol, timeframe,
                                     threshold, period))
     
with open('{}backtest_{}_{}.csv'.format(results_path, mode, timeframe), 'a') as f:
    f.write('{},{},{},{},{},{:.2f},{:.2f},{:.2f},{:.2f}\n'.format(chosen_symbol, compare_symbol, timeframe,
                                                   threshold, period, PnL_final,annualized_Sharpe,max_drawdown,fee_over_PnL))
