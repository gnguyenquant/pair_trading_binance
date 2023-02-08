import pandas as pd
import matplotlib.pyplot as plt
import CointegrationFunctions as cf


data_path = '../../data/'
layer1_symbols_list = ['ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'AVAXUSDT', 'ADAUSDT', 'DOTUSDT',
                       'ALGOUSDT', 'NEARUSDT', 'ATOMUSDT']
timeframes = ['15m','1h','2h','1d']

for timeframe in timeframes:
    datas = []
    for i in range(len(layer1_symbols_list)-1):
        for j in range(i+1, len(layer1_symbols_list)):
            chosen_symbol = layer1_symbols_list[i]
            compare_symbol = layer1_symbols_list[j]
            chosen_symbol_df, compare_symbol_df = cf.get_data(
                data_path, chosen_symbol, compare_symbol, timeframe)
            chosen_symbol_df, compare_symbol_df = cf.resize_data(
                chosen_symbol_df, compare_symbol_df)
            pair_df = cf.get_pairs(chosen_symbol_df, compare_symbol_df)
            training_df, test_df = cf.get_training_test_sets(pair_df)
            crypto_correlation = cf.get_correlation(training_df)
            slope, intercept = cf.get_cointegration(training_df)
            pvalue = cf.get_ADFpvalue(training_df, slope, intercept)
            if pvalue <= 0.05:
                data_line = [chosen_symbol, compare_symbol,
                             crypto_correlation, slope, intercept, pvalue]
                datas.append(data_line)
                cf.get_correlation_plots(chosen_symbol, compare_symbol,
                                         training_df, slope, intercept, pvalue)
                plt.savefig(data_path+'cointegration/figures/{}_{}_{}.png'.format(
                    chosen_symbol, compare_symbol, timeframe))
                plt.close(data_path+'cointegration/figures/{}_{}_{}.png'.format(
                    chosen_symbol, compare_symbol, timeframe))
    columns = ['chosen_symbol', 'compare_symbol', 'correlation', 'hedgingratio_slope',
               'spread_intercept', 'pvalue']
    datas_df = pd.DataFrame(datas, columns=columns)
    datas_df.sort_values(by=['pvalue'], ignore_index=True, inplace=True)
    datas_df.to_csv(
        data_path+'cointegration/tables/layer1_{}.csv'.format(timeframe), index=False)
