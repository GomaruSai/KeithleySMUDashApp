import dash
from dash import Dash, dcc, html, Input, Output, State, callback, ctx
#import os
import pyvisa as visa
from flask import request

#dash.register_page(__name__, path='/')

rm = visa.highlevel.ResourceManager()
instruments_available = rm.list_resources()

layout = html.Div([
    html.H1(children="Welcome to Sai's FET Characterisation Software for KEITHLEY SourceMeters!"),
    dcc.Dropdown(id='instruments-dropdown', options=instruments_available, multi=True, placeholder='Select an instrument to connect to'),
    html.Button('Connect', id='connect-button'),
    html.Div(id='status-messages',children=[]),
    html.Div(id='instrument-setup-div', children=[]),
    dcc.Interval(
        id='interval-comp',
        interval=1*1000,
        n_intervals=0,
        #max_intervals=-1,
        disabled = False
    ),
    html.Button('Quit', id = 'quit-button', n_clicks=0)
])

def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@callback(
    Output('instrument-setup-div', 'children'),
    Output('instruments-dropdown', 'options'),
    Output('status-messages', 'children'),
    Input('connect-button', 'n_clicks'),
    Input('quit-button', 'n_clicks'),
    [State('instruments-dropdown', 'value')],
    [State('instrument-setup-div', 'children')],   
    [State('status-messages', 'children')]
)
def update_layout(connect_button_clicks, quit_button_clicks, instruments_available_value, instruments, stats):
    rm = visa.highlevel.ResourceManager()
    instruments_available = rm.list_resources()
    print(instruments_available)

    instruments = []
    stats = []

    if quit_button_clicks != 0:
        shutdown()

    if instruments_available_value is not None:
        for i, inst in enumerate(instruments_available_value):
            if connect_button_clicks > 0:
                ins = rm.open_resource(inst)
                stats.append(html.Div(str(i) + '. ' + ins.query('*IDN?') + 'is connected at ' + inst + '!'))

            instruments.append(
                html.Div([
                    html.Div([f'What measurement do you want to perform with instrument {i}?']),
                    html.Div(
                        dcc.Link(
                            "Constant Current Measurement", href=f"/ConstantCurrent?address={inst}", target="_blank"
                        )
                    ),
                    html.Div(
                        dcc.Link(
                            "I-V Characteristics Measurement", href=f"/IV?address={inst}", target="_blank"
                        )
                    ),
                    html.Div(
                        dcc.Link(
                            "Pulsed Mode Measurement", href=f"/PulsedMode?address={inst}", target="_blank"
                        )
                    )
                ])
            )
    return instruments, instruments_available, stats