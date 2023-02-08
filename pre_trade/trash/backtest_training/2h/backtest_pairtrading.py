# modules
import pandas as pd
import numpy as np
import BacktestFunctions as BF
import sys

# parameters
pair = int(sys.argv[1])
timeframe = '2h'
threshold = int(sys.argv[2])
takeprofit = float(sys.argv[3])
stoploss = int(sys.argv[4])
period = int(sys.argv[5])
critical_points = [threshold, takeprofit, stoploss]
# 0.036 for transaction fee and 0.114 for slippage, market impact etc.
transaction_cost = 0.15/100
cash_initial = 1000
cash_percentage = 0.95

# variables
data_path = '../../../data/'
tables_path = data_path+'cointegration/tables/'
backtest_path = data_path+'backtest/'
training_path = backtest_path+'training/'
training_results_path = training_path+'results/'
training_figures_path = training_path+'figures/'
summary = pd.read_csv(tables_path+'layer1_{}.csv'.format(timeframe))
[chosen_symbol, compare_symbol, correlation, slope, spread, pvalue] =\
    summary.iloc[pair].to_list()
#print('chosen symbol: {}\n compare symbol: {}'.format(chosen_symbol,compare_symbol))


# get data and resize data
chosen_symbol_df, compare_symbol_df = BF.get_data(
    data_path, chosen_symbol, compare_symbol, timeframe)
chosen_symbol_df, compare_symbol_df = BF.resize_data(
    chosen_symbol_df, compare_symbol_df)
pair_df = BF.get_pairs(chosen_symbol_df, compare_symbol_df)
# split into training set and test set
training_df, test_df = BF.get_training_test_sets(pair_df)
# calculate z-score
training_df = BF.get_zscore(training_df, slope, period)

# backtest
training_df['price_chosen'] = np.exp(training_df['log_price_chosen'])
training_df['price_compare'] = np.exp(training_df['log_price_compare'])
time_series = training_df['Open Time'].tolist()
price_chosen = training_df['price_chosen'].tolist()
price_compare = training_df['price_compare'].tolist()
zscore = training_df['z-score'].tolist()
# parameters for backtest
cash_spent_chosen = 0
cash_spent_compare = 0
amount_chosen = 0
amount_compare = 0
cash_initial_compare = cash_initial
cash_initial_chosen = cash_initial*slope
in_position = 0  # 0:out 1:long 2:short
positions = [0]*len(zscore)
PnL_final = 0

# headings for output files
with open('{}{}_{}_{}_{}_{}_{}_{}.txt'.format(training_results_path, chosen_symbol, compare_symbol, timeframe,
                                              threshold, takeprofit, stoploss, period), 'a') as f:
    f.write('Trading pair: {} vs {}.'.format(chosen_symbol, compare_symbol))
    f.write('\n')
    f.write('Criteria: timeframe= {}, threshold= {}, takeprofit={}, stoploss={}, period={}, cash{}= {:.2f}, cash{}= {:.2f}'
            .format(timeframe, threshold, takeprofit, stoploss, period, chosen_symbol, cash_initial_chosen, compare_symbol, cash_initial_compare))
    f.write('\n')
