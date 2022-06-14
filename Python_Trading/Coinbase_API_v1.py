# -*- coding: utf-8 -*-
"""
Created on Sat May 21 09:20:34 2022

@author: dvspe
"""

import cbpro
import pandas as pd
import time
import plotly.graph_objects as go
import plotly.io as pio



public_client = cbpro.PublicClient()

result = public_client.get_products()
result_time = public_client.get_time()

for row in result:
    print(row['id'])

print(result_time)

df = pd.DataFrame(result)
US_df = df[df['quote_currency']=='USD']
US_df_sorted = US_df.sort_values('id')


# for ids in US_df['id']:
#     print(ids)
#     print(public_client.get_product_historic_rates(ids))

public_client.get_product_24hr_stats('BTC-USD')


#%%
#get historical data for one of the coins
historical = pd.DataFrame(public_client.get_product_historic_rates('BTC-USD'))
historical.columns= ["Date","Open","High","Low","Close","Volume"]
historical['Date'] = pd.to_datetime(historical['Date'],unit = 's')
historical.set_index('Date', inplace=True)
historical.sort_values(by='Date', ascending=True, inplace=True)
historical['20 SMA'] = historical['Close'].rolling(20).mean()

fig = go.Figure(data=[go.Candlestick(x = historical.index,
                                    open = historical['Open'],
                                    high = historical['High'],
                                    low = historical['Low'],
                                    close = historical['Close'],
                                    ),
                     go.Scatter(x=historical.index, y=historical['20 SMA'], line=dict(color='purple', width=1))])


fig.show()
pio.renderers.default='svg'
    
    