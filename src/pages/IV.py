#IV

import dash
import plotly.graph_objects as go # or plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, callback
#from dash.dependencies import Input, Output
import os
import pyvisa as visa
import numpy as np
import datetime
import time as timec

def plot(df, r_state):
    if r_state == '0':
        iv_x = df['Source Voltage [V]'].to_numpy()
    else:
        iv_x = df['Gate Voltage [V]'].to_numpy()
    iv_y_s = df['Source Current [A]'].to_numpy()
    iv_y_g = df['Gate Current [A]'].to_numpy()
    
    #figure = go.Figure()

    # Create figure with secondary y-axis
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    
    figure.add_trace(go.Scatter(
        x=iv_x,
        y=iv_y_s,
        name='Source Current [A]',
        line=dict(color='blue')
        ),
        secondary_y=False
    )
    figure.add_trace(go.Scatter(
        x=iv_x,
        y=iv_y_g,
        name='Gate Current [A]',
        line=dict(color='red')
        ),
        secondary_y=True
    )
    figure.update_layout(title=f'IV Characterization. Last idx: {len(df)}')

    if r_state == '0':
        # Set x-axis title
        figure.update_xaxes(title_text="Source Voltage [V]")
    else:
        # Set x-axis title
        figure.update_xaxes(title_text="Gate Voltage [V]")

    # Set y-axes titles
    figure.update_yaxes(
        title_text="Source Current [A]", 
        secondary_y=False)

    figure.update_yaxes(
        title_text="Gate Current [A]", 
        secondary_y=True)

    return figure

