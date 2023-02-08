#!/bin/bash

for ((threshold=2;threshold<=3;threshold=threshold+1))
do
	for ((period=35;period<=45;period=period+1))
	do
	    python3 -u backtest_pairtrading.py $threshold $period
	done
done
