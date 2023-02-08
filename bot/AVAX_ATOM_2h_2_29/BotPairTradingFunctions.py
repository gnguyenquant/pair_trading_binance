from dataclasses import dataclass
import pandas as pd
from Binancelogin import Binance_client
from binance.client import Client
from datetime import datetime, timedelta
from csv import writer
import numpy as np

binance_client = Binance_client()


def manupulate_binance_klines(candlesticks_df: pd.DataFrame):
    candlesticks_df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close Time',
                               'Quote Asset Volume', 'Number of Trades', 'TB Base Volume', 'TB Quote Volume', 'Ignore']
    numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume',
                       'Quote Asset Volume', 'TB Base Volume', 'TB Quote Volume']
    candlesticks_df[numeric_columns] = candlesticks_df[numeric_columns].apply(
        pd.to_numeric, axis=1)
    drop_columns = ['Close Time', 'Number of Trades',
                    'Ignore', 'TB Base Volume', 'TB Quote Volume']
    candlesticks_df.drop(drop_columns, axis=1, inplace=True)
    candlesticks_df['Quote Asset Volume'] = round(
        candlesticks_df['Quote Asset Volume'], 2)
    #futures_klines_df['Open Time'] = pd.to_datetime(futures_klines_df['Open Time']/1000, unit='s')
    return candlesticks_df


def get_TWAP_price(candlesticks_df: pd.DataFrame):
    TWAP_df = pd.DataFrame()
    TWAP_df['OC_dist'] = abs(candlesticks_df['Open']-candlesticks_df['Close'])
    TWAP_df['OH_dist'] = candlesticks_df['High']-candlesticks_df['Open']
    TWAP_df['OL_dist'] = candlesticks_df['Open']-candlesticks_df['Low']
    TWAP_df['HL_dist'] = candlesticks_df['High']-candlesticks_df['Low']
    TWAP_df['LC_dist'] = candlesticks_df['Close']-candlesticks_df['Low']
    TWAP_df['HC_dist'] = candlesticks_df['High']-candlesticks_df['Close']
    TWAP_df['OHLC_dist'] = TWAP_df['OH_dist'] + \
        TWAP_df['HL_dist']+TWAP_df['LC_dist']
    TWAP_df['OLHC_dist'] = TWAP_df['OL_dist'] + \
        TWAP_df['HL_dist']+TWAP_df['HC_dist']
    TWAP_df['OH_mean'] = 0.5*(candlesticks_df['High']+candlesticks_df['Open'])
    TWAP_df['OL_mean'] = 0.5*(candlesticks_df['Low']+candlesticks_df['Open'])
    TWAP_df['HL_mean'] = 0.5*(candlesticks_df['High']+candlesticks_df['Low'])
    TWAP_df['LC_mean'] = 0.5*(candlesticks_df['Low']+candlesticks_df['Close'])
    TWAP_df['HC_mean'] = 0.5*(candlesticks_df['High']+candlesticks_df['Close'])
    TWAP_df['OHLC_twap'] = (TWAP_df['OH_dist']*TWAP_df['OH_mean'] +
                            TWAP_df['HL_dist']*TWAP_df['HL_mean']+TWAP_df['LC_dist']*TWAP_df['LC_mean'])\
        / TWAP_df['OHLC_dist']
    TWAP_df['OLHC_twap'] = (TWAP_df['OL_dist']*TWAP_df['OL_mean'] +
                            TWAP_df['HL_dist']*TWAP_df['HL_mean']+TWAP_df['HC_dist']*TWAP_df['HC_mean'])\
        / TWAP_df['OLHC_dist']

    TWAP_df['TWAP_price'] = 0.5*(TWAP_df['OHLC_twap']+TWAP_df['OLHC_twap'])
    TWAP_price = TWAP_df['TWAP_price'].to_list()
    return TWAP_price


def get_initial_data(symbol: str, data: list, period: int, timeframe: str):
    end_date = datetime.now()
    end_date = end_date-timedelta(hours=8)  # convert from sing time to UTC
    if timeframe =='2h':
        #end_date = end_date-timedelta(hours=2)  # take the previous candle
        start_date = end_date-timedelta(hours=2*period)
        futures_klines = binance_client.futures_historical_klines(
            symbol=symbol, interval=Client.KLINE_INTERVAL_2HOUR, start_str=str(start_date), end_str=str(end_date))
    elif timeframe =='1h':
        end_date = end_date-timedelta(hours=1)  # take the previous candle
        start_date = end_date-timedelta(hours=1*period)
        futures_klines = binance_client.futures_historical_klines(
            symbol=symbol, interval=Client.KLINE_INTERVAL_1HOUR, start_str=str(start_date), end_str=str(end_date))        
    elif timeframe =='1m':
        end_date = end_date-timedelta(minutes=1)  # take the previous candle
        start_date = end_date-timedelta(minutes=1*period)
        futures_klines = binance_client.futures_historical_klines(
            symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, start_str=str(start_date), end_str=str(end_date))        
    futures_klines_df = pd.DataFrame(futures_klines)

    futures_klines_df = manupulate_binance_klines(
        futures_klines_df)
    initial_opentimes_unix = futures_klines_df['Open Time'].tolist()
    data[0].extend(initial_opentimes_unix)
    initial_opens = futures_klines_df['Open'].tolist()
    data[1].extend(initial_opens)
    initial_highs = futures_klines_df['High'].tolist()
    data[2].extend(initial_highs)
    initial_lows = futures_klines_df['Low'].tolist()
    data[3].extend(initial_lows)
    initial_closes = futures_klines_df['Close'].tolist()
    data[4].extend(initial_closes)


