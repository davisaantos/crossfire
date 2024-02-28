__version__ = "0.1.0"
__all__ = ("AsyncClient", "Client", "cities", "occurrences", "states")

from functools import lru_cache

from crossfire.clients import AsyncClient, Client  # noqa
from crossfire.errors import NestedColumnError

try:
    from pandas import DataFrame, Series, concat

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


NESTED_COLUMNS = {
    "contextInfo",
    "state",
    "region",
    "city",
    "neighborhood",
    "locality",
}


@lru_cache(maxsize=1)
def client():
    return Client()


def states(format=None):
    return client().states(format=format)


def cities(city_id=None, city_name=None, state_id=None, format=None):
    return client().cities(
        city_id=city_id, city_name=city_name, state_id=state_id, format=format
    )


def occurrences(
    id_state,
    id_cities=None,
    type_occurrence="all",
    initial_date=None,
    final_date=None,
    max_parallel_requests=None,
    format=None,
):
    return client().occurrences(
        id_state,
        id_cities=id_cities,
        type_occurrence=type_occurrence,
        initial_date=initial_date,
        final_date=final_date,
        max_parallel_requests=max_parallel_requests,
        format=format,
    )


def _flatten_df(row, column_name):
    column_data = row[column_name]
    return Series(
        {f"{column_name}_{key}": value for key, value in column_data.items()}
    )


def is_empty(data):
    if HAS_PANDAS and isinstance(data, DataFrame):
        return data.empty
    return not data


def flatten(data, nested_columns=None):
    nested_columns = set(nested_columns or NESTED_COLUMNS)
    if not nested_columns.issubset(NESTED_COLUMNS):
        raise NestedColumnError(nested_columns)
    if is_empty(data):
        return data
    if HAS_PANDAS and isinstance(data, DataFrame):
        keys = set(data.columns) & nested_columns
        for key in keys:
            data = concat(
                (
                    data.drop(key, axis=1),
                    data.apply(_flatten_df, args=(key,), axis=1),
                ),
                axis=1,
            )

        return data

    keys = set(data[0].keys()) & nested_columns
    for item in data:
        for key in keys:
            item.update({f"{key}_{k}": v for k, v in item.get(key).items()})
            item.pop(key)
    return data
