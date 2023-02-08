# %%
import pandas as pd
from PIL import Image

# %%
training_path='results/training/'
header=['chosen_symbol','compare_symbol','timeframe','threshold','period','PnL_final','Sharpe ratio','Maximal Drawdown','Fee over PnL']
training_results_df=pd.read_csv('{}backtest_training_1h.csv'.format(training_path),names=header)
training_results_df.drop_duplicates(subset=['threshold','period'],keep='last',inplace=True)

# %%
print(training_results_df)

# %%
figures_path=training_path+'figures/'
PnL_path=training_path+'PnL/'
texts=training_path+'texts/'
chosen_symbol='DOTUSDT'
compare_symbol='NEARUSDT'
timeframe='1h'
threshold=2
period=20
im=Image.open('{}{}_{}_{}_{}_{}.png'.format(PnL_path,chosen_symbol,compare_symbol,timeframe,threshold,period))
im.show()



# %%
training_results_df.sort_values(by=['threshold','period'],inplace=True)


# %%
training_results_df.loc[training_results_df['threshold']==3].plot(x='period',y='Sharpe ratio')


# %%
test_path='results/test/'
header=['chosen_symbol','compare_symbol','timeframe','threshold','period','PnL_final','Sharpe ratio','Maximal Drawdown','Fee over PnL']
test_results_df=pd.read_csv('{}backtest_test_1h.csv'.format(test_path),names=header)
test_results_df.drop_duplicates(subset=['threshold','period'],keep='last',inplace=True)

# %%
test_results_df

# %%
test_results_df.loc[test_results_df['threshold']==3].plot(x='period',y='Sharpe ratio')
