import pandas as pd
import matplotlib.pyplot as plt

results_path = 'results/'
test_path = results_path+'test/'
training_path = results_path+'training/'
header = ['chosen_symbol', 'compare_symbol', 'timeframe', 'threshold',
          'period', 'PnL_final', 'Sharpe ratio', 'Maximal Drawdown', 'Fee over PnL']

training_results_df = pd.read_csv(
    '{}backtest_training_2h.csv'.format(training_path), names=header)
training_results_df.drop_duplicates(
    subset=['threshold', 'period'], keep='last', inplace=True)
training_results_df.sort_values(by=['threshold', 'period'], inplace=True)
test_results_df = pd.read_csv(
    '{}backtest_test_2h.csv'.format(test_path), names=header)
test_results_df.drop_duplicates(
    subset=['threshold', 'period'], keep='last', inplace=True)
test_results_df.sort_values(by=['threshold', 'period'], inplace=True)

training_results_threshold_2_df = training_results_df.loc[training_results_df['threshold'] == 2]
test_results_threshold_2_df = test_results_df.loc[test_results_df['threshold'] == 2]
training_results_threshold_2_df = training_results_threshold_2_df.loc[(
    training_results_threshold_2_df['period'] >= 22) & (training_results_threshold_2_df['period'] <= 32)]
test_results_threshold_2_df = test_results_threshold_2_df.loc[(
    test_results_threshold_2_df['period'] >= 22) & (test_results_threshold_2_df['period'] <= 32)]
print(training_results_threshold_2_df)
print(test_results_threshold_2_df.loc[test_results_threshold_2_df['period'] == 29])
plt.figure(figsize=(16, 9))
plt.title('Threshold = 2')
plt.plot(training_results_threshold_2_df['period'].tolist(
), training_results_threshold_2_df['Sharpe ratio'].tolist(), label='training', color='Blue')
plt.plot(test_results_threshold_2_df['period'].tolist(
), test_results_threshold_2_df['Sharpe ratio'].tolist(), label='test', color='Red')
plt.xlabel('Period')
plt.ylabel('Sharpe ratio')
plt.legend()
plt.savefig('{}confirmed.png'.format(results_path))
