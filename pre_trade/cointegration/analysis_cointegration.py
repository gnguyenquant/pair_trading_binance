# %%
import pandas as pd
from PIL import Image

# %%
data_path='../../data/'
cointegration_path=data_path+'cointegration/'
klines_path=data_path+'klines/'
figures_path=cointegration_path+'figures/'

# %%
layer1_1h_df=pd.read_csv(cointegration_path+'tables/layer1_1h.csv')
layer1_2h_df=pd.read_csv(cointegration_path+'tables/layer1_2h.csv')
layer1_1d_df=pd.read_csv(cointegration_path+'tables/layer1_1d.csv')
layer1_15m_df=pd.read_csv(cointegration_path+'tables/layer1_15m.csv')

# %%
layer1_1h_df
print(layer1_1h_df)
# %%
chosen_symbol='DOTUSDT'
compare_symbol='NEARUSDT'
timeframe='1h'
fig=Image.open('{}{}_{}_{}.png'.format(figures_path,chosen_symbol,compare_symbol,timeframe))
fig.show()

# %%
layer1_2h_df
#print(layer1_2h_df)
