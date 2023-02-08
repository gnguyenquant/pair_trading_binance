This is a pair trading strategy in Binance writen by Giang Truong Nguyen.


I. Find pairs
1. Calculate the log(TWAP_price) of both price series
2. Calculate correlation between them
3. we have s= x- by where x,y are two price series, s is the spread between them and b is the hedging ratio.
   Calculate s and b.
4. Calculate the the stationarity of the spread by Augmented Dicky Fuller (ADF) test.
   If pvalue from ADF is less than 0.05, we can say reject the null hypothesis that there exists unit root in our spread series.
   In other word, we are more than 95% confident that our spread series is stationary.
