# -*- coding: utf-8 -*-
"""
Created on Sun May 22 11:19:14 2022

@author: dvspe

Purpose: The purpose of this script is to define functions that can be called upon
for other scripts when developing the crypto trading algorithms.


Packages needed: cbpro, pandas, plotly


"""

#make a function to determine my pretend market value
#inputs are the current cash value you have, along with all unique types of coins.
#It will find the current market value of the coins and add that to the cash value. 

def Current_Total_Value (cash, number_of_BTC =0, numbe_of_doge = 0):
    import cbpro as cb
    import pandas as pd
    if number_of_BTC>0:
        pc = cb.PublicClient()
        BTC_df = pd.DataFrame.from_dict(pc.get_product_ticker('BTC-USD'),orient = 'index')
        Total = cash+float(BTC_df.loc['price'][0])*number_of_BTC
    else:
        Total = cash
    return Total


def Make_historic_plots(Currency,time_gaps = 300):    
    import cbpro as cb
    import pandas as pd
    import plotly.graph_objects as go
    from plotly.offline import plot
    pc = cb.PublicClient()
    historical = pd.DataFrame(pc.get_product_historic_rates(product_id = Currency, granularity=time_gaps))
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
    return(plot(fig,auto_open = True))

    