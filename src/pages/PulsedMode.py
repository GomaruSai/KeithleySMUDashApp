#Pulsed mode

import dash
import plotly.graph_objects as go # or plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, callback
#from dash.dependencies import Input, Output
import os
import os.path
import pyvisa as visa
import numpy as np
import datetime
import time as timec

def plot(df, r_state):
    pm_x = df['Time [s]'].to_numpy()
    pm_y_v = df['Voltage [V]'].to_numpy()
    pm_y_r = df['Resistance [Ohm]'].to_numpy()
    
    #figure = go.Figure()

    # Create figure with secondary y-axis
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    
    figure.add_trace(go.Scatter(
        x=pm_x,
        y=pm_y_v,
        name='Voltage [V]',
        line=dict(color='blue')
        ),
        secondary_y=False
    )
    figure.add_trace(go.Scatter(
        x=pm_x,
        y=pm_y_r,
        name='Resistance [Ohm]',
        line=dict(color='red')
        ),
        secondary_y=True
    )
    figure.update_layout(title=f'Pulsed Mode Measurement. Last idx: {len(df)}')

    # Set x-axis title
    figure.update_xaxes(title_text="Time")

    # Set y-axes titles
    figure.update_yaxes(
        title_text="Voltage [V]", 
        secondary_y=False)

    figure.update_yaxes(
        title_text="Resistance [Ohm]", 
        secondary_y=True)

    return figure
    
