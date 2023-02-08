from Binancelogin import Binance_client
import websocket
import json
from datetime import datetime, timedelta
import BotPairTradingFunctions as bptf
from binance.client import Client
import pandas as pd
import numpy as np


def on_open(ws):
    print('opened connection')


def on_close(ws):
    print('closed connection')


def on_message(ws, message):
    # print('on_message')
    global chosen_data, compare_data, slope, period, cash_initial, chosen_quantity, compare_quantity, positions, in_position

    # get real time data
    json_message = json.loads(message)
    data = json_message['data']
    kline = data['k']
    realtime_symbol, realtime_data = bptf.get_realtime_data(kline=kline)
    # print(realtime_symbol)
    bptf.append_realtime_data(
        chosen_symbol, realtime_symbol, chosen_data, realtime_data)
    bptf.append_realtime_data(
        compare_symbol, realtime_symbol, compare_data, realtime_data)
    bptf.save_realtime_data(compare_symbol, realtime_symbol, realtime_data)
    bptf.save_realtime_data(chosen_symbol, realtime_symbol, realtime_data)
    bptf.get_realtime_TWAP_price(
        chosen_symbol, realtime_symbol, realtime_data, chosen_TWAP_price)
    bptf.get_realtime_TWAP_price(
        compare_symbol, realtime_symbol, realtime_data, compare_TWAP_price)

    if len(chosen_TWAP_price) == len(compare_TWAP_price):
        pair_df = bptf.get_pairs(
            chosen_opentimes_unix, chosen_TWAP_price, compare_TWAP_price)
        pair_df = bptf.get_zscore(pair_df, slope, period)
        time_series = pair_df['Open Time'].tolist()
        zscore = pair_df['z-score'].tolist()

        # parameters for backtest
        # in_position = 0  # 0:out 1:long 2:short

        # headings for output files
        if in_position == 1:  # if position is long
            if zscore[-1] < -stoploss or zscore[-1] > -takeprofit:
                # stop loss
                # long chosen, short compare
                order_status = bptf.get_out(
                    chosen_symbol, 'BUY', chosen_quantity)
                order_status = bptf.get_out(
                    compare_symbol, 'SELL', compare_quantity)
                print(order_status)
                in_position = 0
                positions.append(-1)
                if zscore[-1] < -stoploss:
                    action = 'STOP LOSS'
                elif zscore[-1] > takeprofit:
                    action = 'TAKE PROFIT'
                with open('positions.txt', 'a') as f:
                    f.write('{}, {}'.format(time_series[-1], action))
                    f.write('\n')
            else:
                positions.append(0)
        elif in_position == 2:  # short
            if zscore[-1] > stoploss or zscore[-1] < takeprofit:
                # stop loss
                # short chosen, long compare
                order_status = bptf.get_out(
                    chosen_symbol, 'SELL', chosen_quantity)
                order_status = bptf.get_out(
                    compare_symbol, 'BUY', compare_quantity)
                print(order_status)
                in_position = 0
                positions.append(-2)
                if zscore[-1] > stoploss:
                    action = 'STOP LOSS'
                elif zscore[-1] < takeprofit:
                    action = 'TAKE PROFIT'
                with open('positions.txt', 'a') as f:
                    f.write('{}, {}'.format(time_series[-1], action))
                    f.write('\n')
            else:
                positions.append(0)
        elif in_position == 0:
            # entry position
            if zscore[-1] <= -threshold:
                # short chosen,long compare
                order_status = bptf.get_entry(
                    chosen_symbol, 'SELL', chosen_quantity)
                order_status = bptf.get_entry(
                    compare_symbol, 'BUY', compare_quantity)
                print(order_status)
                in_position = 1
                action = 'ENTRY'
                with open('positions.txt', 'a') as f:
                    f.write('{}, {}'.format(time_series[-1], action))
                    f.write('\n')
                positions.append(1)
            elif zscore[-1] >= threshold:
                # long chosen, short compare
                order_status = bptf.get_entry(
                    chosen_symbol, 'BUY', chosen_quantity)
                order_status = bptf.get_entry(
                    compare_symbol, 'SELL', compare_quantity)
                print(order_status)
                in_position = 2
                positions.append(2)
                action = 'ENTRY'
                with open('positions.txt', 'a') as f:
                    f.write('{}, {}'.format(time_series[-1], action))
                    f.write('\n')
            else:
                positions.append(0)
        bptf.save_realtime_data(time_series, zscore, positions)


######
in_position = 0
chosen_quantity = 1
compare_quantity = 20
# parameters
cash_initial = 100
chosen_symbol = 'DOTUSDT'
chosen_opentimes_unix = []
chosen_opens = []
chosen_highs = []
chosen_lows = []
chosen_closes = []
chosen_TWAP_price = []
# [time,open,high,low,close]
chosen_data = [chosen_opentimes_unix,
               chosen_opens, chosen_highs, chosen_lows, chosen_closes]

compare_symbol = 'ALGOUSDT'
compare_opentimes_unix = []
compare_opens = []
compare_highs = []
compare_lows = []
compare_closes = []
compare_data = [compare_opentimes_unix,
                compare_opens, compare_highs, compare_lows, compare_closes]
compare_TWAP_price = []

positions = []
# variables
binance_client = Binance_client()
timeframe = '1m'
takeprofit = 0
threshold = 2
stoploss = threshold+1
period = 10
slope = 0.76

bptf.get_initial_data(chosen_symbol, chosen_data, period)
bptf.save_intial_data(chosen_data, chosen_symbol)
bptf.get_initial_TWAP_price(chosen_data, chosen_TWAP_price)
# print(chosen_TWAP_price)

bptf.get_initial_data(compare_symbol, compare_data, period)
bptf.save_intial_data(compare_data, compare_symbol)
bptf.get_initial_TWAP_price(compare_data, compare_TWAP_price)
# print(compare_TWAP_price)
print('step one: done')

SOCKET = "wss://fstream.binance.com/stream?streams={}@kline_{}/{}@kline_{}"\
    .format(chosen_symbol.lower(), timeframe, compare_symbol.lower(), timeframe)
# SOCKET="wss://fstream.binance.com/ws/{}@kline_{}".format(chosen_symbol,timeframe)
ws = websocket.WebSocketApp(SOCKET, on_open=on_open,
                            on_close=on_close, on_message=on_message)
ws.run_forever()
