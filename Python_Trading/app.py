#import plotly express and dash
import dash
from dash import Dash, html, dcc,dash_table
import plotly.express as px
from dash.dependencies import Input, Output, State
from flask_caching import Cache

#connect to the correct directory before running anything else
import os
path, filename = os.path.split(os.path.realpath(__file__))
# should got to Python_Trading AKA one directory up from current file's directory
os.chdir(path)

#importing other packages used
import pandas as pd
#import Binance.Backtesting_Strats_V2 as backtest
import time
from datetime import datetime
from datetime import timedelta
from datetime import date

#import the layouts
from tab_layouts import backtesting_layout, tradingbot_layout

#imports from backtesting
#from backtesting.Backtesting_Strats_V2 import *

#import the cryptobot
from cryptobot.cryptobot import CryptoBot
import strategies as st
import brokers as br



#%% Set up the dashboard

app = Dash(__name__)

app.layout = html.Div([
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Backtesting', value='tab-1'),
        dcc.Tab(label='Trading Bot', value='tab-2'),
    ]),
    html.Div(id='tabs-content',children=backtesting_layout.layout)
])


##################### Put all Callbacks here #######################
#%% Add in all the call backs here to update sections of the app. 
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return backtesting_layout.layout
    elif tab == 'tab-2':
        return tradingbot_layout.layout
    else:
        # Set the default value to the layout of the Backtesting tab
        return backtesting_layout.layout

@app.callback(
    [Output('output-div', 'children'),Output('get_data_id','data')],
    Input('start-button', 'n_clicks'),
    Input('clear-button', 'n_clicks'),
    State('symbol_id', 'value'),
    State('interval_id', 'value'),
    State('lookback_id', 'value')
)
def get_data(start_button_clicks, clear_button_clicks, symbol_value, interval_value, lookback_value):
    ctx = dash.callback_context
    if not ctx.triggered:
        # No button has been clicked yet
        return '', None
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == 'start-button':
            # Perform some action using the values from the inputs
            #df = getdata(symbol = symbol_value,interval = interval_value,lookback = str(lookback_value))
            broker = br.Binance
            bot = CryptoBot(symbol_value,broker)
            df = bot.get_test_data(interval = interval_value, lookback = str(lookback_value))
            df = df.reset_index()
            df['Time'] = df['Time'].apply(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'))
            return f'Selected values: {symbol_value}, {interval_value}, {lookback_value}', df.to_dict(orient = 'records')

        elif button_id == 'clear-button':
            # Clear the output
            return '',None

#gets the dataframe data and the trading strat and output
#a table of information that displays the results. 
@app.callback(
    [Output('stats_table_id', 'data'), Output('plotly_trade_id', 'figure')],
    [Input('test_button_id', 'n_clicks')],
    [State('get_data_id', 'data'), State('trading_strat_id', 'value'), State('symbol_id', 'value')]
)
def test_strategy(test_button_clicks, data, trading_strat_value,symbol_value):
    if test_button_clicks:
        #read the stored data
        df = pd.DataFrame.from_dict(data)
        df['Time'] = pd.to_datetime(df['Time'])
        df = df.set_index('Time')

        #make another instance of the cryptobot
        strat = getattr(st,trading_strat_value)
        broker=br.Binance
        bot = CryptoBot(symbol = symbol_value, broker_class = broker, strategy_class = strat)
        bot.strategy.df = df
        bot.test_strat()
        bot.strategy.symbol = symbol_value
        #pull out the stats
        stats = bot.strategy.trades_stats()
        
        #get plotly fig
        fig = bot.strategy.plot_visual_plotly()
        
        return [stats],fig
    return [],{}





######################End of Callbacks###############################

#%% Run the app and see results
if __name__ == '__main__':
    app.run_server( debug = True)