def layout(param):
    return html.Div([
        dcc.Graph(
            id='pm-fig',
    #       figure=fig
        ),
        dcc.Interval(
            id='int-comp-pm',
            interval=1*1000,
            n_intervals=0,
            #max_intervals=-1,
            disabled = False
        ),
        dcc.RadioItems(id='radio-button-pm', options=[{'label':'Applied Gate Voltage', 'value':'1'}, {'label':'Floating Gate', 'value':'0'}], value='0', inline=True),
        html.Div(html.Button(children='Start', id='PM-button', n_clicks=0), style={'width': '81%', 'display': 'inline-block'}),
        html.Div(children="Instrument Address: ", id='addre', style={'width': '20%', 'display': 'inline-block'}),
        html.Div(children=param[0], id='addr', style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            html.Div(children="Applied Voltage [V]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='PM-V_APP', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(children="Current HI [A]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='PM-I_HI', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(children="Current LO [A]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='PM-I_LO', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(children="Interval [s]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='PM-INTERVAL', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(children="Pulse Duration [s]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='PM-DURATION', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(children="Total Measurement Time [s]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='PM-TIME', type='number', disabled=False)
        ]),
        dcc.Store(id='t2'),
        dcc.Store(id='t3')
    ])

@callback(
    Output('pm-fig', 'figure'),
    Output('int-comp-pm', 'interval'),
    Output('int-comp-pm', 'disabled'),
    Output('PM-V_APP', 'disabled'),
    Output('PM-I_HI', 'disabled'),
    Output('PM-I_LO', 'disabled'),
    Output('PM-TIME', 'disabled'),
    Output('PM-INTERVAL', 'disabled'),
    Output('PM-DURATION', 'disabled'),
    Output('t2', 'data'),
    Output('t3', 'data'),
    [Output('PM-button', 'children'),
    Output('PM-button', 'disabled'),
    Input('PM-button', 'n_clicks'),
    Input('PM-button', 'children')],
    Input('addr', 'children'),
    Input('PM-V_APP', 'value'),
    Input('PM-I_HI', 'value'),
    Input('PM-I_LO', 'value'),
    Input('PM-TIME', 'value'),
    Input('PM-INTERVAL', 'value'),
    Input('PM-DURATION', 'value'),
    Input('int-comp-pm', 'n_intervals'),
    Input('int-comp-pm', 'disabled'),
    Input('radio-button-pm', 'value'),
    Input('int-comp-pm', 'interval'),
    Input('t2', 'data'),
    Input('t3', 'data')
)
def PulsedMode(button_clicks, button_text, address, V_app, I_hi, I_lo, time, interval, duration, ni, flag, radio_state, int_comp, t2, t3):
    samples = 1
    PM_button_state = False
    if button_clicks == 0:
        inter = interval
        states = False
        if radio_state == '0':
            PM_V_state = True
        else:
            PM_V_state = False
        t2 = 0
        t3 = 0
    else:
        states = True
        PM_V_state = True
        interval = 1000 * interval
        duration = 1000 * duration
        time = 1000 * time
        if radio_state == '0':
            V_app = "N/A"
    if button_clicks % 2 == 1:
        t0 = timec.time()
        flag = False
        if ni * interval <= time + interval:
            inter = interval
            rm = visa.highlevel.ResourceManager()
            print(address)
            inst = rm.open_resource(address)
            #inst.timeout = 25000

            if ni == 0:
                inst.write("beeper.enable = beeper.ON")
                inst.write("beeper.beep(1,100)")
                inst.write("beeper.enable = beeper.OFF")
                
                inst.write("smub.reset()\n")

                #start
                inst.write("smub.source.func = smub.OUTPUT_DCAMPS")
                inst.write("smub.source.rangev = 20")
                inst.write("smub.source.limiti = 10e-3")
                
                inst.write("smub.measure.rangev = 20")
                inst.write("smub.nvbuffer1.clear()")
                inst.write("smub.nvbuffer2.clear()")
                #inst.write("smub.nvbuffer1.appendmode = 1")

                #inst.write("smub.source.autorange = smub.ON")
                #inst.write("smub.source.autodelay = smub.ON")
                #inst.write("smub.measure.nplc = samples / duration")
                #inst.write("smub.measure.interval = duration / samples")

                inst.write("localnode.smub.source.output = localnode.smub.OUTPUT_ON")
            
                if radio_state == '1':
                    inst.write("localnode.smua.reset()\n")
                
                    #start
                    inst.write("localnode.smua.source.func = localnode.smua.OUTPUT_DCVOLTS")
                    inst.write("localnode.smua.source.rangev = 20")
                    
                    inst.write("localnode.smua.source.limiti = 1e-7")
                    inst.write("localnode.smua.measure.rangev = 20")
                    inst.write("localnode.smua.nvbuffer1.clear()")
                    
                    inst.write("localnode.smua.source.output = localnode.smua.OUTPUT_ON")

                    inst.write("smua.source.levelv = " + str(V_app))                
            
                d = datetime.datetime.now()
                print(d)
                date = str(d).replace(":", "_")
                filename = "Pulsed_Mode_Measurement_" + date + ".csv"
                localnode_file = open(os.path.dirname(__file__)  + '/../dat/PM/' + filename, "a")
                localnode_file.write("Applied Voltage = " + str(V_app) + "V" + ", Current HI = " + str(I_hi) + "A" + ", Current LO = " + str(I_lo) + "A" + ", Interval = " + str(interval / 1000) + "s, Pulse Duration = " + str(duration /1000) + "s, Measurement Time = " + str(time) + "s \n")
                localnode_file.write("Time [s],Voltage [V],Resistance [Ohm]\n")
                localnode_file.close()
                file = open(os.path.dirname(__file__)  + '/../dat/PM/test.txt', "w")
                file.write(filename)
                file.close()
                print("Setup Successful")
                #inst.write("localnode.smub.source.leveli = " + str(I_lo))
                t2 = 0
                t3 = 0
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/PM/' + filename, usecols = ['Time [s]', 'Voltage [V]', 'Resistance [Ohm]'], skiprows = 1).copy()
                figure = plot(df, radio_state)
                button_text = 'Pause'
            else:
                file = open(os.path.dirname(__file__)  + '/../dat/PM/test.txt', "r")
                filename = file.read()
                file.close()
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/PM/' + filename, usecols = ['Time [s]', 'Voltage [V]', 'Resistance [Ohm]'], skiprows = 1).copy()
                
                inst.write("localnode.smub.source.leveli = " + str(I_hi))
                
                V_sd = 0
                R_sd = 0
                for i in range(0, samples):
                    print(f"t3 = {t3}")
                    t3 = (duration / (1000 * samples)) - t3
                    if t3 > 0:
                        timec.sleep(t3)
                    t3 = timec.time()
                    V_sd = V_sd + (float(inst.query("print(smub.measure.v(smub.nvbuffer1))").replace("\n", "")) / samples)
                    R_sd = R_sd + (float(inst.query("print(smub.measure.r(smub.nvbuffer2))").replace("\n", "")) / samples)
                    inst.write("smub.nvbuffer1.clear()")
                    inst.write("smub.nvbuffer2.clear()")
                    t3 = timec.time() - t3

                #print(f'n_interval = {ni}')
                inst.write("localnode.smub.source.leveli = " + str(I_lo))

                #timec.sleep(((interval - duration) / 1000) - (timec.time() - t0) - t2)

                t2 = timec.time()            
            
                localnode_file = open(os.path.dirname(__file__)  + '/../dat/PM/' + filename, "a")
                localnode_file.write(str(datetime.datetime.now()).split(' ')[-1][:-4] + "," + str(V_sd) + ',' + str(R_sd) + "\n")
                localnode_file.close()
            
                figure = plot(df, radio_state)
                button_text = 'Pause'
        else:
            inter = interval
            file = open(os.path.dirname(__file__)  + '/../dat/PM/test.txt', "r")
            filename = file.read()
            file.close()
            
            df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/PM/' + filename, usecols = ['Time [s]', 'Voltage [V]', 'Resistance [Ohm]'], skiprows = 1).copy()
            
            rm = visa.highlevel.ResourceManager()
            inst = rm.open_resource(address)
            
            inst.write("localnode.smub.source.output = localnode.smub.OUTPUT_OFF")
            #inst.write("localnode.smua.source.output = localnode.smua.OUTPUT_OFF")
            
            inst.write("localnode.beeper.enable = beeper.ON\n")
            inst.write("localnode.beeper.beep(1,500)\n")
            inst.write("localnode.beeper.enable = beeper.OFF\n")
            
            inst.close()
            #max_int = 0
            flag = True
            
            figure = plot(df, radio_state)
            print("Complete")
            print(datetime.datetime.now())
            PM_button_state = True
            button_text = "Complete! Saved in dat/PM/. To restart, refresh the page."
        #timec.sleep(interval - (timec.time() - t))
        
    else:
        inter = interval
        file = open(os.path.dirname(__file__)  + '/../dat/PM/test.txt', "r")
        filename = file.read()
        file.close()
            
        df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/PM/' + filename, usecols = ['Time [s]', 'Voltage [V]', 'Resistance [Ohm]'], skiprows = 1).copy()
        
        figure = plot(df, radio_state)
        flag = True
        button_text = 'Start'

    #inter = inter * 1000
    print("button_clicks = " + str(button_clicks))
    #print("interval = " + str(inter))
    print("interval = " + str(int_comp))
    return figure, inter, flag, PM_V_state, states, states, states, states, states, timec.time() - t2, t3, button_text, PM_button_state