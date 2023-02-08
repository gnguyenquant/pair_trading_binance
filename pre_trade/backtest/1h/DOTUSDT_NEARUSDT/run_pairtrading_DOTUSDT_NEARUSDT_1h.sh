#!/bin/bash

for ((threshold=3;threshold<=3;threshold=threshold+1))
do
	for ((period=30;period<=60;period=period+1))
	do
	    python3 -u backtest_pairtrading.py $threshold $period
	done
done
