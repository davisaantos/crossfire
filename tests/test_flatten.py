from unittest.mock import patch

from geopandas import GeoDataFrame
from pandas import DataFrame
from pytest import raises
from shapely.geometry import Point

from crossfire import flatten

DICT_DATA = [
    {"answer": 42, "contextInfo": {"context1": "info1", "context2": "info2"}}
]
PD_DATA = DataFrame(DICT_DATA)
geometry = [Point(4, 2)]
GEOPD_DATA = GeoDataFrame(DICT_DATA, crs="EPSG:4326", geometry=geometry)




def teste_flatten_wrong_nested_columns_value_error():
    with raises(ValueError):
        flatten(DICT_DATA, nested_columns="wrong")


# test the flatten function with a dictionary mocking it to assert _flatten_dict function is being called
def test_flatten_dict():
    with patch("crossfire._flatten_dict") as mock:
        flattened_dict = flatten(DICT_DATA)
        mock.assert_called_once_with(DICT_DATA, ["contextInfo"])
        flattened_dict == {
            "answer": 42,
            "contextInfo_context1": "info1",
            "contextInfo_context2": "info2",
        }
