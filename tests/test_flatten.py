from unittest.mock import Mock

import pytest
from geopandas import GeoDataFrame
from pandas import DataFrame
from pytest import raises
from shapely import Point

from crossfire import NestedColumnError, flatten

DICT_DATA = [
    {
        "answer": 42,
        "contextInfo": {"context1": "info1", "context2": "info2"},
    }
]
PD_DATA = DataFrame(DICT_DATA)
GEOMETRY = [Point(4, 2)]
GEOPD_DATA = GeoDataFrame(DICT_DATA, crs="EPSG:4326", geometry=GEOMETRY)


def teste_flatten_wrong_nested_columns_value_error():
    with raises(NestedColumnError):
        flatten(DICT_DATA, nested_columns=["wrong"])


def teste_flatten_with_emptylist():
    assert flatten([]) == []


def teste_flatten_with_emptyDataFrame():
    data = flatten(DataFrame())
    assert data.equals(DataFrame())


def test_flatten_dict():
    flattened_dict = flatten(
        DICT_DATA, nested_columns=["contextInfo", "neighborhood"]
    )
    assert flattened_dict == [
        {
            "answer": 42,
            "contextInfo_context1": "info1",
            "contextInfo_context2": "info2",
        }
    ]


def test_flatten_pd():
    flattened_pd = flatten(
        PD_DATA, nested_columns=["contextInfo", "neighborhood"]
    )
    assert flattened_pd.equals(
        DataFrame(
            [
                {
                    "answer": 42,
                    "contextInfo_context1": "info1",
                    "contextInfo_context2": "info2",
                }
            ]
        )
    )


def test_aux_function_is_called():
    mock_flatten_df = Mock()

    with pytest.MonkeyPatch().context() as m:
        m.setattr("crossfire._flatten_df", mock_flatten_df)

        flatten(PD_DATA, nested_columns=["contextInfo"])

    mock_flatten_df.assert_called_once()
