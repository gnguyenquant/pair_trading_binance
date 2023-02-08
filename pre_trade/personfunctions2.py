import pandas as pd
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.stattools import adfuller
from decimal import Decimal

"""
import globals 
import sys 
pair=int(sys.argv[1])
timeframe=sys.argv[2]
#get globals variable
globals.initialize(pair=pair,timeframe=timeframe)
tables_path='../data/cointegration/tables/'
backtest_path='../data/backtest/'
backtest_results_path=backtest_path+'results/'
backtest_figures_path=backtest_path+'figures/'
summary=pd.read_csv(tables_path+'layer1_{}.csv'.format(timeframe))
[chosen_symbol,compare_symbol,correlation,slope,spread,pvalue]=\
    summary.iloc[0].to_list()
tables_path=globals.tables_path
backtest_path=globals.backtest_path
backtest_figures_path=globals.backtest_figures_path
backtest_results_path=globals.backtest_results_path
chosen_symbol=globals.chosen_symbol
compare_symbol=globals.compare_symbol
slope=globals.slope
"""
######################
#functions for cointegration
def get_data(data_path:str,chosen_symbol:str,compare_symbol:str,timeframe:str):
    chosen_symbol_df=pd.read_csv('{}klines/{}_{}.csv'.format(data_path,chosen_symbol,timeframe))
    compare_symbol_df=pd.read_csv('{}klines/{}_{}.csv'.format(data_path,compare_symbol,timeframe))
    return chosen_symbol_df, compare_symbol_df

def resize_data(chosen_symbol_df,compare_symbol_df):    
    chosen_symbol_df_count=len(chosen_symbol_df.index)
    compare_symbol_df_count=len(compare_symbol_df.index)
    if chosen_symbol_df_count>compare_symbol_df_count:
        chosen_symbol_df=chosen_symbol_df.tail(compare_symbol_df_count)
        chosen_symbol_df.reset_index(drop=True,inplace=True)
    elif chosen_symbol_df_count<compare_symbol_df_count:
        compare_symbol_df=compare_symbol_df.tail(chosen_symbol_df_count)
        compare_symbol_df.reset_index(drop=True,inplace=True)
    return chosen_symbol_df, compare_symbol_df

def get_pairs(chosen_symbol_df, compare_symbol_df):
    pair_df=pd.DataFrame()
    pair_df['Open Time']=chosen_symbol_df['Open Time']
    pair_df['log_price_chosen']=np.log(chosen_symbol_df['TWAP_price'])
    pair_df['log_price_compare']=np.log(compare_symbol_df['TWAP_price'])
    pair_df.dropna(axis=0,inplace=True)
    return pair_df

def get_correlation(pair_df):
    crypto_correlation, eff= scipy.stats.pearsonr(pair_df['log_price_chosen'],\
            pair_df['log_price_compare'])
    pair_df.dropna(axis=0,inplace=True)
    return crypto_correlation

def get_cointegration(pair_df):
    x=pair_df['log_price_chosen'].to_numpy().reshape((-1, 1))
    y=pair_df['log_price_compare'].to_numpy()
    model=LinearRegression()
    model.fit(x,y)
    slope=model.coef_[0]
    intercept=model.intercept_
    return slope, intercept

def get_ADFpvalue(pair_df,slope,intercept):
    spread_series=list(pair_df['log_price_chosen']*slope-\
        pair_df['log_price_compare']+intercept)
    ADF_results=adfuller(spread_series)
    pvalue=ADF_results[1]
    return pvalue

def get_plots(chosen_symbol,compare_symbol,pair_df,slope,intercept,pvalue):
    time_series=pd.to_datetime(pair_df['Open Time']/1000,unit='s')
    pair_df = pair_df.set_index(time_series)
    fig, (ax1, ax2, ax3) = plt.subplots(3,figsize=(15, 15))
    x=pair_df['log_price_chosen'].to_numpy().reshape((-1, 1))
    y=pair_df['log_price_compare'].to_numpy()
    regression_line = slope * x + intercept
    ax1.scatter(x, y)
    ax1.plot(x, regression_line,'r',label='y={:.2f}x+{:.2f}'.format(slope,intercept))
    ax1.set_title('Regression')
    ax1.set(xlabel=chosen_symbol,ylabel=compare_symbol)
    ax1.legend(loc="upper right")
    #plt.show()
    #plt.gcf().autofmt_xdate()
    ax2.plot(pair_df['log_price_chosen']*slope+intercept,label=chosen_symbol)
    ax2.plot(pair_df['log_price_compare'],label=compare_symbol)
    ax2.set_title('Regressed price movement')
    ax2.legend(loc="upper right")
    ax3.plot(pair_df['log_price_compare']-pair_df['log_price_chosen']*slope)
    ax3.plot(pair_df.index,[intercept]*(len(pair_df.index)),label='spread={:.2f}'.format(intercept))
    ax3.set_title('Cointegration')
    ax3.legend(title='pvalue={:.2E}'.format(Decimal(pvalue)),loc="upper right")

###########
#functions for backtest

def get_training_test_sets(pair_df):
    break_point=int(len(pair_df.index)/2)
    training_df=pair_df.iloc[0:break_point]
    test_df=pair_df.iloc[break_point:]
    test_df.reset_index(inplace=True,drop=True)    
    return training_df, test_df

