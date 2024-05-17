from unittest.mock import Mock, patch

try:
    from geopandas import GeoDataFrame
    from shapely import Point

    HAS_GEOPANDAS = True
except ModuleNotFoundError:
    HAS_GEOPANDAS = False
try:
    from pandas import DataFrame, Series
    from pandas.testing import assert_frame_equal

    HAS_PANDAS = True
except ModuleNotFoundError:
    HAS_PANDAS = False
from pytest import mark, raises

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
DICT_DATA_MISSING_NESTED_VALUE = [
    {
        "answer": 42,
        "contextInfo": {"context1": "info1"},
    },
    {
        "answer": 42,
        "contextInfo": None,
    },
]
DICT_DATA_ALL_ROWS_MISSING_NESTED_VALUE = [
    {
        "answer": 42,
        "contextInfo": None,
    },
    {
        "answer": 42,
        "contextInfo": None,
    },
]
DICT_DATA_WITH_NESTED_VALUES_IN_NESTED_COLUMNS = [
    {
        "answer": 42,
        "contextInfo": {
            "mainReason": {"mainReason1": "info1", "mainReason2": "info2"}
        },
    },
    {"answer": 42, "contextInfo": {"mainReason": "mainReason1"}},
    {"answer": 42, "contextInfo": None},
]
EXPECTED_DICT_RETURN = [
    {
        "answer": 42,
        "contextInfo": {"context1": "info1", "context2": "info2"},
        "contextInfo_context1": "info1",
        "contextInfo_context2": "info2",
    }
]
EXPECTED_DICT_MISSING_NESTED_VALUE_RETURN = [
    {
        "answer": 42,
        "contextInfo": {"context1": "info1"},
        "contextInfo_context1": "info1",
    },
    {
        "answer": 42,
        "contextInfo": None,
    },
]
EXPECTED_DICT_RETURN_WITH_NESTED_VALUES_IN_NESTED_COLUMNS = [
    {
        "answer": 42,
        "contextInfo": {
            "mainReason": {"mainReason1": "info1", "mainReason2": "info2"}
        },
        "contextInfo_mainReason": {
            "mainReason1": "info1",
            "mainReason2": "info2",
        },
        "contextInfo_mainReason_mainReason1": "info1",
        "contextInfo_mainReason_mainReason2": "info2",
    },
    {
        "answer": 42,
        "contextInfo": {"mainReason": "mainReason1"},
        "contextInfo_mainReason": "mainReason1",
    },
    {
        "answer": 42,
        "contextInfo": None,
    },
]

if HAS_PANDAS:
    PD_DATA = DataFrame(DICT_DATA)
    PD_DATA_MISSING_NESTED_VALUE = DataFrame(DICT_DATA_MISSING_NESTED_VALUE)
    PD_DATA_ALL_ROWS_MISSING_NESTED_VALUE = DataFrame(
        DICT_DATA_ALL_ROWS_MISSING_NESTED_VALUE
    )
    EXPECTED_PD_RETURN = DataFrame(EXPECTED_DICT_RETURN)
    EXPECTED_PD_MISSING_NESTED_VALUE_RETURN = DataFrame(
        EXPECTED_DICT_MISSING_NESTED_VALUE_RETURN
    )
if HAS_GEOPANDAS:
    GEOMETRY = [Point(4, 2)]
    GEOPD_DATA = GeoDataFrame(DICT_DATA, crs="EPSG:4326", geometry=GEOMETRY)
    EXPECTED_GEOPD_RETURN = GeoDataFrame(
        [
            {
                "answer": 42,
                "contextInfo": {"context1": "info1", "context2": "info2"},
                "contextInfo_context1": "info1",
                "contextInfo_context2": "info2",
            }
        ],
        crs="EPSG:4326",
        geometry=GEOMETRY,
    ).reindex(
        columns=(
            "answer",
            "contextInfo",
            "geometry",
            "contextInfo_context1",
            "contextInfo_context2",
        )
    )


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
    assert flattened_dict == EXPECTED_DICT_RETURN


@skip_if_pandas_not_installed
def test_flatten_pd():
    flattened_pd = flatten(
        PD_DATA, nested_columns=["contextInfo", "neighborhood"]
    )
    assert_frame_equal(flattened_pd, EXPECTED_PD_RETURN)


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
    assert_frame_equal(flattened_pd, EXPECTED_GEOPD_RETURN)


def test_flatten_list_is_called():
    with patch(
        "crossfire.clients.occurrences._flatten_list"
    ) as mock_flatten_list:
        flatten(DICT_DATA, nested_columns=["contextInfo", "neighborhood"])

    mock_flatten_list.assert_called_once()


def test_flatten_list():
    result = EXPECTED_DICT_RETURN
    assert (
        flatten(DICT_DATA, nested_columns=["contextInfo", "neighborhood"])
        == result
    )


def test_flatten_dict_with_rows_missing_nested_values():
    assert (
        flatten(DICT_DATA_MISSING_NESTED_VALUE, nested_columns=["contextInfo"])
        == EXPECTED_DICT_MISSING_NESTED_VALUE_RETURN
    )


def test_flatten_dict_with_all_rows_missing_nested_values():
    assert (
        flatten(
            DICT_DATA_ALL_ROWS_MISSING_NESTED_VALUE,
            nested_columns=["contextInfo"],
        )
        == DICT_DATA_ALL_ROWS_MISSING_NESTED_VALUE
    )


@skip_if_pandas_not_installed
def test_flatten_pd_with_missing_nested_values():
    flattened_pd = flatten(
        PD_DATA_MISSING_NESTED_VALUE, nested_columns=["contextInfo"]
    )
    assert_frame_equal(flattened_pd, EXPECTED_PD_MISSING_NESTED_VALUE_RETURN)


@skip_if_pandas_not_installed
def test_flatten_df_with_all_rows_missing_nested_values():
    flattened_pd = flatten(
        PD_DATA_ALL_ROWS_MISSING_NESTED_VALUE, nested_columns=["contextInfo"]
    )
    assert_frame_equal(flattened_pd, PD_DATA_ALL_ROWS_MISSING_NESTED_VALUE)


def test_flatten_list_dicts_with_nested_columns_with_nested_values():
    assert (
        flatten(
            DICT_DATA_WITH_NESTED_VALUES_IN_NESTED_COLUMNS,
            nested_columns=["contextInfo"],
        )
        == EXPECTED_DICT_RETURN_WITH_NESTED_VALUES_IN_NESTED_COLUMNS
    )


@skip_if_pandas_not_installed
def test_flatten_pd_with_nested_columns_with_nested_values():
    flattened_pd = flatten(
        DataFrame(DICT_DATA_WITH_NESTED_VALUES_IN_NESTED_COLUMNS),
        nested_columns=["contextInfo"],
    )
    flattened_pd.columns
    assert_frame_equal(
        flattened_pd,
        DataFrame(EXPECTED_DICT_RETURN_WITH_NESTED_VALUES_IN_NESTED_COLUMNS),
    )
