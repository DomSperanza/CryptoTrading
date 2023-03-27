from dash import html
from dash import dcc

layout = html.Div([
    html.H1('TradingBot', style={'textAlign': 'center'}),
    html.Div([
        html.Div(
            dcc.Dropdown(
                id='dropdown-1',
                options=[
                    {'label': 'Option 1', 'value': '1'},
                    {'label': 'Option 2', 'value': '2'},
                    {'label': 'Option 3', 'value': '3'}
                ],
                value='1'
            ),
            style={'width': 'calc(33.33% - 8px)', 'marginRight': '8px'}
        ),
        html.Div(
            dcc.Dropdown(
                id='dropdown-2',
                options=[
                    {'label': 'Option A', 'value': 'A'},
                    {'label': 'Option B', 'value': 'B'},
                    {'label': 'Option C', 'value': 'C'}
                ],
                value='A'
            ),
            style={'width': 'calc(33.33% - 8px)', 'marginRight': '8px'}
        ),
        html.Div(
            dcc.Dropdown(
                id='dropdown-3',
                options=[
                    {'label': 'Choice X', 'value': 'X'},
                    {'label': 'Choice Y', 'value': 'Y'},
                    {'label': 'Choice Z', 'value': 'Z'}
                ],
                value='X'
            ),
            style={'width': 'calc(33.33% - 8px)'}
        )
    ], style={'display': 'flex', 'justifyContent': 'space-between'})
])
