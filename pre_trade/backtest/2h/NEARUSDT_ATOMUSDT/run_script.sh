#!/bin/bash

for ((threshold=4;threshold<=4;threshold=threshold+1))
do
	for ((period=50;period<=80;period=period+1))
	do
	    python3 -u backtest_pairtrading.py $threshold $period
	done
done
