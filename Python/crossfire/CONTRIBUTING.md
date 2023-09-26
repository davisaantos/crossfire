# Contributing guide

## Requirements

* Python 3.9 or newer
* [Poetry](https://python-poetry.org/)
* Optional, but recommended, environment variables [`FOGOCRUZADO_EMAIL` and `FOGOCRUZADO_PASSWORD`](https://api.fogocruzado.org.br/sign-up)

## Installing dependencies

```console
$ poetry install
```

## Test, linter and formatting

To ensure everyone uses same code style, run [Black](https://black.readthedocs.io/en/stable/index.html), [`isort`](https://pycqa.github.io/isort/), [Ruff](https://beta.ruff.rs/docs/) and tests before sending your code contributions:

```console
$ poetry run pytest
```
