# %%
import pandas as pd

# %%
training_path='results/training/'
header=['chosen_symbol','compare_symbol','timeframe','threshold','period','PnL_final','Sharpe ratio','Maximal Drawdown','Fee over PnL']
training_results_df=pd.read_csv('{}backtest_training_2h.csv'.format(training_path),names=header)
#backtest_results_df.columns['chosen_symbol','compare_symbol','timeframe','threshold','takeprofit','stoploss','period','PnL_final']
training_results_df.drop_duplicates(subset=['threshold','period'],keep='last',inplace=True)


# %%
training_results_df.sort_values(by=['threshold','period'],inplace=True)
training_results_df

# %%
print(training_results_df.loc[training_results_df['threshold']==2])


