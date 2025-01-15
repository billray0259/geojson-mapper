# dash_app/layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_leaflet as dl

def create_layout():
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dcc.Upload(
                    id='upload-data',
                    children='Drag and Drop or Click to Select a File',
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=False
                ),
                dl.Map(id='map', style={'width': '100%', 'height': '750px'}, center=[37.0902, -95.7129], zoom=4, children=[
                    dl.TileLayer(),
                    dl.LayerGroup(id='geojson-layer')
                ])
            ])
        ])
    ])