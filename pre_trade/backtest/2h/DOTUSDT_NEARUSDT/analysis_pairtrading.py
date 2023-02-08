import pandas as pd
results_path='results/training/'
header=['chosen_symbol','compare_symbol','timeframe','threshold','period','PnL_final','Sharpe ratio','Maximal drawdown','Fee over PnL']
backtest_results_df=pd.read_csv('{}backtest_training_2h.csv'.format(results_path),names=header)
print(backtest_results_df)
