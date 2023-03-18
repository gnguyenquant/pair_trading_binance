This is a pair trading strategy in Binance writen by Giang Truong Nguyen.

I. Find pairs
1. Calculate log(TWAP_price) of both price series
2. Calculate the correlation between them.
3. Calculate the cointegration between them. 
3. We have s= x- by where x,y are two price series, s is the spread between them and b is the hedging ratio.
   Calculate s and b.
4. Calculate the the stationarity of the spread by Augmented Dicky Fuller (ADF) test.
   If pvalue from ADF is less than 0.05, we can say reject the null hypothesis that there exists unit root in our spread series.
   In other word, we are more than 95% confident that our spread series is stationary.

II. Backtest
1. There are only two parameters: entry_threshold and periods.
2. Stoploss_threshold and takeprofit_threshold are predefined as entry_threshold+1 and 0. You can further optimize them if you want.
3. A bashscript run_pairtrading.sh is provided to automate the backtest procedure.
4. The data set is split into traing and test sets.
5. The training set is to optimize the parameters while the test set is to verify them.
6. PnL plot, Sharpe ratio and fee over PnL are computed and saved in the results folder.

III. Bot
1. The apikey and secret for Binance API must be provided in Binancelogin.py
2. Provide your optimized parameters in the main file bot_pairtrading_***_***.py and run it.
3. The realtime data is saved in the .csv files and positions.txt.

That's it! Hope you guys make some money!
