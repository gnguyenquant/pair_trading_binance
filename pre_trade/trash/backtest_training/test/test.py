def get_data_lists(data_df:pd.DataFrame):
    data_df['price_chosen'] = np.exp(data_df['log_price_chosen'])
    data_df['price_compare'] = np.exp(data_df['log_price_compare'])
    time_series = data_df['Open Time'].tolist()
    price_chosen = data_df['price_chosen'].tolist()
    price_compare = data_df['price_compare'].tolist()
    zscore = data_df['z-score'].tolist()