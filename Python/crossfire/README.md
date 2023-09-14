<div style="text-align: center">
<img src="https://raw.githubusercontent.com/voltdatalab/crossfire/master/crossfire_hexagono.png" width="130px" alt="hexagon crossfire"/>

# `crossfire` Python client
</div>

`crossfire` is a package created to give easier access to [Fogo Cruzado](https://fogocruzado.org.br/)'s datasets, which is a digital collaborative platform of gun shooting occurences in the metropolitan areas of Rio de Janeiro and Recife.

The package facilitates data extraction from [Fogo Cruzado's open API](https://api.fogocruzado.org.br/), developed by [Volt Data Lab](https://www.voltdata.info/).

## Requirements

* Python 3.9 or newer

## Install

```console
$ pip install crossfire
```

If you want to have access to the data as [Pandas `DataFrame`s](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html):

```console
$ pip install crossfire[df]
```

If you want to have access to the data as [GeoPandas `GeoDataFrame`s](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html):

```console
$ pip install crossfire[geodf]
```

## Basic usage

The basic usage requires the environment variables `FOGOCRUZADO_EMAIL` and `FOGOCRUZADO_PASSWORD` to be set. You can create these credentials [registering as an API user](https://api.fogocruzado.org.br/sign-up).

### Listing cities available

All cities covered by the Fogo Cruzado dataset.

```python
from crossfire import cities

cities()
```

### Listing states availabe

All states with at least one city covered by the Fogo Cruzado dataset.

```python
from crossfire import states

states()
```

### Listing occurences

Shooting occurences from Fogo Cruzado dataset.

```python
from crossfire import occurences

occurences()
```

Also, `occurences` can be filtered using keyword arguments:

| Keyword | Type | Default value | Description |
|:--|:--|:--|:--|
| `city` | _string_ or _iterable of strings_ | `None` | Name of cities |
| `state` |  _string_ or _iterable of strings_ | `["PE", "RJ"]` | Abbreviation of states |
| `starting_at` | _datetime.date_ | `datetime.date.today()` | Start date for the query |
| `until` | _datetime.date_ | `starting_at` minus 6 months | End date for the query (must be at maximum be 210 days before `starting_at`) |
| `security_agent` | _boolean_ | `None` | Presence of security agent |

For example:

```python
from datetime import date
from crossfire import occurences

occurences(starting_at=date(2020, 1, 1), until=date(2020, 3, 1), state="RJ")
```

## Custom credentials usage

If not using the environment variables for authentication, it is recommended to use a custom client:

```python
from crossfire import Client

client = Client(email="fogo@cruza.do", password="Rio&Pernambuco")
client.occurences()
client.states()
client.cities()
```

## Credits

@FelipeSBarros is the creator of the Python package. This implementation was funded by CYTED project number `520RT0010 redGeoLIBERO`.

The API was crated by @lgelape, for @voltdatalab.

### Contributors

* @sergiospagnuolo
* @silvadenisson
* @cuducos
