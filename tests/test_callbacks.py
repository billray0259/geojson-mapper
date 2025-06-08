import json
import base64
from pathlib import Path
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


def encode_geojson(path: Path) -> str:
    data = path.read_text()
    encoded = base64.b64encode(data.encode()).decode()
    return f"data:application/json;base64,{encoded}"


def test_update_map_empty_features():
    app = dash.Dash(__name__)
    update_map = get_update_map(app)
    empty_geojson = {"type": "FeatureCollection", "features": []}
    encoded = base64.b64encode(json.dumps(empty_geojson).encode()).decode()
    contents = f"data:application/json;base64,{encoded}"
    with app.server.test_request_context('/'):
        result = update_map(contents, "empty.geojson")
    assert result == (no_update, no_update, no_update, no_update)


def test_update_map_valid_point():
    app = dash.Dash(__name__)
    update_map = get_update_map(app)
    point_path = Path("tests/fixtures/sample_point.geojson")
    contents = encode_geojson(point_path)
    with app.server.test_request_context('/'):
        message, layer, center, zoom = update_map(contents, point_path.name)
    assert message == f"Successfully uploaded {point_path.name}"
    assert len(layer) == 1
    assert center == [20.0, 10.0]
    assert zoom is no_update


def test_update_map_valid_polygon():
    app = dash.Dash(__name__)
    update_map = get_update_map(app)
    poly_path = Path("tests/fixtures/sample_polygon.geojson")
    contents = encode_geojson(poly_path)
    with app.server.test_request_context('/'):
        message, layer, center, zoom = update_map(contents, poly_path.name)
    assert message == f"Successfully uploaded {poly_path.name}"
    assert len(layer) == 1
    assert center == [0.5, 0.5]
    assert zoom is no_update


def test_update_map_malformed_json():
    app = dash.Dash(__name__)
    update_map = get_update_map(app)
    malformed = base64.b64encode(b"{bad json").decode()
    contents = f"data:application/json;base64,{malformed}"
    with app.server.test_request_context('/'):
        message, layer, center, zoom = update_map(contents, "malformed.geojson")
    assert message.startswith("Error processing malformed.geojson:")
    assert layer is no_update
    assert center is no_update
    assert zoom is no_update


def test_update_map_missing_features():
    app = dash.Dash(__name__)
    update_map = get_update_map(app)
    data = {"type": "FeatureCollection"}
    encoded = base64.b64encode(json.dumps(data).encode()).decode()
    contents = f"data:application/json;base64,{encoded}"
    with app.server.test_request_context('/'):
        message, layer, center, zoom = update_map(contents, "missing.geojson")
    assert message == "File missing.geojson is not a valid GeoJSON file."
    assert layer is no_update
    assert center is no_update
    assert zoom is no_update


def test_update_map_bad_geometry():
    app = dash.Dash(__name__)
    update_map = get_update_map(app)
    geojson = {
        "type": "FeatureCollection",
        "features": [{"type": "Feature", "properties": {}, "geometry": {"type": "Point", "coordinates": [10]}}]
    }
    encoded = base64.b64encode(json.dumps(geojson).encode()).decode()
    contents = f"data:application/json;base64,{encoded}"
    with app.server.test_request_context('/'):
        message, layer, center, zoom = update_map(contents, "bad.geojson")
    assert message.startswith("Error processing bad.geojson:")
    assert layer is no_update
    assert center is no_update
    assert zoom is no_update
