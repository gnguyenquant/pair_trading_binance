from Binancelogin import Binance_client
from datetime import datetime, date, timedelta
import pandas as pd
from binance.client import Client
from pathlib import Path

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
    candlesticks_df['TWAP_price'] = round(TWAP_df['TWAP_price'], 6)
    return candlesticks_df


# variables
binance_client = Binance_client()
data_path = '../../data/'
klines_path = data_path+'klines/'
timeframes = ['15m']
symbols_df = pd.read_csv(data_path+'futures_USDT_symbols.txt')
symbols_df.columns = ['symbol']
symbols_list = symbols_df['symbol'].values.tolist()
start_date = '30 Apr, 2000'
end_date = '30 Jun, 2022'

# main_functions
for timeframe in timeframes:
    for symbol in symbols_list:
        if timeframe == '1h':
            candlesticks = binance_client.get_historical_klines(
                symbol, Client.KLINE_INTERVAL_1HOUR, start_date, end_date)
        elif timeframe == '2h':
            candlesticks = binance_client.get_historical_klines(
                symbol, Client.KLINE_INTERVAL_2HOUR, start_date, end_date)
        elif timeframe == '1d':
            candlesticks = binance_client.get_historical_klines(
                symbol, Client.KLINE_INTERVAL_1DAY, start_date, end_date)
        elif timeframe == '15m':
            
            path= Path(klines_path+'{}_{}.csv'.format(symbol, timeframe))
            if not path.is_file():
                candlesticks = binance_client.get_historical_klines(
                    symbol, Client.KLINE_INTERVAL_15MINUTE, start_date, end_date)
            else:
                continue
        candlesticks_df = pd.DataFrame(candlesticks)
        candlesticks_df = manupulate_binance_klines(candlesticks_df)
        candlesticks_df = get_TWAP_price(candlesticks_df)
        candlesticks_df.to_csv(
            klines_path+'{}_{}.csv'.format(symbol, timeframe), index=False)
