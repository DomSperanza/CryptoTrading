import plotly
import plotly.graph_objs as go
import pandas as pd
# import plotly.io as pio

# pio.renderers.default = "notebook_connected"
df = pd.read_csv('https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-andamento-nazionale/dpc-covid19-ita-andamento-nazionale.csv')
# Create a trace
data = [go.Scatter(
    x = df['data'],
    y = df['totale_positivi'],
)]
layout = go.Layout(
        xaxis=dict(
            title='Data',    
        ),
        yaxis=dict(
            title='Totale positivi',  
        )
    )
fig = go.Figure(data=data, layout=layout)

plotly.offline.plot(fig,filename='positives.html',config={'displayModeBar': False})