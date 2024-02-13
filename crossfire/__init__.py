__version__ = "0.1.0"
__all__ = ("AsyncClient", "Client", "cities", "occurrences", "states")

from functools import lru_cache

from crossfire.clients import AsyncClient, Client  # noqa

NESTED_COLUMNS = {"contextInfo", "transports", "victims", "animalVictims"}


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


def flatten(data, nested_columns=None):
    if nested_columns is None:
        nested_columns = NESTED_COLUMNS
    nested_columns = set(nested_columns)
    if not nested_columns.issubset(NESTED_COLUMNS):
        raise ValueError(f"Invalid `nested_columns` value: {nested_columns}")
    if isinstance(data, list):
        keys = set(data[0].keys()) & nested_columns
        for item in data:
            for key in keys:
                for k, v in item.get(key).items():
                    return f"{key}_{k}", v
