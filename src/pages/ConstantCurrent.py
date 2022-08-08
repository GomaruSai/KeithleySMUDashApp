#Constant Current

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

#dash.register_page(__name__,title='Constant Current Measurement')

def plot(df, r_state):
    cc_x = df['Time [s]'].to_numpy()
    cc_y_s = df['Source Voltage [V]'].to_numpy()
    cc_y_g = df['Gate Current [A]'].to_numpy()
    
    #figure = go.Figure()

    # Create figure with secondary y-axis
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    
    figure.add_trace(go.Scatter(
        x=cc_x,
        y=cc_y_s,
        name='Source Voltage [V]',
        line=dict(color='blue')
        ),
        secondary_y=False
    )
    figure.add_trace(go.Scatter(
        x=cc_x,
        y=cc_y_g,
        name='Gate Current [A]',
        line=dict(color='red')
        ),
        secondary_y=True
    )
    if r_state == '0':
        cc_y_g_v = df['Gate Voltage [V]'].to_numpy()
        figure.add_trace(go.Scatter(
            x=cc_x,
            y=cc_y_g_v,
            name='Gate Voltage [V]',
            line=dict(color='green')
            ),
            secondary_y=True
        )

    figure.update_layout(title=f'Constant Current Measurement. Last idx: {len(df)}')

    # Set x-axis title
    figure.update_xaxes(title_text="Time [s]")

    # Set y-axes titles
    figure.update_yaxes(
        title_text="Source", 
        secondary_y=False)

    figure.update_yaxes(
        title_text="Gate", 
        secondary_y=True)

    return figure
    
def layout(param):
    return html.Div([
        dcc.Graph(
            id='cc-fig',
    #        figure=fig
            ),
        dcc.Interval(
            id='int-comp-cc',
            interval=1*1000,
            n_intervals=0,
            #max_intervals=-1,
            disabled = False
        ),
        dcc.RadioItems(id='radio-button-cc', options=[{'label':'Applied Gate Voltage', 'value':'1'}, {'label':'Floating Gate', 'value':'0'}], value='1', inline=True),
        html.Div(html.Button(children='Start', id='CC-button', n_clicks=0, disabled=False), style={'width': '81%', 'display': 'inline-block'}),
        html.Div(children="Instrument Address: ", id='addre', style={'width': '20%', 'display': 'inline-block'}),
        html.Div(children=param[0], id='addr', style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            html.Div(children="Gate Voltage [V]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='CC-V_GATE', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(children="Source Current [A]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='CC-I_SOURCE', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(children="Total Measurement Time [s]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='CC-TIME', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(children="Interval [s]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='CC-INTERVAL', type='number', disabled=False)
        ]),
        dcc.Store(id='btn-clicks')
    ])

