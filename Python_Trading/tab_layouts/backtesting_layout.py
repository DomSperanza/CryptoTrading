from dash import html
from dash import dcc
from dash import dash_table

currency_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'XRP/USDT']
intervals = ['1m','5m','15m','30m','1h','6h','1d']
strategies = ['Heiken_EMA','Magic','Lazy_Bear','HighLow','HeikenStoch','Boom']

#make and modify my stats table
stats_table = dash_table.DataTable(
    id='stats_table_id',
    columns=[{'name': i, 'id': i} for i in ['profit_no_fee', 'profit_fee', 'winrate', 'num_of_trades','buyhold']],
    data=[],
    style_cell={'textAlign': 'center'}
)


layout = html.Div([
    html.H1('Backtesting', style={'textAlign': 'center'}),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id='symbol_id',
                options=[{'label': pair, 'value': pair.replace('/', '')} for pair in currency_pairs],
                value=currency_pairs[0].replace('/', '')
            ),
            style={'width': 'calc(33.33% - 8px)', 'marginRight': '8px'}
        ),
        html.Div(
            dcc.Dropdown(
                id='interval_id',
                options=[{'label':interval,'value':interval} for interval in intervals],
                value='30m'
            ),
            style={'width': 'calc(33.33% - 8px)', 'marginRight': '8px'}
        ),
        html.Div([
            html.Div('Lookback must be in hours', style={'fontSize': '12px'}),
            dcc.Input(
                id='lookback_id',
                type='number',
                value = 100
            )
        ], style={'width': 'calc(33.33% - 8px)'})
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    html.Div([
        html.Button('Start', id='start-button',style={'width':'100px','height':'50px'}),
        html.Button('Clear', id='clear-button',style={'width':'100px','height':'50px'})
    ], style={'display':'flex','justifyContent':'center','padding':'20px','gap':'20px'}),
    html.Div(id='output-div',style={'textAlign':'center'}),
    dcc.Store(id='get_data_id'),
    html.Div(
        dcc.Dropdown(
            id='trading_strat_id',
            options=[{'label':strat,'value':strat} for strat in strategies],
            value=strategies[0]
        ),
        style={'width': 'calc(33.33% - 8px)', 'margin': '0 auto'}
    ),
    html.Div(
        html.Button('Test_Strat', id='test_button_id', style={'width': '100px', 'height': '50px'}),
        style={'textAlign': 'center', 'paddingTop': '20px', 'marginBottom': '20px'}
    ),
    html.Div(stats_table, style={'width': '50%', 'margin': '0 auto'})
    
])
