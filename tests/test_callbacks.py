import json
import base64
import dash
from dash import no_update
from geojson_mapper.callbacks import register_callbacks


def setup_app():
    app = dash.Dash(__name__)
    register_callbacks(app)
    callbacks = {}
    for data in app.callback_map.values():
        func = data['callback'].__wrapped__
        callbacks[func.__name__] = func
    return app, callbacks


def test_update_map_empty_features():
    app, cbs = setup_app()
    update_map = cbs['update_map']
    empty_geojson = {"type": "FeatureCollection", "features": []}
    encoded = base64.b64encode(json.dumps(empty_geojson).encode()).decode()
    contents = f"data:application/json;base64,{encoded}"
    with app.server.test_request_context('/'):
        result = update_map(contents, "empty.geojson", [])
    assert result == (no_update, no_update, no_update, no_update, no_update)


def test_update_map_multiple_uploads():
    app, cbs = setup_app()
    update_map = cbs['update_map']
    g1 = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 0]}, "properties": {}}]}
    g2 = {"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 1]}, "properties": {}}]}
    c1 = f"data:application/json;base64,{base64.b64encode(json.dumps(g1).encode()).decode()}"
    c2 = f"data:application/json;base64,{base64.b64encode(json.dumps(g2).encode()).decode()}"
    with app.server.test_request_context('/'):
        result = update_map([c1, c2], ["a.geojson", "b.geojson"], [])
    layers = result[4]
    assert len(layers) == 2
    assert len(result[1]) == 2


def test_clear_map():
    app, cbs = setup_app()
    clear_map = cbs['clear_map']
    with app.server.test_request_context('/'):
        result = clear_map(1)
    assert result == ([], [])
