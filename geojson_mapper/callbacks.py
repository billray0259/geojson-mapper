from dash.dependencies import Input, Output, State, ALL
from dash import dcc, html, callback_context, no_update
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import json
import base64
from shapely.geometry import shape
import math


def register_callbacks(app):
    
    @app.callback(
        [Output('upload-data', 'children'), Output('geojson-layer', 'children'), Output('map', 'center'), Output('map', 'zoom')],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename')]
    )
    def update_map(contents, filename):
        if contents is None:
            return no_update, no_update, no_update, no_update

        content_type, content_string = contents.split(',')
        try:
            decoded = base64.b64decode(content_string)
            geojson = json.loads(decoded)
            if not 'features' in geojson:
                return f"File {filename} is not a valid GeoJSON file.", no_update, no_update, no_update, no_update
        except Exception as e:
            return f"Error processing {filename}: {str(e)}", no_update, no_update, no_update, no_update
    
        geojson_layer = []
        centroids = []
        latitudes = []
        longitudes = []
        
        for feature in geojson['features']:
            feature_component = dl.GeoJSON(
                data=feature,
                children=dl.Tooltip(content=feature['properties']['description'])
            )
            if 'icon' in feature['properties']:
                feature_component = dl.Marker(
                    position=[feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]],
                    children=[
                        dl.Tooltip(content=feature['properties']['name']),
                        dl.Popup(content=feature['properties']['description'])
                    ],
                    icon=feature['properties']['icon']
                )
            geojson_layer.append(
                feature_component
            )
            geom = shape(feature['geometry'])
            centroids.append(geom.centroid)
            bounds = geom.bounds
            longitudes.extend([bounds[0], bounds[2]])
            latitudes.extend([bounds[1], bounds[3]])
        
        avg_lat = sum(centroid.y for centroid in centroids) / len(centroids)
        avg_lon = sum(centroid.x for centroid in centroids) / len(centroids)
        
        return f"Successfully uploaded {filename}", geojson_layer, [avg_lat, avg_lon], no_update