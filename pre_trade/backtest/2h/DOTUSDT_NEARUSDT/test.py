
import pandas as pd
chosen_symbol='DOTUSDT'
compare_symbol='NEARUSDT'
timeframe = '2h'  # or '1h',, '15m', '1d'

data_path = '../../../../data/'
tables_path = data_path+'cointegration/tables/'

cointegration_data = pd.read_csv(tables_path+'layer1_{}.csv'.format(timeframe))
cointegration_data=cointegration_data[(cointegration_data['chosen_symbol']==chosen_symbol) & (cointegration_data['compare_symbol']==compare_symbol)]
#correlation=cointegration_data['correlation']
[hedging_ratio]=cointegration_data['hedgingratio_slope'].values
print(hedging_ratio)
