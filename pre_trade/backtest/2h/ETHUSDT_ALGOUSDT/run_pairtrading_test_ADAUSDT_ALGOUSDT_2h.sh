#!/bin/bash

for ((threshold=3;threshold<=3;threshold=threshold+1))
do
	for ((period=24;period<=50;period=period+2))
	do
	    python3 -u backtest_pairtrading_test.py $threshold $period
	done
done
