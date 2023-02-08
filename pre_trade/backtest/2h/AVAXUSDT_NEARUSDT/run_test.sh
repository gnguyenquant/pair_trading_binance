#!/bin/bash

for ((threshold=2;threshold<=2;threshold=threshold+1))
do
	for ((period=30;period<=36;period=period+1))
	do
	    python3 -u backtest_pairtrading_test.py $threshold $period
	done
done