def save_intial_data(data: list, symbol: str):
    data_transpose_df = get_initial_data_df(data)
    data_transpose_df.to_csv('{}_data.csv'.format(
        symbol), index=False, header=False)
    return None


def get_realtime_data(kline: dict):
    is_candle_closed = kline['x']
    if is_candle_closed == True:
        realtime_symbol = kline['s']
        opentime_unix = kline['t']
        openprice = float(kline['o'])
        highprice = float(kline['h'])
        lowprice = float(kline['l'])
        closeprice = float(kline['c'])
        #['Open Time','Open','High','LoW','Close']
        realtime_data = [opentime_unix, openprice,
                         highprice, lowprice, closeprice]
        return realtime_symbol, realtime_data


def append_realtime_data(symbol: str, realtime_symbol: str, data: list, realtime_data: list):
    if symbol == realtime_symbol:
        data[0].append(realtime_data[0])
        data[1].append(realtime_data[1])
        data[2].append(realtime_data[2])
        data[3].append(realtime_data[3])
        data[4].append(realtime_data[4])
        # return data
    return None


def save_realtime_data(symbol: str, realtime_symbol: str, realtime_data: list):
    if symbol == realtime_symbol:
        with open('{}_data.csv'.format(symbol), 'a') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(realtime_data)
            f_object.close()
    return None


def get_initial_data_df(data: list):
    data_df = pd.DataFrame(data)
    data_df = data_df.transpose()
    data_df.columns = ['Open Time', 'Open', 'High', 'Low', 'Close']
    return data_df


def get_initial_TWAP_price(data: list, TWAP_price: list):
    data_df = get_initial_data_df(data)
    TWAP_price_temp = get_TWAP_price(data_df)
    TWAP_price.extend(TWAP_price_temp)


def get_realtime_TWAP_price(symbol: str, realtime_symbol: str, data: list, TWAP_price: list):
    if symbol == realtime_symbol:
        get_initial_TWAP_price(data, TWAP_price)


def get_pairs(opentimes_unix: list, chosen_TWAP_price: list, compare_TWAP_price: list):
    pair_df = pd.DataFrame()
    pair_df['Open Time'] = opentimes_unix
    pair_df['log_price_chosen'] = np.log(chosen_TWAP_price)
    pair_df['log_price_compare'] = np.log(compare_TWAP_price)
    #pair_df.dropna(axis=0, inplace=True)
    return pair_df


def get_zscore(pair_df: pd.DataFrame, slope: float, period: int):
    # pair_df['Open Time'] = pd.to_datetime(
    #    pair_df['Open Time']/1000, unit='s')
    pair_df['n_log_price_chosen'] = slope*pair_df['log_price_chosen']
    pair_df['spread'] = pair_df['log_price_compare'] - \
        pair_df['n_log_price_chosen']
    pair_df['mean_spread'] = pair_df['spread'].rolling(
        period).mean().shift()  # shift to avoid look-ahead bias
    pair_df['std_spread'] = pair_df['spread'].rolling(
        period).std().shift()
    pair_df['z-score'] = (pair_df['spread'] -
                          pair_df['mean_spread'])/pair_df['std_spread']
    pair_df.dropna(inplace=True)
    return pair_df


def get_entry(symbol: str, side: str, quantity: float):
    order_status = binance_client.futures_create_order(
        symbol=symbol, side=side, type='MARKET', quantity=quantity)
    return order_status


def get_out(symbol: str, side: str, quantity: float):
    order_status = binance_client.futures_create_order(
        symbol=symbol, side=side, type='MARKET', quantity=quantity, reduceOnly='true')
    return order_status


def save_realtime_output(time_series: list, zscore: list, positions: list):
    realtime_data_df = pd.DataFrame([time_series, zscore, positions])
    realtime_data_df = realtime_data_df.transpose()
    realtime_data_df.to_csv('realtime_data.csv', header=False, index=False)
