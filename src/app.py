import dash
from dash import Dash, dcc, html, Input, Output, State, callback
#import os
import webbrowser
import socket
from pages import ConstantCurrent, IV, PulsedMode, home


app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
    ])

#dr = webdriver.Chrome()

#os.system("start \"\" http://192.168.75.103:8080/")
webbrowser.open_new("http://" + socket.gethostbyname(socket.gethostname()) + ":8080/")

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'),
              Input('url', 'href'),
              )
def display_page(pathname, href):
    if len(href.split('?')) > 1:
        param=[]
        query = href.split('?')[1]
        params = query.split('&')
        for p in params:
            param.append(p.split('=')[1])
    if pathname == '/ConstantCurrent':
        return ConstantCurrent.layout(param)
    elif pathname == '/IV':
        return IV.layout(param)
    elif pathname == '/PulsedMode':
        return PulsedMode.layout(param)
    elif pathname == '/':
        return home.layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8080, debug=False)  # Turn off reloader if inside Jupyter
    #os.system("start \"\" http://" + socket.gethostbyname(socket.gethostname()) + ":8080/")