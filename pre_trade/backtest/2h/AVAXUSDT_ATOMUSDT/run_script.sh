#!/bin/bash

for ((threshold=2;threshold<=2;threshold=threshold+1))
do
	for ((period=20;period<=35;period=period+1))
	do
	    python3 -u backtest_pairtrading.py $threshold $period
	done
done
