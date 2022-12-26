# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 10:53:03 2022

@author: dvspe
Purpose: The purpose of this dashboard is to more easily implement stratgies
    from our Backtesting_V2 script. I am hoping that the fuctions from there 
    will easily transfer over to her to test. Eventually, This will all 
    interconnect in an object orientated way. For now, I am going to connect it
    to the Backtestin_v2.py script to run the function there

Required Packages:
    plotly
    dash
    pandas
    
Input:
    User interface to allow users to select a strategy and output the results
    This will have more user inputs to allow for robust backtesting capabilities.

Output:
    Dashboard plots and results for the user to review and modify in the dashboard
"""

#%% Get into correct file structure
import os
# should work ony any computer
path, filename = os.path.split(os.path.realpath(__file__))
# should got to Python_Trading AKA one directory up from current file's directory
os.chdir(path+"\..")
#%%
#import plotly express and dash
from dash import Dash, html, dcc
import plotly.express as px
from dash.dependencies import Input, Output
from flask_caching import Cache

#importing other packages used
import pandas as pd
import Binance.Backtesting_Strats_V2 as backtest
import time
from datetime import datetime
from datetime import timedelta
from datetime import date



#%% Set up the dashboard

app = Dash(__name__)

app.layout = html.Div(children=[
    #redirects to home flask app
    html.A('Cryptobot Home', href='http://localhost:5000'),

    #app header
    html.H1('Printing Money Backtesting Dashboard'),
    html.H3('Backtest your strats here'),
    
    #User inputs list
    # - end date (as a date picker)
    # - lookback (in number of hours number input)
    # - candel stick length (1m, 3m, 5m, 10m, 30m... dropdown list)
    # - curreny pair to look at (string input)
    # - strat name wanting to test (from dropdown of available)
    # - button to submit so it doesnt run until ready to test
    # -
    html.Br(),
    #Dropdowns in a line
    html.Div(children = [
        html.H5('Candel Stick timeframe'),
        dcc.Dropdown(['1m','3m','5m','10m','30m','1h','6h','1day'],'5m',id = 'candel_len_dd',
                     style = {'width':'100px', 'margin':'0 auto','display':'inline-block'}),
        
        html.H5('Strat'),
        dcc.Dropdown(['High_Low','Heiken_ema','Magic'],'High_Low',id = 'strat_select_dd',
                     style = {'width':'200px', 'margin':'0 auto','display':'inline-block'}),
        
        ], 
        style={'width':'300', 'height':'200px', 'display':'inline-block', 'vertical-align':'top', 'border':'1px solid black', 'padding':'20px'}),
    
    html.Br(),
    html.Br(),
    html.Br(),
   #datepicker for when your end date will be
   html.H5('Pick ending date'),
   dcc.DatePickerSingle(id = 'end_date_picker',
                        min_date_allowed = date(2000,1,1),
                        max_date_allowed = date.today(),
                        initial_visible_month = date.today(),
                        date = date.today()),
   html.Br(),
   html.Br(),
   #lookback in hours input and input currency pair to investigate. 
   html.H5('Input number of hours for lookback (In Hours)'),
   dcc.Input(id = 'hours_lookback_input',type = 'number',min = 1,max = 10000, placeholder=100,step = 1),
   html.H5('Input the currency pair to investigate in all caps'),
   dcc.Input(id = 'currency_pair_input',type = 'text'),
   
   html.Br(),
   #button to submit everything at once. 
   html.Br(),
   html.Br(),
   html.Button('Submit',id = 'submit_all')
   ],
style = {'text-align':'center','display':'inline-block','width':'100%'}
)

#%% Add in all the call backs here to update sections of the app. 


#%% Run the app and see results
if __name__ == '__main__':
    app.run_server( debug = True,
                    port=8051,
                    use_reloader=False)