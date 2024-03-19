from unittest.mock import Mock, patch

try:
    from geopandas import GeoDataFrame

    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
try:
    from pandas import DataFrame, Series

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
from pytest import raises

try:
    from shapely import Point
except ImportError:
    pass
from pytest import mark

from crossfire.clients.occurrences import flatten
from crossfire.errors import NestedColumnError

skip_if_pandas_not_installed = mark.skipif(
    not HAS_PANDAS, reason="pandas is not installed"
)
skip_if_geopandas_not_installed = mark.skipif(
    not HAS_GEOPANDAS, reason="geopandas is not installed"
)

DICT_DATA = [
    {
        "answer": 42,
        "contextInfo": {"context1": "info1", "context2": "info2"},
    }
]
if HAS_PANDAS:
    PD_DATA = DataFrame(DICT_DATA)
if HAS_GEOPANDAS:
    GEOMETRY = [Point(4, 2)]
    GEOPD_DATA = GeoDataFrame(DICT_DATA, crs="EPSG:4326", geometry=GEOMETRY)


def test_flatten_wrong_nested_columns_value_error():
    with raises(NestedColumnError):
        flatten(DICT_DATA, nested_columns=["wrong"])


def test_flatten_with_empty_list():
    assert flatten([]) == []


@skip_if_pandas_not_installed
def test_flatten_with_empty_data_frame():
    with patch("crossfire.clients.occurrences._flatten_df") as mock_flatten_df:
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


@skip_if_pandas_not_installed
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


@skip_if_pandas_not_installed
def test_flatten_df_is_called():
    # There is a bug on Pandas that makes apply fails when called from Series with the default MagicMock
    # more info: https://github.com/pandas-dev/pandas/issues/45298
    with patch(
        "crossfire.clients.occurrences._flatten_df", new_callable=Mock
    ) as mock_flatten_df:
        mock_flatten_df.return_value = Series(
            {
                "contextInfo_context1": "info1",
                "contextInfo_context2": "info2",
            }
        )

        flatten(PD_DATA, nested_columns=["contextInfo"])

    mock_flatten_df.assert_called_once()


@skip_if_geopandas_not_installed
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
