from json import dumps
from unittest.mock import Mock, patch

try:
    from geopandas import GeoDataFrame

    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False

try:
    from pandas import DataFrame

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from pytest import mark, raises

from crossfire.parser import (
    IncompatibleDataError,
    UnknownFormatError,
    parse_response,
)

DATA = [{"answer": 42}]
GEODATA = [{"answer": 42, "latitude": 4, "longitude": 2}]

skip_if_pandas_not_installed = mark.skipif(
    not HAS_PANDAS, reason="pandas is not installed"
)
skip_if_geopandas_not_installed = mark.skipif(
    not HAS_GEOPANDAS, reason="geopandas is not installed"
)


class DummyError(Exception):
    pass


def create_response(geo=False, has_next_page=False):
    data = {
        "pageMeta": {
            "hasNextPage": has_next_page,
            "pageCount": 42 if has_next_page else 1,
        },
        "data": GEODATA if geo else DATA,
    }

    response = Mock()
    response.url = "http://127.0.0.1/"
    response.status_code = 200
    response.text = dumps(data)
    response.json.return_value = data
    return response


def test_parse_response_raises_error_for_unknown_format():
    with raises(UnknownFormatError):
        parse_response(None, format="parquet")


def test_parse_response_raises_error_when_cannot_parse_json():
    response = create_response()
    response.json.side_effect = DummyError()
    with raises(DummyError), patch("crossfire.parser.Logger") as mock:
        parse_response(response)
        mock.return_value.error.assert_called_once()
        msg, *_ = mock.return_value.error.call_args.args
        assert response.status_code in msg
        assert response.url in msg
        assert response.text in msg


def test_parse_response_uses_dict_by_default():
    data, _ = parse_response(create_response())
    assert isinstance(data, list)
    for obj in data:
        assert isinstance(obj, dict)


def test_parse_response_handles_metadata():
    _, metadata = parse_response(create_response(has_next_page=True))
    assert metadata.has_next_page
    assert metadata.page_count == 42

    _, metadata = parse_response(create_response())
    assert not metadata.has_next_page
    assert metadata.page_count == 1


@skip_if_pandas_not_installed
def test_parse_response_uses_dataframe_when_specified():
    data, _ = parse_response(create_response(), format="df")
    assert isinstance(data, DataFrame)


@skip_if_geopandas_not_installed
def test_parse_response_uses_geodataframe_when_specified():
    data, _ = parse_response(create_response(True), format="geodf")
    assert isinstance(data, GeoDataFrame)


@skip_if_geopandas_not_installed
def test_parse_response_raises_error_when_missing_coordinates():
    with raises(IncompatibleDataError):
        parse_response(create_response(), format="geodf")
