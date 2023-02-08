#!/bin/bash

for ((threshold=2;threshold<=4;threshold=threshold+1))
do
	for ((period=10;period<=60;period=period+10))
	do
	    python3 -u backtest_pairtrading.py $threshold $period
	done
done
