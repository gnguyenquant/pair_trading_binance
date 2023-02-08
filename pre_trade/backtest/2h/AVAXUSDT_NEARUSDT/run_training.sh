#!/bin/bash

for ((threshold=2;threshold<=2;threshold=threshold+1))
do
	for ((period=24;period<=40;period=period+2))
	do
	    python3 -u backtest_pairtrading.py $threshold $period
	done
done
