#!/bin/bash

timeframe='2h'
pair=3
threshold=2
takeprofit=0.5
stoploss=3
period=50

python3 -u backtest_pairtrading_test.py $timeframe  $pair $threshold $takeprofit $stoploss $period
