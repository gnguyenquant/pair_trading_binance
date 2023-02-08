#!/bin/bash

echo 'chosen_symbol,compare_symbol,timeframe,threshold,takeprofit,stoploss,period,PnL_final' > ../../data/backtest/training/backtest_training.csv
declare -a takeprofits=("0" "0.5")
for ((pair=0;pair<=7;pair=pair+1))
do
       for ((threshold=2;threshold<=5;threshold=threshold+1))
        do
          for takeprofit in "${takeprofits[@]}"
           do
               let stoploss=$threshold+1
                for ((period=15;period<=60;period=period+5))
                do
                    python3 -u backtest_pairtrading.py $pair $threshold $takeprofit $stoploss $period
                done
            done
        done
done
