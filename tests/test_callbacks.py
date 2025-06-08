import base64
import json
import dash
from dash import no_update

import geojson_mapper.callbacks as cb


def get_update_map_function():
    app = dash.Dash(__name__)
    cb.register_callbacks(app)
    # Extract the original callback function from the map
    callback_fn = next(iter(app.callback_map.values()))['callback'].__wrapped__
    return callback_fn


def test_update_map_with_empty_features():
    update_map = get_update_map_function()
    empty_geojson = {"type": "FeatureCollection", "features": []}
    contents = "data:application/json;base64," + base64.b64encode(
        json.dumps(empty_geojson).encode()
    ).decode()
    message, layer, center, zoom = update_map(contents, "empty.geojson")

    assert "No features" in message
    assert layer is no_update
    assert center is no_update
    assert zoom is no_update
