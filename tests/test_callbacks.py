import json
import base64
import dash
from dash import no_update
from geojson_mapper.callbacks import register_callbacks


def get_update_map(app):
    # register_callbacks adds the callback function to the app and returns nothing.
    register_callbacks(app)
    # Retrieve the first registered callback function
    callback_data = next(iter(app.callback_map.values()))
    # Dash wraps the function; __wrapped__ gives the original user function
    return callback_data['callback'].__wrapped__


def test_update_map_empty_features():
    app = dash.Dash(__name__)
    update_map = get_update_map(app)
    empty_geojson = {"type": "FeatureCollection", "features": []}
    encoded = base64.b64encode(json.dumps(empty_geojson).encode()).decode()
    contents = f"data:application/json;base64,{encoded}"
    # simulate dash callback context with test_request_context
    with app.server.test_request_context('/'):
        result = update_map(contents, "empty.geojson")
    assert result == (no_update, no_update, no_update, no_update)
