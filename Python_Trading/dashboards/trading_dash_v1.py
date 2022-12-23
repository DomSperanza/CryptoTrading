# -*- coding: utf-8 -*-
"""
Created on Wed Dec 21 10:12:00 2022

@author: dvspe
Purpose: 
    This is an initial hack at trying to figure out how to incoperate
    a plotly Dashboard into the app to allow users to toggle an on and off 
    switch. Start small build up

Required Packages: 
    plotly
    dash
    pandas
    
Input: 
    allow for user input to turn the bot on and off
Output: 
    a trading bot that will turn on and off. Display what is being traded
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
import Functions.Binance_Functions_v3 as func
from time import sleep

#%% App constuction
#initally will be pretty basic to allow just a handful of bottons

app = Dash(__name__)

#Make a Cashe to implement the on off switch
cache = Cache(app.server, config={
    'CACHE_TYPE': 'simple',

    # should be equal to maximum number of users on the app at a single time
    # higher numbers will store more data in the filesystem / redis cache
    'CACHE_THRESHOLD': 100
})


app.layout = html.Div(children=[
    
    #app header
    html.H1('Printing Money Dashbaord'),
    html.H3('Turn your bot on and off. Make money.'),
    
    #make the on/off buttons
    html.Div(dcc.RadioItems(
        ['On','Off'],
        'Off',
        labelStyle={'display':'block'},
        id = 'on_off_button'
        )),
    html.H3('Trading bot is Off',id = 'you_are_trading')

], style = {'text-align':'center','display':'inline-block','width':'100%'}
)


#%%Functions to allow to update while in an infinite loop.
#This is the url to the code i used to make changes to the button with flask. 
#never done anything with flask but it seems to work as intented!
#https://community.plotly.com/t/can-you-break-out-of-a-while-loop-based-on-the-state-of-booleanswitch/41473/3

def global_store(switch_state=None):
    if switch_state is not None:
        cache.set("switch-state",switch_state)
        return 'Off'
    else:
        switch_state = cache.get("switch-state")
        return switch_state

def dummy_test(state):
    while state=='On':
        print(f'The Tradingbot is {state}')
        sleep(2)
        state = global_store()  # here I'm getting the boolean switch state (this is an alternative to using global variables)
        if state=='Off':
            break


#%% function to turn off and on the trading bot. 
@app.callback(
    Output('you_are_trading','children'),
    Input('on_off_button','value'))
def On_Off(my_select):
    global_store(my_select)
    if my_select=='On':
        dummy_test('On')
    return None


#%% Run the app and see results
if __name__ == '__main__':
    app.run_server(debug = True,use_reloader=False)