@callback(
    Output('cc-fig', 'figure'),
    Output('int-comp-cc', 'interval'),
    Output('int-comp-cc', 'disabled'),
    Output('CC-V_GATE', 'disabled'),
    Output('CC-I_SOURCE', 'disabled'),
    Output('CC-TIME', 'disabled'),
    Output('CC-INTERVAL', 'disabled'),
    [Output('CC-button', 'children'),
    Output('CC-button', 'disabled'),
    Input('CC-button', 'n_clicks'),
    Input('CC-button', 'children')],
    Input('addr', 'children'),
    Input('CC-V_GATE', 'value'),
    Input('CC-I_SOURCE', 'value'),
    Input('CC-TIME', 'value'),
    Input('CC-INTERVAL', 'value'),
    Input('int-comp-cc', 'n_intervals'),
    Input('int-comp-cc', 'disabled'),
    Input('radio-button-cc', 'value')
)
def ConstantCurrent(button_clicks, button_text, address, V_g, I_s, time, interval, ni, flag, radio_state):
    CC_button_state = False
    states = False
    if button_clicks == 0:
        if radio_state == '0':
            CC_V_state = True
        else:
            CC_V_state = False
    else:
        CC_V_state = True
        states = True
    if radio_state == '1':
        if button_clicks % 2 == 1:
            #t = timec.time()
            flag = False
            if ni * interval < time:
                btn_clicks = 0
                rm = visa.highlevel.ResourceManager()
                print(address)
                inst = rm.open_resource(address)
                if ni == 0:
                    inst.write("localnode.beeper.enable = beeper.ON\n")
                    inst.write("localnode.beeper.beep(1,100)\n")
                    inst.write("localnode.beeper.enable = beeper.OFF\n")
                    
                    inst.write("localnode.smub.reset()\n")
                    
                    #start
                    inst.write("localnode.smub.source.func = localnode.smub.OUTPUT_DCAMPS")
                    inst.write("localnode.smub.source.rangev = 20")
                    inst.write("localnode.smub.source.limiti = 10e-3")
                    
                    inst.write("localnode.smub.measure.rangev = 20")
                    inst.write("localnode.smub.nvbuffer1.clear()")
                    
                    #localnode.smu-A
                    inst.write("localnode.smua.reset()\n")
                    
                    #start
                    inst.write("localnode.smua.source.func = localnode.smua.OUTPUT_DCVOLTS")
                    inst.write("localnode.smua.source.rangev = 20")
                    
                    inst.write("localnode.smua.source.limiti = 10e-3")
                    inst.write("localnode.smua.measure.rangei = 10e-3")
                    inst.write("localnode.smua.nvbuffer1.clear()")
                    
                    inst.write("localnode.smub.source.output = localnode.smub.OUTPUT_ON\n")
                    inst.write("localnode.smua.source.output = localnode.smua.OUTPUT_ON\n")

                    d = datetime.datetime.now()
                    date = str(d).replace(":", "_")
                    filename = "Const_Curr_Measurement_" + date + ".csv"
                    localnode_file = open(os.path.dirname(__file__)  + '/../dat/CC/' + filename, "a")
                    localnode_file.write("Source Current = " + str(I_s) + "A" + ", Gate Voltage = " + str(V_g) + "V" + ", Measurement Time = " + str(time) + "s" + ", Measurement interval = " + str(interval) + "s \n")
                    localnode_file.write("Time [s],Source Voltage [V],Gate Current [A],Gate Voltage [V]\n")
                    localnode_file.close()
                    file = open(os.path.dirname(__file__)  + '/../dat/CC/test.txt', "w")
                    file.write(filename)
                    file.close()
                    print("Setup Successful")
                file = open(os.path.dirname(__file__)  + '/../dat/CC/test.txt', "r")
                filename = file.read()
                file.close()
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/CC/' + filename, usecols = ['Time [s]', 'Source Voltage [V]', 'Gate Current [A]'], skiprows = 1).copy()
                
                inst.write("localnode.smub.source.leveli = " + str(I_s))
                inst.write("localnode.smua.source.levelv = " + str(V_g))
                
                I_GATE = inst.query("print(localnode.smua.measure.i(localnode.smua.nvbuffer1))")
                V_SOURCE = inst.query("print(localnode.smub.measure.v(localnode.smub.nvbuffer1))")
                
                I_g = float(I_GATE.replace("\n", ""))
                V_s = float(V_SOURCE.replace("\n", ""))
                
                localnode_file = open(os.path.dirname(__file__)  + '/../dat/CC/' + filename, "a")
                localnode_file.write(str(ni * interval) + "," + str(V_s) + "," + str(I_g) + "," + str(V_g) + "\n")
                localnode_file.close()
                    
                figure = plot(df, radio_state)
                
                button_text = 'Pause'

            else:
                file = open(os.path.dirname(__file__)  + '/../dat/CC/test.txt', "r")
                filename = file.read()
                file.close()
                
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/CC/' + filename, usecols = ['Time [s]', 'Source Voltage [V]', 'Gate Current [A]'], skiprows = 1).copy()
                
                rm = visa.highlevel.ResourceManager()
                inst = rm.open_resource(address)
                
                inst.write("localnode.smub.source.output = localnode.smub.OUTPUT_OFF")
                inst.write("localnode.smua.source.output = localnode.smua.OUTPUT_OFF")
                
                inst.write("localnode.beeper.enable = beeper.ON\n")
                inst.write("localnode.beeper.beep(1,500)\n")
                inst.write("localnode.beeper.enable = beeper.OFF\n")
                
                inst.close()
                #max_int = 0
                flag = True
                
                figure = plot(df, radio_state)
                
                button_text = "Complete! Saved in dat/CC/. To restart, refresh the page."
                CC_button_state = True
            #timec.sleep(interval - (timec.time() - t))
            interval = interval * 1000
        else:
            file = open(os.path.dirname(__file__)  + '/../dat/CC/test.txt', "r")
            filename = file.read()
            file.close()
                
            df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/CC/' + filename, usecols = ['Time [s]', 'Source Voltage [V]', 'Gate Current [A]'], skiprows = 1).copy()
            
            figure = plot(df, radio_state)
            btn_clicks = 0
            flag = True
            #max_int = 0
            button_text = 'Start'# Constant Current Measurement'
            
    elif radio_state == '0':
        if button_clicks % 2 == 1:
            #t = timec.time()
            flag = False
            if ni * interval < time:
                btn_clicks = 0
                rm = visa.highlevel.ResourceManager()
                inst = rm.open_resource(address)
                if ni == 0:
                    inst.write("localnode.beeper.enable = beeper.ON\n")
                    inst.write("localnode.beeper.beep(1,100)\n")
                    inst.write("localnode.beeper.enable = beeper.OFF\n")
                    
                    inst.write("localnode.smub.reset()\n")
                    
                    #start
                    inst.write("localnode.smub.source.func = localnode.smub.OUTPUT_DCAMPS")
                    inst.write("localnode.smub.source.rangev = 20")
                    inst.write("localnode.smub.source.limiti = 10e-3")
                    
                    inst.write("localnode.smub.measure.rangev = 20")
                    inst.write("localnode.smub.nvbuffer1.clear()")
                    
                    #localnode.smu-A
                    inst.write("localnode.smua.reset()\n")
                    
                    #start
                    #inst.write("localnode.smua.source.func = localnode.smua.OUTPUT_DCVOLTS")
                    #inst.write("localnode.smua.source.rangev = 20")
                    
                    #inst.write("localnode.smua.source.limiti = 10e-3")
                    inst.write("localnode.smua.measure.rangei = 10e-3")
                    inst.write("localnode.smua.measure.rangev = 20")
                    inst.write("localnode.smua.nvbuffer1.clear()")
                    inst.write("localnode.smua.nvbuffer2.clear()")
                    
                    inst.write("localnode.smub.source.output = localnode.smub.OUTPUT_ON\n")
                    inst.write("localnode.smua.source.output = localnode.smua.OUTPUT_ON\n")

                    d = datetime.datetime.now()
                    date = str(d).replace(":", "_")
                    filename = "Const_Curr_Measurement_FloatingGate_" + date + ".csv"
                    localnode_file = open(os.path.dirname(__file__)  + '/../dat/CC/' + filename, "a")
                    localnode_file.write("Source Current = " + str(I_s) + "A" +", Measurement Time = " + str(time) + "s" + ", Measurement interval = " + str(interval) + "s \n")
                    localnode_file.write("Time [s],Source Voltage [V],Gate Current [A],Gate Voltage [V]\n")
                    localnode_file.close()
                    file = open(os.path.dirname(__file__)  + '/../dat/CC/test.txt', "w")
                    file.write(filename)
                    file.close()
                    print("Setup Successful")
                file = open(os.path.dirname(__file__)  + '/../dat/CC/test.txt', "r")
                filename = file.read()
                file.close()
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/CC/' + filename, usecols = ['Time [s]', 'Source Voltage [V]', 'Gate Current [A]', 'Gate Voltage [V]'], skiprows = 1).copy()
            
                inst.write("localnode.smub.source.leveli = " + str(I_s))
                #inst.write("localnode.smua.source.levelv = " + str(V_g))
                
                I_GATE = inst.query("print(localnode.smua.measure.i(localnode.smua.nvbuffer1))")
                V_GATE = inst.query("print(localnode.smua.measure.v(localnode.smua.nvbuffer2))")
                V_SOURCE = inst.query("print(localnode.smub.measure.v(localnode.smub.nvbuffer1))")
                
                I_g = float(I_GATE.replace("\n", ""))
                V_g = float(V_GATE.replace("\n", ""))
                V_s = float(V_SOURCE.replace("\n", ""))
                
                localnode_file = open(os.path.dirname(__file__)  + '/../dat/CC/' + filename, "a")
                localnode_file.write(str(ni * interval) + "," + str(V_s) + "," + str(I_g) + "," + str(V_g) + "\n")
                localnode_file.close()
                    
                figure = plot(df, radio_state)
                
                button_text = 'Pause'# Constant Current Measurement'

            else:
                file = open(os.path.dirname(__file__)  + '/../dat/CC/test.txt', "r")
                filename = file.read()
                file.close()
                
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/CC/' + filename, usecols = ['Time [s]', 'Source Voltage [V]', 'Gate Current [A]', 'Gate Voltage [V]'], skiprows = 1).copy()
                
                rm = visa.highlevel.ResourceManager()
                inst = rm.open_resource(address)
                
                inst.write("localnode.smub.source.output = localnode.smub.OUTPUT_OFF")
                inst.write("localnode.smua.source.output = localnode.smua.OUTPUT_OFF")
                
                inst.write("localnode.beeper.enable = beeper.ON\n")
                inst.write("localnode.beeper.beep(1,500)\n")
                inst.write("localnode.beeper.enable = beeper.OFF\n")
                
                inst.close()
                #max_int = 0
                flag = True
                
                figure = plot(df, radio_state)
                btn_clicks = button_clicks
                button_text = "Complete! Saved in dat/CC/. To restart, refresh the page."
                print("Complete")
                CC_button_state = True
            #timec.sleep(interval - (timec.time() - t))
            interval = interval * 1000
        else:
            file = open(os.path.dirname(__file__)  + '/../dat/CC/test.txt', "r")
            filename = file.read()
            file.close()
                
            df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/CC/' + filename, usecols = ['Time [s]', 'Source Voltage [V]', 'Gate Current [A]', 'Gate Voltage [V]'], skiprows = 1).copy()
            
            figure = plot(df, radio_state)
            btn_clicks = 0
            flag = True
            #max_int = 0
            button_text = 'Start'# Constant Current Measurement'

    print("button_clicks = " + str(button_clicks))
    #print("interval = " + str(nt - n))
    return figure, interval, flag, CC_V_state, states, states, states, button_text, CC_button_state