def layout(param):
    return html.Div([
        dcc.Graph(
            id='iv-fig',
    #        figure=fig
            ),
        dcc.Interval(
            id='int-comp-iv',
            interval=1*1000,
            n_intervals=0,
            #max_intervals=-1,
            disabled = False
        ),
        dcc.RadioItems(id='radio-button-iv', options=[{'label':'IV_g', 'value':'1'}, {'label':'IV_ds', 'value':'0'}], value='1', inline=True),
        html.Div(html.Button(children='Start', id='IV-button', n_clicks=0), style={'width': '81%', 'display': 'inline-block'}),
        html.Div(children="Instrument Address: ", id='addre', style={'width': '20%', 'display': 'inline-block'}),
        html.Div(children=param[0], id='addr', style={'width': '20%', 'display': 'inline-block'}),
        html.Div([
            html.Div(id='t1', children="Gate Voltage Start [V]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='IV-V_START', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(id='t2', children="Gate Voltage End [V]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='IV-V_END', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(id='t3', children="Voltage Step [V]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='IV-V_STEP', type='number', disabled=False)
        ]),
        html.Div([
            html.Div(id='t4', children="Source Applied Voltage [V]: ", style={'width': '20%', 'display': 'inline-block'}),
            dcc.Input(id='IV-V_APP', type='number', disabled=False)
        ]),
    ])

@callback(
    Output('iv-fig', 'figure'),
    Output('int-comp-iv', 'disabled'),
    Output('IV-V_START', 'disabled'),
    Output('IV-V_END', 'disabled'),
    Output('IV-V_STEP', 'disabled'),
    Output('IV-V_APP', 'disabled'),
    Output('t1', 'children'),
    Output('t2', 'children'),
    Output('t3', 'children'),
    Output('t4', 'children'),
    [Output('IV-button', 'children'),
    Output('IV-button', 'disabled'),
    Input('IV-button', 'n_clicks'),
    Input('IV-button', 'children')],
    Input('addr', 'children'),
    Input('IV-V_START', 'value'),
    Input('IV-V_END', 'value'),
    Input('IV-V_STEP', 'value'),
    Input('IV-V_APP', 'value'),
    Input('int-comp-iv', 'n_intervals'),
    Input('int-comp-iv', 'disabled'),
    Input('radio-button-iv', 'value')
)
def IV(button_clicks, button_text, address, V_i, V_f, dV, V_a, ni, flag, radio_state):
    IV_button_state = False    
    if button_clicks == 0:
        states = False
        IV_V_i_state = False
    else:
        IV_V_i_state = True
        states = True
        STEPS = int(np.abs(V_f - V_i) / dV)

    if radio_state == '1':
        t1 = "Gate Voltage Start [V]: "
        t2 = "Gate Voltage End [V]: "
        t3 = "Voltage Step [V]: "
        t4 = "Source Applied Voltage [V]: "

        if button_clicks % 2 == 1:
            #t = timec.time()
            flag = False
            if ni < STEPS:
                v = V_i + (ni * dV)
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
                    inst.write("localnode.smub.source.func = localnode.smub.OUTPUT_DCVOLTS")
                    inst.write("localnode.smub.source.rangev = 20")
                    inst.write("localnode.smub.source.limiti = 10e-3")
                    
                    inst.write("localnode.smub.measure.limiti = 10e-3")
                    inst.write("localnode.smub.nvbuffer1.clear()")
                    
                    inst.write("localnode.smub.source.levelv = " + str(V_a))

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
                    filename = "IVg_Measurement_" + date + ".csv"
                    localnode_file = open(os.path.dirname(__file__)  + '/../dat/IV/' + filename, "a")
                    localnode_file.write("Source Voltage = " + str(V_a) + "A" + ", Gate Voltage Start = " + str(V_i) + "V" + ", Gate Voltage End = " + str(V_f) + "V" + ", Gate Voltage Step = " + str(dV) + "V\n")
                    localnode_file.write("Source Voltage [V],Gate Voltage [V],Source Current [A],Gate Current [A]\n")
                    localnode_file.close()
                    file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "w")
                    file.write(filename)
                    file.close()
                    print("Setup Successful")
                file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "r")
                filename = file.read()
                file.close()
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/IV/' + filename, usecols = ['Gate Voltage [V]', 'Source Current [A]', 'Gate Current [A]'], skiprows = 1).copy()
                
                
                inst.write("localnode.smua.source.levelv = " + str(v))
                
                I_GATE = inst.query("print(localnode.smua.measure.i(localnode.smua.nvbuffer1))")
                I_SOURCE = inst.query("print(localnode.smub.measure.i(localnode.smub.nvbuffer1))")
                
                I_g = float(I_GATE.replace("\n", ""))
                I_s = float(I_SOURCE.replace("\n", ""))
                
                localnode_file = open(os.path.dirname(__file__)  + '/../dat/IV/' + filename, "a")
                localnode_file.write(str(V_a) + "," + str(v) + "," + str(I_s) + "," + str(I_g) + "\n")
                localnode_file.close()
                    
                figure = plot(df, radio_state)
                
                button_text = 'Pause'
            elif ni >= STEPS and ni < (2 * STEPS) + 1:
                v = V_f - ((ni - STEPS) * dV)

                rm = visa.highlevel.ResourceManager()
                inst = rm.open_resource(address)

                file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "r")
                filename = file.read()
                file.close()
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/IV/' + filename, usecols = ['Gate Voltage [V]', 'Source Current [A]', 'Gate Current [A]'], skiprows = 1).copy()                
                
                inst.write("localnode.smua.source.levelv = " + str(v))
                
                I_GATE = inst.query("print(localnode.smua.measure.i(localnode.smua.nvbuffer1))")
                I_SOURCE = inst.query("print(localnode.smub.measure.i(localnode.smub.nvbuffer1))")
                
                I_g = float(I_GATE.replace("\n", ""))
                I_s = float(I_SOURCE.replace("\n", ""))
                
                localnode_file = open(os.path.dirname(__file__)  + '/../dat/IV/' + filename, "a")
                localnode_file.write(str(V_a) + "," + str(v) + "," + str(I_s) + "," + str(I_g) + "\n")
                localnode_file.close()
                    
                figure = plot(df, radio_state)
                
                button_text = 'Pause'

            else:
                file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "r")
                filename = file.read()
                file.close()
                
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/IV/' + filename, usecols = ['Gate Voltage [V]', 'Source Current [A]', 'Gate Current [A]'], skiprows = 1).copy()
                
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
                button_text = "Complete! Saved in dat/IV/. To restart, refresh the page."
                IV_button_state = True
            #timec.sleep(interval - (timec.time() - t))
        else:
            file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "r")
            filename = file.read()
            file.close()
                
            df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/IV/' + filename, usecols = ['Gate Voltage [V]', 'Source Current [A]', 'Gate Current [A]'], skiprows = 1).copy()
            
            figure = plot(df, radio_state)
            btn_clicks = 0
            flag = True
            #max_int = 0
            button_text = 'Start'
            
    elif radio_state == '0':
        t1 = "Source Voltage Start [V]: "
        t2 = "Source Voltage End [V]: "
        t3 = "Voltage Step [V]: "
        t4 = "Gate Applied Voltage [V]: "

        if button_clicks % 2 == 1:
            #t = timec.time()
            flag = False
            if ni < STEPS:
                v = V_i + (ni * dV)
                btn_clicks = 0
                rm = visa.highlevel.ResourceManager()
                print(address)
                inst = rm.open_resource(address)
                if ni == 0:
                    inst.write("localnode.beeper.enable = beeper.ON\n")
                    inst.write("localnode.beeper.beep(1,100)\n")
                    inst.write("localnode.beeper.enable = beeper.OFF\n")
                    
                    inst.write("localnode.smua.reset()\n")
                    
                    #start
                    inst.write("localnode.smua.source.func = localnode.smub.OUTPUT_DCVOLTS")
                    inst.write("localnode.smua.source.rangev = 20")
                    inst.write("localnode.smua.source.limiti = 10e-3")
                    
                    inst.write("localnode.smua.measure.limiti = 10e-3")
                    inst.write("localnode.smua.nvbuffer1.clear()")
                    
                    inst.write("localnode.smua.source.levelv = " + str(V_a))

                    #localnode.smu-A
                    inst.write("localnode.smub.reset()\n")
                    
                    #start
                    inst.write("localnode.smub.source.func = localnode.smua.OUTPUT_DCVOLTS")
                    inst.write("localnode.smub.source.rangev = 20")
                    inst.write("localnode.smub.source.limiti = 10e-3")
                    
                    inst.write("localnode.smub.measure.rangei = 10e-3")
                    inst.write("localnode.smub.nvbuffer1.clear()")

                    inst.write("localnode.smub.source.output = localnode.smub.OUTPUT_ON\n")
                    inst.write("localnode.smua.source.output = localnode.smua.OUTPUT_ON\n")

                    d = datetime.datetime.now()
                    date = str(d).replace(":", "_")
                    filename = "IVds_Measurement_" + date + ".csv"
                    localnode_file = open(os.path.dirname(__file__)  + '/../dat/IV/' + filename, "a")
                    localnode_file.write("Gate Voltage = " + str(V_a) + "A" + ", Source Voltage Start = " + str(V_i) + "V" + ", Source Voltage End = " + str(V_f) + "V" + ", Source Voltage Step = " + str(dV) + "V\n")
                    localnode_file.write("Source Voltage [V],Gate Voltage [V],Source Current [A],Gate Current [A]\n")
                    localnode_file.close()
                    file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "w")
                    file.write(filename)
                    file.close()
                    print("Setup Successful")
                file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "r")
                filename = file.read()
                file.close()
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/IV/' + filename, usecols = ['Source Voltage [V]', 'Source Current [A]', 'Gate Current [A]'], skiprows = 1).copy()                
                
                inst.write("localnode.smub.source.levelv = " + str(v))
                
                I_GATE = inst.query("print(localnode.smua.measure.i(localnode.smua.nvbuffer1))")
                I_SOURCE = inst.query("print(localnode.smub.measure.i(localnode.smub.nvbuffer1))")
                
                I_g = float(I_GATE.replace("\n", ""))
                I_s = float(I_SOURCE.replace("\n", ""))
                
                localnode_file = open(os.path.dirname(__file__)  + '/../dat/IV/' + filename, "a")
                localnode_file.write(str(v) + "," + str(V_a) + "," + str(I_s) + "," + str(I_g) + "\n")
                localnode_file.close()
                    
                figure = plot(df, radio_state)
                
                button_text = 'Pause'
            elif ni >= STEPS and ni < (2 * STEPS) + 1:
                v = V_f - ((ni - STEPS) * dV)

                rm = visa.highlevel.ResourceManager()
                inst = rm.open_resource(address)

                file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "r")
                filename = file.read()
                file.close()
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/IV/' + filename, usecols = ['Source Voltage [V]', 'Source Current [A]', 'Gate Current [A]'], skiprows = 1).copy()
                
                inst.write("localnode.smub.source.levelv = " + str(v))
                
                I_GATE = inst.query("print(localnode.smua.measure.i(localnode.smua.nvbuffer1))")
                I_SOURCE = inst.query("print(localnode.smub.measure.i(localnode.smub.nvbuffer1))")
                
                I_g = float(I_GATE.replace("\n", ""))
                I_s = float(I_SOURCE.replace("\n", ""))
                
                localnode_file = open(os.path.dirname(__file__)  + '/../dat/IV/' + filename, "a")
                localnode_file.write(str(v) + "," + str(V_a) + "," + str(I_s) + "," + str(I_g) + "\n")
                localnode_file.close()
                    
                figure = plot(df, radio_state)
                
                button_text = 'Pause'

            else:
                file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "r")
                filename = file.read()
                file.close()
                
                df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/IV/' + filename, usecols = ['Source Voltage [V]', 'Source Current [A]', 'Gate Current [A]'], skiprows = 1).copy()
                
                rm = visa.highlevel.ResourceManager()
                inst = rm.open_resource(address)
                
                inst.write("localnode.smua.source.output = localnode.smua.OUTPUT_OFF")
                inst.write("localnode.smub.source.output = localnode.smub.OUTPUT_OFF")
                
                inst.write("localnode.beeper.enable = beeper.ON\n")
                inst.write("localnode.beeper.beep(1,500)\n")
                inst.write("localnode.beeper.enable = beeper.OFF\n")
                
                inst.close()
                #max_int = 0
                flag = True
                
                figure = plot(df, radio_state)
                #button_text = 'Restart'
                #btn_clicks = button_clicks
                print("Complete")
                button_text = "Complete! Saved in dat/IV/. To restart, refresh the page."
                IV_button_state = True
            #timec.sleep(interval - (timec.time() - t))
        else:
            file = open(os.path.dirname(__file__)  + '/../dat/IV/test.txt', "r")
            filename = file.read()
            file.close()
                
            df = pd.read_csv(os.path.dirname(__file__)  + '/../dat/IV/' + filename, usecols = ['Source Voltage [V]', 'Source Current [A]', 'Gate Current [A]'], skiprows = 1).copy()
            
            figure = plot(df, radio_state)
            btn_clicks = 0
            flag = True
            #max_int = 0
            button_text = 'Start'
        

    print("button_clicks = " + str(button_clicks))
    return figure, flag, IV_V_i_state, states, states, states, t1, t2, t3, t4, button_text, IV_button_state