#!/bin/bash

for ((threshold=3;threshold<=3;threshold=threshold+1))
do
	for ((period=42;period<=57;period=period+1))
	do
	    python3 -u backtest_pairtrading.py $threshold $period
	done
done
