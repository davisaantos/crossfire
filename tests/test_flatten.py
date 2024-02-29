from unittest.mock import patch

from geopandas import GeoDataFrame
from pandas import DataFrame, Series
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


def test_flatten_wrong_nested_columns_value_error():
    with raises(NestedColumnError):
        flatten(DICT_DATA, nested_columns=["wrong"])


def test_flatten_with_empty_list():
    assert flatten([]) == []


def test_flatten_with_empty_data_frame():
    with patch("crossfire._flatten_df") as mock_flatten_df:
        flatten(DataFrame(), nested_columns=["contextInfo"])

    mock_flatten_df.assert_not_called()


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


def test_flatten_df_is_called():
    with patch("crossfire._flatten_df") as mock_flatten_df:
        mock_flatten_df.return_value = Series(
            {
                "contextInfo_contextInfo_context1": "info1",
                "contextInfo_contextInfo_context2": "info2",
            }
        )

        flatten(PD_DATA, nested_columns=["contextInfo"])

        mock_flatten_df.assert_called_once()


def test_flatten_gpd():
    flattened_pd = flatten(
        GEOPD_DATA, nested_columns=["contextInfo", "neighborhood"]
    )
    result = GeoDataFrame(
        [
            {
                "answer": 42,
                "contextInfo_context1": "info1",
                "contextInfo_context2": "info2",
            }
        ],
        crs="EPSG:4326",
        geometry=GEOMETRY,
    )
    result = result.reindex(
        columns=(
            "answer",
            "geometry",
            "contextInfo_context1",
            "contextInfo_context2",
        )
    )
    assert flattened_pd.equals(result)
