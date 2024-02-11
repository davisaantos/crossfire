__version__ = "0.1.0"
__all__ = ("AsyncClient", "Client", "cities", "occurrences", "states")

from functools import lru_cache

from crossfire.clients import AsyncClient, Client  # noqa

NESTED_COLUMNS = ["contextInfo"]


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


def _flatten_dict(data, parent_key, sep="_"):
    items = []
    for dict in data:
        for k, v in dict.items():
            new_key = parent_key + sep + k if parent_key else k
            items.append((new_key, v))
        return dict(items)


def flatten(data, nested_columns=None):
    if nested_columns is None:
        nested_columns = NESTED_COLUMNS
    elif nested_columns not in (NESTED_COLUMNS):
        raise ValueError(f"Invalid `nested_columns` value: {nested_columns}")
    if isinstance(data, list):
        return _flatten_dict(data, nested_columns)