def get_zscore(training_df,slope,period):
    training_df['Open Time']=pd.to_datetime(training_df['Open Time']/1000,unit='s')
    training_df['n_log_price_chosen']=slope*training_df['log_price_chosen']
    training_df['spread']=training_df['log_price_compare']-training_df['n_log_price_chosen']
    training_df['mean_spread']=training_df['spread'].rolling(period).mean().shift() #shift to avoid look-ahead bias
    training_df['std_spread']=training_df['spread'].rolling(period).std().shift()
    training_df['z-score']=(training_df['spread']-training_df['mean_spread'])/training_df['std_spread']
    training_df.dropna(inplace=True)    
    return training_df

def get_entry_chosen(cash_initial_chosen,cash_percentage,price_chosen,transaction_cost):
    cash_spent_chosen=cash_initial_chosen*cash_percentage #calculate money spent
    amount_chosen=cash_spent_chosen/price_chosen #calculate the amount of bought coins
    commission_chosen=cash_spent_chosen*transaction_cost #calculate commission fee
    cash_initial_chosen=cash_initial_chosen-commission_chosen #calculate the remain cash
    return cash_spent_chosen,amount_chosen,commission_chosen,cash_initial_chosen

def get_entry_compare(cash_initial_compare,cash_percentage,price_compare,transaction_cost):
    cash_spent_compare=cash_initial_compare*cash_percentage
    amount_compare=cash_spent_compare/price_compare
    commission_compare=cash_spent_compare*transaction_cost
    cash_initial_compare=cash_initial_compare-commission_compare
    return cash_spent_compare,amount_compare,commission_compare,cash_initial_compare

def get_out_position_chosen(amount_chosen,price_chosen,transaction_cost):
    cash_back_chosen=amount_chosen*price_chosen
    commission_chosen=cash_back_chosen*transaction_cost
    return cash_back_chosen,commission_chosen

def get_out_position_compare(amount_compare,price_compare,transaction_cost):
    cash_back_compare=amount_compare*price_compare
    commission_compare=cash_back_compare*transaction_cost
    return cash_back_compare,commission_compare

def get_PnL(cash_spent_chosen,cash_back_chosen,cash_spent_compare,cash_back_compare):
    PnL_chosen=-cash_spent_chosen+cash_back_chosen
    PnL_compare=-cash_spent_compare+cash_back_compare
    return(PnL_chosen,PnL_compare)

def get_backtest_plot(chosen_symbol,compare_symbol,time_series,price_chosen,\
    price_compare,positions,zscore,critical_points):
    fig, (ax1, ax2, ax3) = plt.subplots(3,figsize=(15, 15))
    ax1.plot(time_series,price_chosen)
    ax1.set_title('{}'.format(chosen_symbol))
    for i in range(len(positions)):
        if positions[i]==1:
            ax1.scatter(time_series[i],price_chosen[i],marker='v',c='red')
        elif positions[i]==-1:
            ax1.scatter(time_series[i],price_chosen[i],marker='^',c='green')
        elif positions[i]==2:
            ax1.scatter(time_series[i],price_chosen[i],marker='^',c='green')
        elif positions[i]==-2:
            ax1.scatter(time_series[i],price_chosen[i],marker='v',c='red')

    ax2.plot(time_series,price_compare)
    ax2.set_title('{}'.format(compare_symbol))
    for i in range(len(positions)):
        if positions[i]==1:
            ax2.scatter(time_series[i],price_compare[i],marker='^',c='green')
        elif positions[i]==-1:
            ax2.scatter(time_series[i],price_compare[i],marker='v',c='red')
        elif positions[i]==2:
            ax2.scatter(time_series[i],price_compare[i],marker='v',c='red')
        elif positions[i]==-2:
            ax2.scatter(time_series[i],price_compare[i],marker='^',c='green')

    ax3.plot(time_series,zscore)
    ax3.set_title('z-score')
    for i in range(len(positions)):
        if positions[i]==1 or positions[i]==-1 or positions[i]==2 or positions[i]==-2:
            ax3.scatter(time_series[i],zscore[i],marker='*',c='red')
    for point in critical_points:
        ax3.plot(time_series,[point]*len(positions),'k--')
        ax3.plot(time_series,[-point]*len(positions),'k--')
    return fig, ax1, ax2, ax3 


"""
def print_output(text):
    global chosen_symbol,compare_symbol,timeframe,threshold,TP_point,SL_point,period
    with open('{}_{}_{}_{}_{}_{}_{}.txt'.format(chosen_symbol,compare_symbol,timeframe,\
    threshold,TP_point,SL_point,period), 'a') as f:
        f.write(text)

def print_headings(text):
    global cash_initial_chosen,cash_initial_compare
    print_output('Trading pair: {} vs {}.'.format(chosen_symbol,compare_symbol))
    print_output('\n')
    print_output('Criteria: timeframe= {}, threshold= {}, takeprofit={}, stoploss={},\
        period={}, cash{}= {}, cash{}= {}'.format(timeframe,threshold,TP_point,\
            SL_point,period,chosen_symbol,cash_initial_chosen,compare_symbol,cash_initial_compare))
    print_output('\n')
"""