for i in range(len(zscore)):
    if in_position == 1:  # if position is long
        if zscore[i] < -stoploss:
            # stop loss
            cash_back_chosen, commission_chosen = BF.get_out_position_chosen(
                amount_chosen, price_chosen[i], transaction_cost)
            cash_back_compare, commission_compare = BF.get_out_position_compare(
                amount_compare, price_compare[i], transaction_cost)
            amount_chosen = 0
            amount_compare = 0
            PnL_chosen, PnL_compare = BF.get_PnL(
                cash_spent_chosen, cash_back_chosen, cash_spent_compare, cash_back_compare)
            PnL_total = -PnL_chosen+PnL_compare
            PnL_final = PnL_final+PnL_total
            cash_initial_chosen = cash_initial_chosen-PnL_chosen-commission_chosen
            cash_initial_compare = cash_initial_compare+PnL_compare-commission_compare
            in_position = 0
            positions[i] = -1
            with open('{}{}_{}_{}_{}_{}_{}_{}.txt'.format(training_results_path, chosen_symbol, compare_symbol, timeframe,
                                                          threshold, takeprofit, stoploss, period), 'a') as f:
                f.write('{}, STOP LOSS, PnL = {:.2f}'.format(
                    time_series[i], PnL_total))
                f.write('\n')
        elif zscore[i] > -takeprofit:
            # take profit
            cash_back_chosen, commission_chosen = BF.get_out_position_chosen(
                amount_chosen, price_chosen[i], transaction_cost)
            cash_back_compare, commission_compare = BF.get_out_position_compare(
                amount_compare, price_compare[i], transaction_cost)
            amount_compare = 0
            amount_chosen = 0
            PnL_chosen, PnL_compare = BF.get_PnL(
                cash_spent_chosen, cash_back_chosen, cash_spent_compare, cash_back_compare)
            PnL_total = -PnL_chosen+PnL_compare
            PnL_final = PnL_final+PnL_total
            cash_initial_chosen = cash_initial_chosen-PnL_chosen-commission_chosen
            cash_initial_compare = cash_initial_compare+PnL_compare-commission_compare
            in_position = 0
            positions[i] = -1
            with open('{}{}_{}_{}_{}_{}_{}_{}.txt'.format(training_results_path, chosen_symbol, compare_symbol, timeframe,
                                                          threshold, takeprofit, stoploss, period), 'a') as f:
                f.write('{}, TAKE PROFIT, PnL = {:.2f}'.format(
                    time_series[i], PnL_total))
                f.write('\n')
    elif in_position == 2:  # short
        if zscore[i] > stoploss:
            # stop loss
            cash_back_chosen, commission_chosen = BF.get_out_position_chosen(
                amount_chosen, price_chosen[i], transaction_cost)
            cash_back_compare, commission_compare = BF.get_out_position_compare(
                amount_compare, price_compare[i], transaction_cost)
            amount_compare = 0
            amount_chosen = 0
            PnL_chosen, PnL_compare = BF.get_PnL(
                cash_spent_chosen, cash_back_chosen, cash_spent_compare, cash_back_compare)
            PnL_total = PnL_chosen-PnL_compare
            PnL_final = PnL_final+PnL_total
            cash_initial_chosen = cash_initial_chosen+PnL_chosen-commission_chosen
            cash_initial_compare = cash_initial_compare-PnL_compare-commission_compare
            in_position = 0
            positions[i] = -2
            with open('{}{}_{}_{}_{}_{}_{}_{}.txt'.format(training_results_path, chosen_symbol, compare_symbol, timeframe,
                                                          threshold, takeprofit, stoploss, period), 'a') as f:
                f.write('{}, STOP LOSS, PnL = {:.2f}'.format(
                    time_series[i], PnL_total))
                f.write('\n')
        elif zscore[i] < takeprofit:
            # take profit
            cash_back_chosen, commission_chosen = BF.get_out_position_chosen(
                amount_chosen, price_chosen[i], transaction_cost)
            cash_back_compare, commission_compare = BF.get_out_position_compare(
                amount_compare, price_compare[i], transaction_cost)
            amount_compare = 0
            amount_chosen = 0
            PnL_chosen, PnL_compare = BF.get_PnL(
                cash_spent_chosen, cash_back_chosen, cash_spent_compare, cash_back_compare)
            PnL_total = PnL_chosen-PnL_compare
            PnL_final = PnL_final+PnL_total
            cash_initial_chosen = cash_initial_chosen+PnL_chosen-commission_chosen
            cash_initial_compare = cash_initial_compare-PnL_compare-commission_compare
            in_position = 0
            positions[i] = -2
            with open('{}{}_{}_{}_{}_{}_{}_{}.txt'.format(training_results_path, chosen_symbol, compare_symbol, timeframe,
                                                          threshold, takeprofit, stoploss, period), 'a') as f:
                f.write('{}, TAKE PROFIT, PnL = {:.2f}'.format(
                    time_series[i], PnL_total))
                f.write('\n')
    elif in_position == 0:
        # entry position
        if zscore[i] <= -threshold:
            # long compare, short chosen
            cash_spent_chosen, amount_chosen, commission_chosen, cash_initial_chosen =\
                BF.get_entry_chosen(
                    cash_initial_chosen, cash_percentage, price_chosen[i], transaction_cost)
            cash_spent_compare, amount_compare, commission_compare, cash_initial_compare =\
                BF.get_entry_compare(
                    cash_initial_compare, cash_percentage, price_compare[i], transaction_cost)
            in_position = 1
            positions[i] = 1
            with open('{}{}_{}_{}_{}_{}_{}_{}.txt'.format(training_results_path, chosen_symbol, compare_symbol, timeframe,
                                                          threshold, takeprofit, stoploss, period), 'a') as f:
                f.write('{}, ENTRY, short {}, long {}'.format(
                    time_series[i], chosen_symbol, compare_symbol))
                f.write('\n')
        elif zscore[i] >= threshold:
            # long chosen, short compare
            cash_spent_chosen, amount_chosen, commission_chosen, cash_initial_chosen =\
                BF.get_entry_chosen(
                    cash_initial_chosen, cash_percentage, price_chosen[i], transaction_cost)
            cash_spent_compare, amount_compare, commission_compare, cash_initial_compare =\
                BF.get_entry_compare(
                    cash_initial_compare, cash_percentage, price_compare[i], transaction_cost)
            in_position = 2
            positions[i] = 2
            with open('{}{}_{}_{}_{}_{}_{}_{}.txt'.format(training_results_path, chosen_symbol, compare_symbol, timeframe,
                                                          threshold, takeprofit, stoploss, period), 'a') as f:
                f.write('{}, ENTRY, long {}, short {}'.format(
                    time_series[i], chosen_symbol, compare_symbol))
                f.write('\n')

with open('{}{}_{}_{}_{}_{}_{}_{}.txt'.format(training_results_path, chosen_symbol, compare_symbol, timeframe,
                                              threshold, takeprofit, stoploss, period), 'a') as f:
    f.write('PnL_final: {:.2f}\n'.format(PnL_final))

# plot
fig, ax1, ax2, ax3 = BF.get_backtest_plot(chosen_symbol, compare_symbol, time_series, price_chosen,
                                          price_compare, positions, zscore, critical_points)
fig.savefig('{}{}_{}_{}_{}_{}_{}_{}.png'.format(training_figures_path, chosen_symbol, compare_symbol, timeframe,
                                                threshold, takeprofit, stoploss, period))

with open('{}backtest_training_{}.csv'.format(training_path,timeframe), 'a') as f:
    f.write('{},{},{},{},{},{},{},{:.2f}\n'.format(chosen_symbol, compare_symbol, timeframe,
                                                   threshold, takeprofit, stoploss, period, PnL_final))
