<div style="text-align: center">
<img src="https://raw.githubusercontent.com/voltdatalab/crossfire/master/crossfire_hexagono.png" width="130px" alt="hexagon crossfire"/>

# `crossfire` Python client
</div>

`crossfire` is a package created to give easier access to [Fogo Cruzado](https://fogocruzado.org.br/)'s datasets, which is a digital collaborative platform of gun shooting occurences in the metropolitan areas of Rio de Janeiro and Recife.

The package facilitates data extraction from [Fogo Cruzado's open API](https://api.fogocruzado.org.br/).

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

## User registration

To have access to the API data, [registration is required](https://api.fogocruzado.org.br/sign-up).

## Environmental variables

The `email` and `password` used in the registration must be configured as `FOGOCRUZADO_EMAIL` and `FOGOCRUZADO_PASSWORD` environment variables in a `.env` file.

````commandline
#.env
FOGOCRUZADO_EMAIL=your@mail.com
FOGOCRUZADO_PASSWORD=YOUR_PASSWORD
````

### List of states covered by the project

Get all states with at least one city covered by the Fogo Cruzado project:
```python
from crossfire import Client
client = Client()
client.states()
```

It is possible to get results in `DataFrae`:
```python
client.states(format='df')
```

### List of cities covered by the project

Get cities from a specific state covered by the Fogo Cruzado project.

```python
from crossfire import Client
client = Client()
client.cities()
```

It is possible to get results in `DataFrae`:
```python
client.cities(format='df')
```

### Listing occurences

To get shooting occurences from Fogo Cruzado dataset it is necessary to specify a state id in `id_state` parameter:

```python
from crossfire import Client, Occurences
client = Client()
Occurences(client, state_id='813ca36b-91e3-4a18-b408-60b27a1942ef')
```

It is possible to get results in `DataFrae`:
```python
Occurences(client, state_id='813ca36b-91e3-4a18-b408-60b27a1942ef', format='df')
```
Or as `GeoDataFrame`:
```python
Occurences(client, state_id='813ca36b-91e3-4a18-b408-60b27a1942ef', format='geodf')
```

## Custom credentials usage

If not using the environment variables for authentication, it is recommended to use a custom client:

```python
from crossfire import Client

client = Client(email="fogo@cruza.do", password="Rio&Pernambuco")
client.states()
client.cities()
```

## Credits

@FelipeSBarros is the creator of the Python package. This implementation was funded by CYTED project number `520RT0010 redGeoLIBERO`.

### Contributors

* @sergiospagnuolo
* @silvadenisson
* @cuducos
