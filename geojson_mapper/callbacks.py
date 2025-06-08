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
        [
            Output('upload-data', 'children'),
            Output('geojson-layer', 'children'),
            Output('map', 'center'),
            Output('map', 'zoom'),
            Output('layers-store', 'data'),
        ],
        [Input('upload-data', 'contents')],
        [State('upload-data', 'filename'), State('layers-store', 'data')]
    )
    def update_map(contents, filename, stored_layers):
        if contents is None:
            return no_update, no_update, no_update, no_update, no_update

        stored_layers = stored_layers or []

        if not isinstance(contents, list):
            contents = [contents]
        if not isinstance(filename, list):
            filename = [filename]

        new_features = []

        for cont, fname in zip(contents, filename):
            content_type, content_string = cont.split(',')
            try:
                decoded = base64.b64decode(content_string)
                geojson = json.loads(decoded)
                if 'features' not in geojson:
                    return (
                        f"File {fname} is not a valid GeoJSON file.",
                        no_update,
                        no_update,
                        no_update,
                        no_update,
                    )
            except Exception as e:
                return (
                    f"Error processing {fname}: {str(e)}",
                    no_update,
                    no_update,
                    no_update,
                    no_update,
                )

            if not geojson.get('features'):
                continue

            new_features.extend(geojson['features'])

        if not new_features:
            return no_update, no_update, no_update, no_update, no_update

        updated_features = stored_layers + new_features

        geojson_layer = []
        centroids = []
        latitudes = []
        longitudes = []

        for feature in updated_features:
            if 'description' in feature['properties']:
                feature_component = dl.GeoJSON(
                    data=feature,
                    children=dl.Tooltip(content=feature['properties']['description'])
                )
            else:
                feature_component = dl.GeoJSON(
                    data=feature
                )
            if 'icon' in feature['properties']:
                feature_component = dl.Marker(
                    position=[feature['geometry']['coordinates'][1], feature['geometry']['coordinates'][0]],
                    children=[
                        dl.Tooltip(content=feature['properties'].get('name')),
                        dl.Popup(content=feature['properties'].get('description'))
                    ],
                    icon=feature['properties']['icon'],
                )
            geojson_layer.append(
                feature_component
            )

        for feature in new_features:
            geom = shape(feature['geometry'])
            centroids.append(geom.centroid)
            bounds = geom.bounds
            longitudes.extend([bounds[0], bounds[2]])
            latitudes.extend([bounds[1], bounds[3]])

        avg_lat = sum(centroid.y for centroid in centroids) / len(centroids)
        avg_lon = sum(centroid.x for centroid in centroids) / len(centroids)

        filenames_str = ', '.join(filename)

        return (
            f"Successfully uploaded {filenames_str}",
            geojson_layer,
            [avg_lat, avg_lon],
            no_update,
            updated_features,
        )

    @app.callback(
        [Output('geojson-layer', 'children'), Output('layers-store', 'data')],
        Input('clear-map', 'n_clicks'),
    )
    def clear_map(n_clicks):
        if not n_clicks:
            return no_update, no_update
        return [], []
